!pip install ultralytics sahi networkx matplotlib

import os
import math
import torch
import networkx as nx
import matplotlib.pyplot as plt
from sahi.predict import get_sliced_prediction
from sahi import AutoDetectionModel

MODEL_PATH = '/kaggle/working/runs/detect/dota_experiment_aabb11_1024/weights/best.pt'
WORK_DIR = '/kaggle/working/'
DATA_ROOT = '/kaggle/input/dota15c/dota.yaml' 
DATA_SPLITS = {
    'train': os.path.join(DATA_ROOT, '/kaggle/working/yolo/images/train') 
}
CONF_THRESH = 0.3
SLICE_H, SLICE_W = 1024, 1024
OVER_H, OVER_W = 0.2, 0.2

ALLOWED_LOCATED_ON = {('large_vehicle', 'Bridge')}
ALLOWED_LOCATED_NEAR = { ('ship', 'harbor'), ('small_vehicle', 'small_vehicle'), ('helicopter', 'plane'), ('small_vehicle', 'roundabout'), ('roundabout', 'small_vehicle'), ('storage_tank', 'harbor'), ('small_vehicle', 'tennis_court'), ('small_vehicle', 'basketball_court'), ('small_vehicle', 'soccer_ball_field'), ('small_vehicle', 'Ground_Track_Field'), ('small_vehicle', 'baseball_diamond'), }
ALLOWED_ADJACENT_TO = { ('tennis_court', 'basketball_court'), ('baseball_diamond', 'soccer_ball_field'), ('swimming_pool', 'Ground_Track_Field'), ('large_vehicle', 'small_vehicle'), ('plane', 'plane'), }

KG_DIR = os.path.join(WORK_DIR, 'knowledge_graph')
FACTS_PATH = os.path.join(KG_DIR, 'facts.pl')
GRAPH_IMG_PATH = os.path.join(KG_DIR, 'knowledge_graph_visuals.png')
os.makedirs(KG_DIR, exist_ok=True)

def get_center(bbox):
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def get_distance(bbox_a, bbox_b):
    center_a, center_b = get_center(bbox_a), get_center(bbox_b)
    return math.hypot(center_a[0] - center_b[0], center_a[1] - center_b[1])

def get_bbox_area(bbox):
    x1, y1, x2, y2 = bbox
    return max(0, x2 - x1) * max(0, y2 - y1)

def get_intersection_area(bbox_a, bbox_b):
    x1a, y1a, x2a, y2a = bbox_a
    x1b, y1b, x2b, y2b = bbox_b
    ix1, iy1 = max(x1a, x1b), max(y1a, y1b)
    ix2, iy2 = min(x2a, x2b), min(y2a, y2b)
    return max(0, ix2 - ix1) * max(0, iy2 - iy1)

def get_bbox_diag(bbox):
    x1, y1, x2, y2 = bbox
    return math.hypot(x2 - x1, y2 - y1)

# --- MODEL LOADING ---
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")
try:
    detection_model = AutoDetectionModel.from_pretrained(model_type='yolov8', model_path=MODEL_PATH, confidence_threshold=CONF_THRESH, device=device)
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

# --- KG BUILDING ---
G = nx.DiGraph()
relation_counts = {}
def add_relation(rel, obj_a_class, obj_b_class):
    key = (rel, obj_a_class, obj_b_class)
    relation_counts[key] = relation_counts.get(key, 0) + 1

print("Starting fact extraction...")
for split, img_dir in DATA_SPLITS.items():
    if not os.path.isdir(img_dir):
        print(f"Warning: Directory not found for split '{split}': {img_dir}")
        continue
    print(f"Processing split: {split}")
    image_files = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    for i, img_name in enumerate(image_files):
        path = os.path.join(img_dir, img_name)
        print(f"  Processing image {i+1}/{len(image_files)}: {img_name}", end='\r')
        try:
            result = get_sliced_prediction(path, detection_model, slice_height=SLICE_H, slice_width=SLICE_W, overlap_height_ratio=OVER_H, overlap_width_ratio=OVER_W, verbose=0)
            objects = [(o.category.name, o.score.value, o.bbox.to_voc_bbox()) for o in result.object_prediction_list]
            
            for i in range(len(objects)):
                c1, _, b1 = objects[i]
                for j in range(i + 1, len(objects)):
                    c2, _, b2 = objects[j]
                    sorted_pair = tuple(sorted((c1, c2)))
                    add_relation('cooccurs', sorted_pair[0], sorted_pair[1])
                    
                    for subject, object_, sub_bbox, obj_bbox in [(c1, c2, b1, b2), (c2, c1, b2, b1)]:
                        pair = (subject, object_)
                        
                        if pair in ALLOWED_LOCATED_ON and get_intersection_area(sub_bbox, obj_bbox) / get_bbox_area(sub_bbox) >= 0.5:
                            add_relation('located_on', subject, object_)
                        
                        if pair in ALLOWED_LOCATED_NEAR and get_distance(sub_bbox, obj_bbox) < 2 * ((get_bbox_diag(sub_bbox) + get_bbox_diag(obj_bbox)) / 2):
                            add_relation('located_near', subject, object_)
                        
                        if pair in ALLOWED_ADJACENT_TO:
                            eps = 0.1 * get_bbox_diag(sub_bbox)
                            x1a, y1a, x2a, y2a = sub_bbox
                            x1b, y1b, x2b, y2b = obj_bbox
                            if (abs(x2a - x1b) <= eps or abs(x1a - x2b) <= eps or abs(y2a - y1b) <= eps or abs(y1a - y2b) <= eps):
                                add_relation('adjacent_to', subject, object_)

        except Exception as e:
            print(f"\nError processing image {img_name}: {e}")

print("\nFact extraction complete.")
for (rel, A, B), count in relation_counts.items():
    G.add_edge(A, B, relation=rel, weight=count)

with open(FACTS_PATH, 'w') as f:
    f.write('% fact(Relation, Subject, Object, Count).\n')
    for (rel, A, B), count in sorted(relation_counts.items(), key=lambda item: item[0]):
        f.write(f"fact('{rel}', '{A}', '{B}', {count}).\n")
print(f"Prolog facts written to: {FACTS_PATH}")

relation_types = ['cooccurs', 'located_near', 'adjacent_to', 'located_on']
relation_colors = {'cooccurs': '#d62728', 'located_near': '#2ca02c', 'adjacent_to': '#1f77b4', 'located_on': '#9467bd'}

VISUALIZATION_THRESHOLDS = {
    'cooccurs': 12000,
    'located_near': 20,
    'adjacent_to': 75,
    'located_on': 0
}

fig, axes = plt.subplots(len(relation_types), 1, figsize=(25, 20 * len(relation_types)))
if len(relation_types) == 1: axes = [axes]
print("Generating KG visualizations...")

for ax, rel_type in zip(axes, relation_types):
    min_weight = VISUALIZATION_THRESHOLDS.get(rel_type, 0)
    subG = nx.DiGraph([(u, v, d) for u, v, d in G.edges(data=True) if d.get("relation") == rel_type and d.get("weight", 0) > min_weight])
    
    ax.set_title(f"Relation: {rel_type.replace('_', ' ').title()} (Count > {min_weight:,})", fontsize=24, fontweight='bold')
    if not subG.nodes():
        ax.text(0.5, 0.5, 'No relations found for this threshold', ha='center', va='center', fontsize=18)
        ax.axis("off")
        continue

    pos = nx.spring_layout(subG, k=6.0 / math.sqrt(len(subG.nodes()) + 0.01), seed=42, iterations=100)
    node_sizes = [dict(subG.degree()).get(n, 1) * 1500 + 800 for n in subG.nodes()]
    
    edge_weights = [d['weight'] for _, _, d in subG.edges(data=True)]
    max_weight = max(edge_weights) if edge_weights else 1
    edge_widths = [((w / max_weight) * 8) + 1.5 for w in edge_weights]

    nx.draw_networkx_nodes(subG, pos, node_color="#a0cbe2", node_size=node_sizes, ax=ax, edgecolors='black')
    nx.draw_networkx_labels(subG, pos, font_size=12, font_weight="bold", ax=ax)
    nx.draw_networkx_edges(subG, pos, edge_color=relation_colors[rel_type], width=edge_widths, arrows=True, arrowstyle='->', arrowsize=25, ax=ax, node_size=node_sizes, connectionstyle='arc3,rad=0.1')
    nx.draw_networkx_edge_labels(subG, pos, edge_labels={(u, v): f"{d['weight']:,}" for u, v, d in subG.edges(data=True)}, font_size=11, font_color='black', ax=ax)
    ax.axis("off")

plt.tight_layout(pad=5.0)
plt.savefig(GRAPH_IMG_PATH, dpi=300, bbox_inches='tight')
print(f"KG visualizations saved to: {GRAPH_IMG_PATH}")