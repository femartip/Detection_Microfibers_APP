import torch 
import torchvision
import numpy as np
import cv2
from skimage.morphology import skeletonize
import time

TRESHOLD = 0.5

def convert_hsl_to_names(rgb_tuple):
    colors = {"red":[0,100,50], "green":[147,50,47], "yellow":[39,100,50], "blue":[240,100,50], "pink":[300,76,72]}
    distances = []
    for color in colors:
        distances.append(np.sqrt((colors[color][0]-rgb_tuple[0])**2 + (colors[color][1]-rgb_tuple[1])**2 + (colors[color][2]-rgb_tuple[2])**2))
    color_label = list(colors.keys())[np.argmin(distances)]
    return color_label

def extract_color(img, mask):
    image_hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    roi = cv2.bitwise_and(image_hls, image_hls, mask=mask)
    non_black_pixels_mask = np.any(roi != [0, 0, 0], axis=-1)
    average_color_per_row = np.average(roi[non_black_pixels_mask], axis=0)
    average_color_hsl = [int((average_color_per_row[0]/179)*360), int((average_color_per_row[2]/255)*100), int((average_color_per_row[1]/255)*100)]
    color_label = convert_hsl_to_names(average_color_hsl)
    return color_label

def ppx_to_nm(distance, scale, width, model_type):
    if model_type == "Filtro de Vidrio":
        if scale == 750:
            mm_per_px = 750/155
        
    

def mask_size(mask):
    skel = skeletonize(mask/255)
    skeleton = skel.astype(np.uint8)*255
    points = np.argwhere(skeleton==255)
    distance = len(points)
    return skeleton, distance

def buld_mask(masks, boxes):
    image_mask = np.zeros((IMAGE_SIZE[1],IMAGE_SIZE[0]), dtype=np.uint8)
    for i,mask in enumerate(masks):
        image_mask[int(boxes[i][1]):int(boxes[i][3]), int(boxes[i][0]):int(boxes[i][2])] = mask
    image_mask = cv2.cvtColor(image_mask, cv2.COLOR_GRAY2BGR)
    return image_mask

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

# Functions that handles the detection, this function is called from the main.py file
def process_image(path, model_type, scale):
    global MODEL
    global IMAGE_SIZE

    if model_type == "Filtro de Vidrio":
        MODEL = "models/glass_model.ts"
        IMAGE_SIZE = (1000, 750)
    elif model_type == "Filtro de CA":
        MODEL = "models/ca_model.ts"
        IMAGE_SIZE = (1280, 720)
    else:
        print("Modelo no encontrado")
        return None, None, None, None, None
    
    data_orig = cv2.imread(path)
    data = preprocess_image(data_orig)
    bbox, masks, scores = inference(data)
    
    if len(bbox) == 0:
        return data, None, scores, None, None
    bbox, masks = merge_boxes_and_masks(bbox, masks)
    
    colors = []
    sizes = []
    empty_mask = np.zeros((IMAGE_SIZE[1],IMAGE_SIZE[0]), dtype=np.uint8)
    for i in range(len(bbox)):
        masks[i] = fit_mask(masks[i], bbox[i])
        skel, ms = mask_size(masks[i])
        roi = empty_mask.copy()
        
        roi[int(bbox[i][1]):int(bbox[i][3]), int(bbox[i][0]):int(bbox[i][2])] = skel
        color = extract_color(data, roi)
        colors.append(color)
        sizes.append(ms)
        cv2.rectangle(data, (int(bbox[i][0]), int(bbox[i][1])), (int(bbox[i][2]), int(bbox[i][3])), (0, 255, 0), 2)
        cv2.putText(data, str(scores[i]), (int(bbox[i][0]), int(bbox[i][1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    
    mask = buld_mask(masks,bbox)

    return data, mask, scores, sizes, colors