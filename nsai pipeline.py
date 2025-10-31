# stage1_preprocess.py

import os
import torch
import torchvision
from collections import defaultdict


RAW_PREDICTIONS_DIR = '/kaggle/working/predictions1'
NMS_PREDICTIONS_DIR = '/kaggle/working/predictions_nms'
NMS_IOU_THRESHOLD = 0.6 

def parse_predictions_for_nms(predictions_dir):
    predictions = defaultdict(list)
    for pred_file in os.listdir(predictions_dir):
        if not pred_file.endswith('.txt'): continue
        image_name = pred_file.replace('.txt', '.png')
        with open(os.path.join(predictions_dir, pred_file), 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 6: continue
                category_id, cx, cy, w, h, conf = map(float, parts)
                predictions[image_name].append({
                    'category_id': int(category_id),
                    'bbox_yolo': [cx, cy, w, h], 
                    'bbox_voc': [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                    'confidence': conf
                })
    return predictions

def pre_filter_with_nms(objects_in_image, iou_threshold):
    if not objects_in_image: return []
    objects_by_class = defaultdict(list)
    for obj in objects_in_image:
        objects_by_class[obj['category_id']].append(obj)
    
    filtered_objects = []
    for cat_id, objects in objects_by_class.items():
        if len(objects) < 2:
            filtered_objects.extend(objects)
            continue
        boxes = torch.tensor([obj['bbox_voc'] for obj in objects], dtype=torch.float32)
        scores = torch.tensor([obj['confidence'] for obj in objects], dtype=torch.float32)
        keep_indices = torchvision.ops.nms(boxes, scores, iou_threshold)
        for i in keep_indices:
            filtered_objects.append(objects[i])
    return filtered_objects

def save_predictions_to_file(predictions_dict, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for image_name, objects in predictions_dict.items():
        txt_file_name = image_name.replace('.png', '.txt')
        with open(os.path.join(output_dir, txt_file_name), 'w') as f:
            for obj in objects:
                cat_id = obj['category_id']
                conf = obj['confidence']
                cx, cy, w, h = obj['bbox_yolo']
                f.write(f"{cat_id} {cx} {cy} {w} {h} {conf}\n")

# --- Main Execution Block ---
if __name__ == '__main__':
    print("--- Stage 1: Pre-processing with NMS ---")
    
    raw_predictions = parse_predictions_for_nms(RAW_PREDICTIONS_DIR)
    print(f"Loaded {len(raw_predictions)} raw prediction files.")

    nms_predictions = defaultdict(list)
    total_before = 0
    total_after = 0
    for image_name, objects in raw_predictions.items():
        total_before += len(objects)
        filtered = pre_filter_with_nms(objects, NMS_IOU_THRESHOLD)
        total_after += len(filtered)
        if filtered:
            nms_predictions[image_name] = filtered

    print(f"NMS completed. Reduced detections from {total_before} to {total_after}.")

    save_predictions_to_file(nms_predictions, NMS_PREDICTIONS_DIR)
    print(f"Cleaned predictions saved to '{NMS_PREDICTIONS_DIR}'")



# Symbolic reasoning and explainability report

!sudo apt-get update && sudo apt-get install -y swi-prolog
!pip install pyswip

import os
import csv
import math
from pyswip import Prolog
from collections import defaultdict

NMS_PREDICTIONS_DIR = '/kaggle/working/predictions_nms'
REFINED_PREDICTIONS_DIR = '/kaggle/working/predictions_refined'
RULES_FILE = '/kaggle/working/rules.pl' 
REPORT_FILE = '/kaggle/working/explainability_report1.csv'


def get_center(bbox):
    return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)

def get_distance(bbox_a, bbox_b):
    center_a, center_b = get_center(bbox_a), get_center(bbox_b)
    return math.hypot(center_a[0] - center_b[0], center_a[1] - center_b[1])

def get_bbox_area(bbox):
    return max(0, bbox[2] - bbox[0]) * max(0, bbox[3] - bbox[1])

def get_intersection_area(bbox_a, bbox_b):
    ix1, iy1 = max(bbox_a[0], bbox_b[0]), max(bbox_a[1], bbox_b[1])
    ix2, iy2 = min(bbox_a[2], bbox_b[2]), min(bbox_a[3], bbox_b[3])
    return max(0, ix2 - ix1) * max(0, iy2 - iy1)

def get_bbox_diag(bbox):
    return math.hypot(bbox[2] - bbox[0], bbox[3] - bbox[1])

def parse_predictions(predictions_dir):
    predictions = defaultdict(list)
    if not os.path.isdir(predictions_dir): return predictions
    for pred_file in os.listdir(predictions_dir):
        if not pred_file.endswith('.txt'): continue
        image_name = pred_file.replace('.txt', '.png')
        with open(os.path.join(predictions_dir, pred_file), 'r') as f:
            for i, line in enumerate(f):
                parts = line.strip().split()
                if len(parts) != 6: continue
                category_id, center_x, center_y, width, height, confidence = map(float, parts)
                x_min, y_min = center_x - width / 2, center_y - height / 2
                x_max, y_max = center_x + width / 2, center_y + height / 2
                predictions[image_name].append({
                    'id': f'det_{i}', 'category_id': int(category_id),
                    'bbox': [x_min, y_min, x_max, y_max],
                    'bbox_yolo': [center_x, center_y, width, height],
                    'confidence': confidence
                })
    return predictions

def load_prolog_modifiers(prolog_engine):
    modifier_map = {}
    query = "confidence_modifier(A, B, Weight)"
    for solution in prolog_engine.query(query):
        key = (solution['A'], solution['B'])
        modifier_map[key] = solution['Weight']
    return modifier_map

def apply_symbolic_modifiers(objects_in_image, modifier_map, class_map):
    modified_objects = {obj['id']: obj.copy() for obj in objects_in_image}
    change_log = [] 

    obj_ids = list(modified_objects.keys())

    for i in range(len(obj_ids)):
        for j in range(i + 1, len(obj_ids)):
            id_a, id_b = obj_ids[i], obj_ids[j]
            if id_a not in modified_objects or id_b not in modified_objects: continue

            obj_a, obj_b = modified_objects[id_a], modified_objects[id_b]
            class_a, class_b = class_map[obj_a['category_id']], class_map[obj_b['category_id']]
            weight = modifier_map.get((class_a, class_b)) or modifier_map.get((class_b, class_a))

            if weight is None: continue

            log_entry = None
            if weight > 1.0: 
                avg_diag = (get_bbox_diag(obj_a['bbox']) + get_bbox_diag(obj_b['bbox'])) / 2
                if get_distance(obj_a['bbox'], obj_b['bbox']) < 2 * avg_diag:
                    original_conf_a, original_conf_b = obj_a['confidence'], obj_b['confidence']
                    obj_a['confidence'] = min(1.0, original_conf_a * weight)
                    obj_b['confidence'] = min(1.0, original_conf_b * weight)
                    log_entry = {'action': 'BOOST', 'rule_pair': f"{class_a}<->{class_b}", 'object_1': class_a, 'conf_1_before': f"{original_conf_a:.2f}", 'conf_1_after': f"{obj_a['confidence']:.2f}", 'object_2': class_b, 'conf_2_before': f"{original_conf_b:.2f}", 'conf_2_after': f"{obj_b['confidence']:.2f}"}

            elif weight < 1.0: 
                intersection = get_intersection_area(obj_a['bbox'], obj_b['bbox'])
                min_area = min(get_bbox_area(obj_a['bbox']), get_bbox_area(obj_b['bbox']))
                if min_area > 0 and intersection / min_area > 0.5:
                    suppressed_obj, kept_obj = (obj_b, obj_a) if obj_a['confidence'] > obj_b['confidence'] else (obj_a, obj_b)
                    original_conf = suppressed_obj['confidence']
                    suppressed_obj['confidence'] *= weight
                    log_entry = {'action': 'PENALTY', 'rule_pair': f"{class_a}<->{class_b}", 'suppressed_object': class_map[suppressed_obj['category_id']], 'conf_before': f"{original_conf:.2f}", 'conf_after': f"{suppressed_obj['confidence']:.2f}", 'kept_object': class_map[kept_obj['category_id']], 'kept_object_conf': f"{kept_obj['confidence']:.2f}"}

            if log_entry:
                change_log.append(log_entry)

    return list(modified_objects.values()), change_log

def save_predictions_to_file(predictions_dict, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for image_name, objects in predictions_dict.items():
        txt_file_name = image_name.replace('.png', '.txt')
        with open(os.path.join(output_dir, txt_file_name), 'w') as f:
            for obj in objects:
                cat_id = obj['category_id']
                conf = obj['confidence']
                cx, cy, w, h = obj['bbox_yolo']
                f.write(f"{cat_id} {cx} {cy} {w} {h} {conf}\n")

if __name__ == '__main__':
    print("--- Stage 2: Symbolic Reasoning (CPU-only) ---")
    CLASS_MAP = {
        0: 'plane', 1: 'ship', 2: 'storage_tank', 3: 'baseball_diamond', 4: 'tennis_court',
        5: 'basketball_court', 6: 'Ground_Track_Field', 7: 'harbor', 8: 'Bridge',
        9: 'large_vehicle', 10: 'small_vehicle', 11: 'helicopter', 12: 'roundabout',
        13: 'soccer_ball_field', 14: 'swimming_pool'
    }

    prolog = Prolog()
    prolog.consult(RULES_FILE)
    modifier_map = load_prolog_modifiers(prolog)
    print(f"Loaded {len(modifier_map)} modifier rules.")

    nms_predictions = parse_predictions(NMS_PREDICTIONS_DIR)
    print(f"Loaded {len(nms_predictions)} NMS-filtered prediction files.")

    refined_predictions = defaultdict(list)
    full_report = []
    for image_name, objects in nms_predictions.items():
        if not objects: continue
        refined_objs, report_entries = apply_symbolic_modifiers(objects, modifier_map, CLASS_MAP)
        if refined_objs:
            refined_predictions[image_name] = refined_objs
        for entry in report_entries:
            entry['image_name'] = image_name 
            full_report.append(entry)

    save_predictions_to_file(refined_predictions, REFINED_PREDICTIONS_DIR)
    print(f"Final refined predictions saved to '{REFINED_PREDICTIONS_DIR}'")

    if full_report:
        fieldnames = ['image_name', 'action', 'rule_pair', 'object_1', 'conf_1_before', 'conf_1_after', 'object_2', 'conf_2_before', 'conf_2_after']
        with open(REPORT_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(full_report)
        print(f"Explainability report saved to '{REPORT_FILE}'")
    else:
        print("No symbolic reasoning actions were logged; explainability report not generated.")



!pip install torchmetrics -q
!pip install torchmetrics detection -q
!pip install faster-coco-eval -q
!pip install pycocotools -q
import os
import torch
from torchmetrics.detection.mean_ap import MeanAveragePrecision
from collections import defaultdict

# --- Configuration ---
RAW_PREDICTIONS_DIR = '/kaggle/working/predictions1'
NMS_PREDICTIONS_DIR = '/kaggle/working/predictions_nms'
REFINED_PREDICTIONS_DIR = '/kaggle/working/predictions_refined'
GROUND_TRUTH_DIR = '/kaggle/working/yolo/labels/val' 


def parse_predictions(predictions_dir):
    """Parses a directory of YOLO-format prediction files."""
    predictions = defaultdict(list)
    if not os.path.isdir(predictions_dir):
        print(f"Warning: Prediction directory not found at {predictions_dir}")
        return predictions

    for pred_file in os.listdir(predictions_dir):
        if not pred_file.endswith('.txt'):
            continue

        image_name = pred_file.replace('.txt', '.png')

        with open(os.path.join(predictions_dir, pred_file), 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 6: continue 

                category_id = int(parts[0])
                center_x, center_y, width, height, confidence = map(float, parts[1:])

              
                x_min = center_x - width / 2
                y_min = center_y - height / 2
                x_max = center_x + width / 2
                y_max = center_y + height / 2

                predictions[image_name].append({
                    'category_id': category_id,
                    'bbox': [x_min, y_min, x_max, y_max],
                    'confidence': confidence
                })
    return predictions

def parse_ground_truths(label_dir):
    """Parses a directory of YOLO-format ground truth label files."""
    ground_truths = defaultdict(list)
    if not os.path.isdir(label_dir):
        print(f"Warning: Ground truth directory not found at {label_dir}")
        return ground_truths

    for label_file in os.listdir(label_dir):
        if not label_file.endswith('.txt'):
            continue

        image_name = label_file.replace('.txt', '.png') 
        with open(os.path.join(label_dir, label_file), 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 5: continue

                category_id = int(parts[0])
                center_x, center_y, width, height = map(float, parts[1:])

                # Convert to VOC format
                x_min = center_x - width / 2
                y_min = center_y - height / 2
                x_max = center_x + width / 2
                y_max = center_y + height / 2

                ground_truths[image_name].append({
                    'category_id': category_id,
                    'bbox': [x_min, y_min, x_max, y_max]
                })
    return ground_truths

def calculate_map(predictions, ground_truths):
    """Calculates mAP using torchmetrics."""
    metric = MeanAveragePrecision(box_format='xyxy')

    preds_for_metric = []
    targets_for_metric = []

    for image_name in ground_truths.keys():
       
        if image_name in predictions:
            preds_for_metric.append({
                'boxes': torch.tensor([p['bbox'] for p in predictions[image_name]], dtype=torch.float32),
                'scores': torch.tensor([p['confidence'] for p in predictions[image_name]], dtype=torch.float32),
                'labels': torch.tensor([p['category_id'] for p in predictions[image_name]], dtype=torch.int32),
            })
        else: 
             preds_for_metric.append({
                'boxes': torch.empty(0, 4, dtype=torch.float32),
                'scores': torch.empty(0, dtype=torch.float32),
                'labels': torch.empty(0, dtype=torch.int32),
            })

        targets_for_metric.append({
            'boxes': torch.tensor([gt['bbox'] for gt in ground_truths[image_name]], dtype=torch.float32),
            'labels': torch.tensor([gt['category_id'] for gt in ground_truths[image_name]], dtype=torch.int32),
        })

    metric.update(preds_for_metric, targets_for_metric)
    return metric.compute()

if __name__ == '__main__':
    print("--- Stage 3: Final Evaluation ---")

    print("Loading ground truths")
    ground_truths = parse_ground_truths(GROUND_TRUTH_DIR)
    print(f"Loaded {len(ground_truths)} ground truth files.")

    print("Loading raw YOLO predictions")
    raw_preds = parse_predictions(RAW_PREDICTIONS_DIR)
    print(f"Loaded {len(raw_preds)} raw prediction files.")

    print("Loading NMS-filtered predictions")
    nms_preds = parse_predictions(NMS_PREDICTIONS_DIR)
    print(f"Loaded {len(nms_preds)} NMS-filtered prediction files.")

    print("Loading final refined predictions")
    refined_preds = parse_predictions(REFINED_PREDICTIONS_DIR)
    print(f"Loaded {len(refined_preds)} refined prediction files.")

    
    print("\n--- Calculating mAP for Raw YOLO Detections ---")
    map_raw = calculate_map(raw_preds, ground_truths)

    print("\n--- Calculating mAP for NMS-Filtered Detections ---")
    map_nms = calculate_map(nms_preds, ground_truths)

    print("\n--- Calculating mAP for Final Symbolic-Refined Detections ---")
    map_refined = calculate_map(refined_preds, ground_truths)

    print("\n\n--- 🏆 FINAL RESULTS COMPARISON ---")
    print("Metric          | Raw YOLO | NMS Only | Symbolic Refined")
    print("----------------|----------|----------|-----------------")

    map50_raw = map_raw.get('map_50', torch.tensor(-1.0)).item()
    map50_nms = map_nms.get('map_50', torch.tensor(-1.0)).item()
    map50_refined = map_refined.get('map_50', torch.tensor(-1.0)).item()
    print(f"mAP@.50         | {map50_raw:.4f}   | {map50_nms:.4f}   | {map50_refined:.4f}")

    map_raw_val = map_raw.get('map', torch.tensor(-1.0)).item()
    map_nms_val = map_nms.get('map', torch.tensor(-1.0)).item()
    map_refined_val = map_refined.get('map', torch.tensor(-1.0)).item()
    print(f"mAP@.50:.95     | {map_raw_val:.4f}   | {map_nms_val:.4f}   | {map_refined_val:.4f}")
    print("==================================================")