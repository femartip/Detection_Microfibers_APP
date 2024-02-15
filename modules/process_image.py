import torch 
import torchvision
import numpy as np
import cv2

TRESHOLD = 0.5

# Function that merges the boxes and masks that intersect. This is done to avoid multiple detections of the same object
def merge_boxes_and_masks(pred_boxes, pred_masks):
    sorted_indices = sorted(range(len(pred_boxes)), key=lambda i: pred_boxes[i][0])
    pred_boxes = [pred_boxes[i] for i in sorted_indices]
    pred_masks = [pred_masks[i] for i in sorted_indices]

    # Initialize the list of merged boxes and masks
    merged_boxes = [pred_boxes[0]]
    merged_masks = [pred_masks[0]]

    for current_box, current_mask in zip(pred_boxes[1:], pred_masks[1:]):
        # Get the last box and mask in the merged_boxes and merged_masks lists
        last_box = merged_boxes[-1]
        last_mask = merged_masks[-1]

        # If the current box intersects with the last box, merge them
        if not (last_box[2] < current_box[0] or last_box[3] < current_box[1]):
            merged_box = (min(last_box[0], current_box[0]), min(last_box[1], current_box[1]), max(last_box[2], current_box[2]), max(last_box[3], current_box[3]))
            merged_mask = np.logical_or(last_mask, current_mask)

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
    model = torch.jit.load("./models/model.ts", map_location="cpu")
    model.eval()
    input_data = torch.tensor(data).permute(2, 0, 1).float()
    output = model(input_data)
    filtered_output = apply_treshold(output)
    bbox = filtered_output[0].detach().numpy()
    masks = filtered_output[2].detach().numpy()
    scores = filtered_output[3].detach().numpy()
    return bbox, masks, scores

# Resize the image to the input size of the model
def preprocess_image(data):
    data = cv2.resize(data, (1000, 750))
    return data

# Functions that handles the detection, this function is called from the main.py file
def process_image(path):
    data_orig = cv2.imread(path)
    data = preprocess_image(data_orig)
    bbox, masks, scores = inference(data)
    if len(bbox) == 0:
        return data, scores
    bbox, masks = merge_boxes_and_masks(bbox, masks)
    for i in range(len(bbox)):
        cv2.rectangle(data, (int(bbox[i][0]), int(bbox[i][1])), (int(bbox[i][2]), int(bbox[i][3])), (0, 255, 0), 2)
        cv2.putText(data, str(scores[i]), (int(bbox[i][0]), int(bbox[i][1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    return data, scores