!pip install ultralytics 
import os
import cv2
import torch
import numpy as np
import subprocess
import json
from ultralytics import YOLO
from PIL import Image
from tqdm import tqdm
import matplotlib.pyplot as plt


DATA_YAML = '/kaggle/input/dota15c/dota.yaml'
TRAINED_MODEL_NAME = 'dota_experiment_v11_1024'
TEST_IMAGE_DIR = '/kaggle/working/yolo/images/test'
VISUALIZATION_DIR = '/kaggle/working/yolo/viz_results'
MODEL_WEIGHTS_DIR = '/kaggle/working/runs/obb/dota_experiment_v11_1024/weights'
IMGSZ = 1024
CONF_THRESH = 0.3

os.makedirs(VISUALIZATION_DIR, exist_ok=True)

def train_yolov11_obb():
    model = YOLO("yolo11n-obb.pt") 
    model.train(
        data=DATA_YAML,
        epochs=50,
        imgsz=1024,
        batch=8,
        workers=0,
        name=TRAINED_MODEL_NAME,
        save=True,
        save_txt=True
    )
    return model

def run_inference(model_path, test_dir, output_dir, imgsz=1024, conf_thres=0.3):
    model = YOLO(model_path)
    all_predictions = {}

    for img_name in tqdm(os.listdir(test_dir)):
        if not img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        img_path = os.path.join(test_dir, img_name)
        results = model(img_path, imgsz=imgsz, conf=conf_thres)[0]

        predictions = []
        result_image = cv2.imread(img_path)

        if results and results.boxes:
            for box in results.boxes:
                xyxy = box.xyxy[0].cpu().numpy().tolist()
                conf = float(box.conf[0].item())
                cls_id = int(box.cls[0].item())
                label = model.names[cls_id]

                predictions.append({
                    'class': label,
                    'confidence': round(conf, 4),
                    'bbox': [round(x, 2) for x in xyxy]
                })

                x1, y1, x2, y2 = map(int, xyxy)
                cv2.rectangle(result_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(result_image, f"{label} {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        out_path = os.path.join(output_dir, img_name)
        cv2.imwrite(out_path, result_image)

        all_predictions[img_name] = predictions

    json_path = os.path.join(output_dir, "yolo_predictions.json")
    with open(json_path, "w") as f:
        json.dump(all_predictions, f, indent=2)

    print(f"📄 JSON predictions saved to: {json_path}")
    return json_path

def package_results():
    zip_path = "/kaggle/working/yolo/final_results.zip"
    subprocess.run(["zip", "-r", zip_path, "/kaggle/working/yolo"], check=False)
    return zip_path

if __name__ == "__main__":
    print("Starting YOLOv11-OBB Training...")
    trained_model = train_yolov11_obb()

    best_model_path = trained_model.trainer.best if hasattr(trained_model.trainer, 'best') else os.path.join(MODEL_WEIGHTS_DIR, 'best.pt')

    print("Running Inference on Test Images...")
    json_output = run_inference(
        model_path=best_model_path,
        test_dir=TEST_IMAGE_DIR,
        output_dir=VISUALIZATION_DIR,
        imgsz=IMGSZ,
        conf_thres=CONF_THRESH
    )

    print(" Zipping Results for Download...")
    zip_result_path = package_results()

    print(f"Visual results saved to: {VISUALIZATION_DIR}")
    print(f"JSON file saved to: {json_output}")
    print(f"Download zipped results from: {zip_result_path}")
