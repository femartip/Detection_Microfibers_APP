import torch 
import torchvision
import numpy as np
import cv2
from skimage.morphology import skeletonize
from sklearn.cluster import KMeans
import webcolors
import time

# Global variables
TRESHOLD = 0.5  # Treshold for the model at inference time

# COLOR EXTRACTION
############################################################################################
# Function that gets the closest primary color to the given hls color 
# does not work so well
def convert_hsl_to_names(hls_tuple):
    colors = {"red":[0,100,50], "green":[147,50,47], "yellow":[39,100,50], "blue":[240,100,50], "pink":[300,76,72]}
    distances = []
    for color in colors:
        distances.append(np.sqrt((colors[color][0]-hls_tuple[0])**2 + (colors[color][1]-hls_tuple[1])**2 + (colors[color][2]-hls_tuple[2])**2))
    color_label = list(colors.keys())[np.argmin(distances)]
    return color_label

# Function that extracts the color of the object in the image by 
# extracting the region of interest and calculating the average color
# of the region in the HSL color space
def extract_color(img, mask):
    image_hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    roi = cv2.bitwise_and(image_hls, image_hls, mask=mask)
    non_black_pixels_mask = np.any(roi != [0, 0, 0], axis=-1)
    average_color_per_row = np.average(roi[non_black_pixels_mask], axis=0)
    average_color_hsl = [int((average_color_per_row[0]/179)*360), int((average_color_per_row[2]/255)*100), int((average_color_per_row[1]/255)*100)]
    color_label = convert_hsl_to_names(average_color_hsl)   #convert to color name by getting the minimum distance to a primary color
    return color_label

# Function that gets the closest color name to the given rgb color
# by calculating the euclidean distance between the rgb color and the
# colors in the CSS3_HEX_TO_NAMES dictionary
# Solves the error on the webcolors.rgb_to_name function
def closest_colour(requested_colour):
    min_colours = {}
    primary_colors_dict = webcolors.CSS3_HEX_TO_NAMES
    #primary_colors_dict = {"#FF0000":"red", "#00FF00":"green", "#FFFF00":"yellow", "#0000FF":"blue", "#6600FF":"purple", "#FF6600":"orange", "#000000":"black", "#FFFFFF":"white"}
    for key, name in primary_colors_dict.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

# Function that extracts the color of the object in the image by
# extracting the region of interest and applying kmeans clustering
# to the region to get the primary color
def extract_color_kmeans(img, mask):
    roi = cv2.bitwise_and(img, img, mask=mask)
    non_black_pixels_mask = np.any(roi != [0, 0, 0], axis=-1)
    kmeans_color = KMeans(n_clusters=3).fit(roi[non_black_pixels_mask].reshape(-1, 3))
    primary_color = kmeans_color.cluster_centers_[0]
    rgb_primary_color = (int(primary_color[2]), int(primary_color[1]), int(primary_color[0]))
    #print("Primary rgb color: ", rgb_primary_color)
    #try:
    #    primary_color_label = webcolors.rgb_to_name(rgb_primary_color, spec='css3')
    #except ValueError:
    primary_color_label = closest_colour(rgb_primary_color)
    print("Primary kmeans color: ", primary_color_label)
    return primary_color_label
    
# GET MASK SIZE
############################################################################################
"""
def scale_to_ppx(data, scale):
    #extract positions of the image where the bgr values are 0, assuming scale bar is black
    black_pixels_bool = np.all(data == [0, 0, 0], axis=-1).astype(np.uint8)
    #crop the image to the region where the bgr values are not 0
    cropped_data = data[np.ix_(black_pixels_bool.any(1),black_pixels_bool.any(0))]
    #cv2.imshow("Cropped", cropped_data)
    #length of the cropped image in pixels, this is the distance in pixels
    ppx = cropped_data.shape[1]
    if ppx == 0:
        #try with white pixel bar 
        white_pixels_bool = np.all(data == [255, 255, 255], axis=-1).astype(np.uint8)
        cropped_data = data[np.ix_(white_pixels_bool.any(1),white_pixels_bool.any(0))]
        ppx = cropped_data.shape[1]
        if ppx == 0:
            return 0
    print(ppx)
    #return the size of a pixel in microm
    return int(scale)/ppx
"""
#Medida de un pixel en microm segun escala
def scale_to_ppx(scale: str, model: str):
    if model == "Glass Filter":
        if scale == "200":
            return 2.05
        if scale == "350":
            return 2.50
        if scale == "500":
            return 4.03
        if scale == "750":
            return 3.9
        if scale == "1000":
            return 6.45
        else:
            return 0
    elif model == "CA Filter":
        if scale == "200":
            return 1.18
        if scale == "350":
            return 2.06
        if scale == "500":
            return 2.92
        if scale == "750":
            return 4.41
        if scale == "1000":
            return 5.88
    else:
        return 0
def mask_size(mask, nm_of_ppx):
    skel = skeletonize(mask/255)
    skeleton = skel.astype(np.uint8)*255
    points = np.argwhere(skeleton==255)
    distance = len(points)
    lenght_microm = distance*nm_of_ppx
    return skeleton, lenght_microm
############################################################################################

# MASKS
############################################################################################
# Function that builds the mask from the masks and bounding boxes
def buld_mask(masks, boxes):
    image_mask = np.zeros((IMAGE_SIZE[1],IMAGE_SIZE[0]), dtype=np.uint8)
    for i,mask in enumerate(masks):
        image_mask[int(boxes[i][1]):int(boxes[i][3]), int(boxes[i][0]):int(boxes[i][2])] = mask
    image_mask = cv2.cvtColor(image_mask, cv2.COLOR_GRAY2BGR)
    return image_mask

# Function that resizes the mask to the size of the bounding box
def fit_mask(mask, box):
    mask = cv2.resize(mask[0], (int(box[2])-int(box[0]), int(box[3])-int(box[1])))
    return mask

# Function that merges the boxes and masks that intersect. This is done to avoid multiple detections of the same object
def merge_boxes_and_masks(pred_boxes, pred_masks):
    sorted_indices = sorted(range(len(pred_boxes)), key=lambda i: pred_boxes[i][0])
    
    pred_boxes = [pred_boxes[i] for i in sorted_indices]
    pred_masks = [pred_masks[i] for i in sorted_indices]

    # Initialize the list of merged boxes and masks
    merged_boxes = []
    merged_masks = []

    merged_boxes.append(pred_boxes[0])
    merged_masks.append(pred_masks[0])

    for current_box, current_mask in zip(pred_boxes[1:], pred_masks[1:]):
        # Get the last box and mask in the merged_boxes and merged_masks lists
        last_box = merged_boxes[-1]
        last_mask = merged_masks[-1]

        # If the current box intersects with the last box, merge them
        if not(last_box[2] < current_box[0] or last_box[3] < current_box[1]):
            merged_box = [min(last_box[0], current_box[0]), min(last_box[1], current_box[1]), max(last_box[2], current_box[2]), max(last_box[3], current_box[3])]
            
            merged_mask = np.logical_or(last_mask, current_mask) #Returns boolean array
            merged_mask = merged_mask.astype(np.uint8) * 255 #Convert to binary mask

            merged_boxes[-1] = merged_box
            merged_masks[-1] = merged_mask
        else:
            # If the current box does not intersect with the last box, add it to the lists
            merged_boxes.append(current_box)
            merged_masks.append(current_mask)

    return merged_boxes, merged_masks
############################################################################################

# INFERENCE
############################################################################################
# Function that applies the treshold to the output of the model, results with a score lower than the treshold are discarded
def apply_treshold(output):
    tresholded_output = []
    for i in range(len(output[3])):
        if output[3][i] > TRESHOLD:
            tresholded_output.append(i)
    return output[0][tresholded_output], output[1][tresholded_output], output[2][tresholded_output], output[3][tresholded_output]

# Function that loads the model and makes the inference on the image. It returns the bounding boxes, masks and scores
def inference(data):
    start_time = time.time()
    try:
        model = torch.jit.load(MODEL, map_location="cpu")
    except UserWarning:
        pass
    model.eval()
    input_data = torch.tensor(data).permute(2, 0, 1).float()
    output = model(input_data)
    print("Model loaded in: {} seconds".format(time.time()-start_time))
    filtered_output = apply_treshold(output)
    bbox = filtered_output[0].detach().numpy()
    masks = (filtered_output[2].detach().numpy() > 0.5).astype(np.uint8) * 255
    scores = filtered_output[3].detach().numpy()
    return bbox, masks, scores

# Resize the image to the input size of the model
def preprocess_image(data):
    data = cv2.resize(data, IMAGE_SIZE)
    return data
############################################################################################

# MAIN FUNCTION
############################################################################################
# Functions that handles the detection, this function is called from the main.py file
def process_image(path, model_type, scale):
    global MODEL
    global IMAGE_SIZE

    start = time.time()

    if model_type == "Glass Filter":
        MODEL = "models/glass_model.ts"
        IMAGE_SIZE = (1000, 750)
    elif model_type == "CA Filter":
        MODEL = "models/ca_model.ts"
        IMAGE_SIZE = (1280, 720)
    else:
        print("Modelo no encontrado")
        return None, None, None, None, None
    
    data_orig = cv2.imread(path)

    data = preprocess_image(data_orig)
    
    nm_of_ppx = scale_to_ppx(scale, model_type)

    bbox, masks, scores = inference(data)
    
    if len(bbox) == 0:
        return data, None, scores, None, None
    bbox, masks = merge_boxes_and_masks(bbox, masks)
    
    colors = []
    sizes = []
    empty_mask = np.zeros((IMAGE_SIZE[1],IMAGE_SIZE[0]), dtype=np.uint8)
    for i in range(len(bbox)):
        masks[i] = fit_mask(masks[i], bbox[i])
        skel, ms = mask_size(masks[i], nm_of_ppx)
        roi = empty_mask.copy()
        
        roi[int(bbox[i][1]):int(bbox[i][3]), int(bbox[i][0]):int(bbox[i][2])] = skel
        #color = extract_color(data, roi)   #previous color extraction method
        color = extract_color_kmeans(data, roi)
        colors.append(color)
        sizes.append(round(ms, 1))
        cv2.rectangle(data, (int(bbox[i][0]), int(bbox[i][1])), (int(bbox[i][2]), int(bbox[i][3])), (0, 255, 0), 2)
        #cv2.putText(data, str(scores[i]), (int(bbox[i][0]), int(bbox[i][1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    
    mask = buld_mask(masks,bbox)

    scores = [round(score, 2) for score in scores]

    print("Image processed in: {} seconds".format(time.time()-start))

    return data, mask, scores, sizes, colors
############################################################################################