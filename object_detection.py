import argparse
import sys
import os
import time
import cv2
import numpy as np
from functools import lru_cache
from picamera2 import MappedArray, Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import (NetworkIntrinsics, postprocess_nanodet_detection)

#Needed for transmitting queue data to ground station
import queue
from shared_resources import ai_data_queue, stop_event

# Create the detected_images directory if it doesn't exist
output_dir = 'detected_images'
os.makedirs(output_dir, exist_ok=True)

# Global variables
last_detections = []
imx500 = None
picam2 = None
last_results = None
intrinsics = None
picam2 = None  # Needed for Detection class

class Detection:
    def __init__(self, coords, category, conf, metadata, imx500_instance, picam2_instance):
        self.category = category
        self.conf = conf
        self.box = imx500_instance.convert_inference_coords(coords, metadata, picam2_instance)

def parse_detections(metadata: dict, imx500):
   
    global last_detections, intrinsics
    bbox_normalization = intrinsics.bbox_normalization
    bbox_order = intrinsics.bbox_order
    threshold = args.threshold
    iou = args.iou
    max_detections = args.max_detections

    # Check the structure of metadata
    print("Metadata:", metadata)  # Debugging line

    # Ensure that metadata is passed correctly
    try:
        np_outputs = imx500.get_outputs(metadata, add_batch=True)  # Adjust if more parameters are needed
    except TypeError as e:
        print(f"Error calling get_outputs: {e}")  # Debugging line
        return last_detections

    input_w, input_h = imx500.get_input_size()

    if np_outputs is None:
        return last_detections

    if intrinsics.postprocess == "nanodet":
        boxes, scores, classes = postprocess_nanodet_detection(outputs=np_outputs[0], conf=threshold, iou_thres=iou,
                                                               max_out_dets=max_detections)[0]
        from picamera2.devices.imx500.postprocess import scale_boxes
        boxes = scale_boxes(boxes, 1, 1, input_h, input_w, False, False)
    else:
        boxes, scores, classes = np_outputs[0][0], np_outputs[1][0], np_outputs[2][0]
        if bbox_normalization:
            boxes = boxes / input_h
        if bbox_order == "xy":
            boxes = boxes[:, [1, 0, 3, 2]]
        boxes = np.array_split(boxes, 4, axis=1)
        boxes = zip(*boxes)

    last_detections = [
        Detection(box, category, score, metadata, imx500, picam2)
        for box, score, category in zip(boxes, scores, classes)
        if score > threshold
    ]
    return last_detections

@lru_cache
def get_labels():
    labels = intrinsics.labels
    if intrinsics.ignore_dash_labels:
        labels = [label for label in labels if label and label != "-"]
    return labels

def draw_detections(request, stream="main"):
    global last_results
    detections = last_results
    if detections is None:
        return
    labels = get_labels()

    with MappedArray(request, stream) as m:
        for detection in detections:
            x, y, w, h = detection.box
            label = f"{labels[int(detection.category)]} ({detection.conf:.2f})"

            # Draw the detection box and label
            cv2.rectangle(m.array, (x, y), (x + w, y + h), (0, 255, 0), thickness=2)
            cv2.putText(m.array, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Print the detected object and its confidence
            detected_msg = f"Detected {labels[int(detection.category)]} with confidence {detection.conf:.2f}"
            print(detected_msg)
            
            # Save the frame if confidence is high
            if detection.conf >= 0.3:
                save_detected_image(m.array, detection.conf, labels[int(detection.category)])

def save_detected_image(frame, confidence, category):
    import re

    sanitized_category = re.sub(r'[^a-zA-Z0-9_.-]', '_', category)
    image_path = os.path.join(output_dir, f'detected_{sanitized_category}_{int(time.time())}_{int(confidence * 100)}.jpg')

    if cv2.imwrite(image_path, frame):
        print(f"Image saved: {image_path}")
    else:
        print(f"Failed to save image: {image_path}")

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str,
                        default="/usr/share/imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk")
    parser.add_argument("--fps", type=int)
    parser.add_argument("--threshold", type=float, default=0.55)
    parser.add_argument("--iou", type=float, default=0.65)
    parser.add_argument("--max-detections", type=int, default=10)
    parser.add_argument("--ignore-dash-labels", action=argparse.BooleanOptionalAction)
    parser.add_argument("--postprocess", choices=["", "nanodet"], default=None)
    parser.add_argument("-r", "--preserve-aspect-ratio", action=argparse.BooleanOptionalAction)
    parser.add_argument("--labels", type=str)
    parser.add_argument("--print-intrinsics", action="store_true")
    return parser.parse_args()

def camera_running(stop_event):
    
    print("[Camera] Starting camera thread...")

    global picam2, last_results, intrinsics, args, imx500

    args = get_args()

    imx500 = IMX500(args.model)
    intrinsics = imx500.network_intrinsics or NetworkIntrinsics()
    intrinsics.task = "object detection"
    intrinsics.update_with_defaults()

    if intrinsics.labels is None:
        with open("assets/coco_labels.txt", "r") as f:
            intrinsics.labels = f.read().splitlines()

    picam2 = Picamera2(imx500.camera_num)
    config = picam2.create_preview_configuration(
    controls={
        "FrameRate": intrinsics.inference_rate,
        # "AwbMode": 1  # Enable auto white balance
    },
    buffer_count=12)

    picam2.start(config)

    try:
        while not stop_event.is_set():
            request = picam2.capture_request()
            metadata = request.get_metadata()

            # Get model outputs
            np_outputs = imx500.get_outputs(metadata, add_batch=True)
            if np_outputs is None:
                print("[Camera] No outputs from model.")
                request.release()
                continue

            input_w, input_h = imx500.get_input_size()

            # Postprocess detections
            if intrinsics.postprocess == "nanodet":
                boxes, scores, classes = postprocess_nanodet_detection(
                    outputs=np_outputs[0], conf=args.threshold, iou_thres=args.iou,
                    max_out_dets=args.max_detections)[0]
                from picamera2.devices.imx500.postprocess import scale_boxes
                boxes = scale_boxes(boxes, 1, 1, input_h, input_w, False, False)
            else:
                boxes, scores, classes = np_outputs[0][0], np_outputs[1][0], np_outputs[2][0]
                if intrinsics.bbox_normalization:
                    boxes = boxes / input_h
                if intrinsics.bbox_order == "xy":
                    boxes = boxes[:, [1, 0, 3, 2]]
                boxes = np.array_split(boxes, 4, axis=1)
                boxes = zip(*boxes)

            detections = []
            for box, score, category in zip(boxes, scores, classes):
                if score > args.threshold:
                    det = Detection(box, category, score, metadata, imx500, picam2)
                    detections.append(det)

            if not detections:
                print("[Camera] No objects detected.")
            else:
                print(f"[Camera] {len(detections)} object(s) detected.")
                   
            # Draw detections and save images
            with MappedArray(request, "main") as m:
                for det in detections:
                    x, y, w, h = det.box
                    label = f"{intrinsics.labels[int(det.category)]} ({det.conf:.2f})"
                    cv2.rectangle(m.array, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(m.array, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    detected_msg = f"Detected {intrinsics.labels[int(det.category)]} with confidence {det.conf:.2f}"
                    print(detected_msg)

                    if det.conf >= 0.3:
                        filename = f"detected_{intrinsics.labels[int(det.category)]}_{int(time.time())}_{int(det.conf*100)}.jpg"
                        filepath = os.path.join(output_dir, filename)
                        cv2.imwrite(filepath, m.array)
                        
                        print(f"Image saved: {filepath}")
                        
                        ai_data_queue.put(filepath)
                        print(f"[DEBUG ODC] Image filename added to queue: {filepath}")            
                        
                        '''
                        filepath_str = str(filepath)
                        ai_data_queue.put(filepath_str)

                        print(f"[DEBUG ODC] ai_data_queue size: {ai_data_queue.qsize()}")
                        '''

            request.release()

            time.sleep(1)  # Wait before next detection

    except Exception as e:
        print(f"[Camera] Exception: {e}")

    finally:
        print("[Camera] Cleaning up...")
        picam2.stop()
        cv2.destroyAllWindows()
