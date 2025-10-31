!pip install ultralytics sahi

import os
import torch
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction


MODEL_PATH = '/kaggle/working/runs/detect/dota_experiment_aabb11_1024/weights/best.pt'
TEST_IMAGES_DIR = '/kaggle/working/yolo/images/val'

OUTPUT_PREDICTIONS_DIR = '/kaggle/working/predictions'

MODEL_CONF_THRESH = 0.01
SLICE_H, SLICE_W = 1024, 1024
OVER_H, OVER_W = 0.2, 0.2

def main():
    
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    try:
        detection_model = AutoDetectionModel.from_pretrained(
            model_type='yolov8',
            model_path=MODEL_PATH,
            confidence_threshold=MODEL_CONF_THRESH,
            device=device
        )
        print("YOLO model loaded successfully.")
    except Exception as e:
        print(f"ERROR loading model: {e}")
        return

    
    if not os.path.isdir(TEST_IMAGES_DIR):
        print(f"ERROR: Test image directory not found at '{TEST_IMAGES_DIR}'")
        return
        
    image_files = [f for f in os.listdir(TEST_IMAGES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f"Found {len(image_files)} images to process.")

    
    os.makedirs(OUTPUT_PREDICTIONS_DIR, exist_ok=True)
    print(f"🚀 Starting prediction generation...")
    print(f"   All prediction files will be saved to: {OUTPUT_PREDICTIONS_DIR}")

   
    for i, img_name in enumerate(image_files):
        img_path = os.path.join(TEST_IMAGES_DIR, img_name)
        print(f"  Processing image {i+1}/{len(image_files)}: {img_name}", end='\r')

        output_filename = os.path.splitext(img_name)[0] + ".txt"
        output_filepath = os.path.join(OUTPUT_PREDICTIONS_DIR, output_filename)

        try:
            result = get_sliced_prediction(
                img_path,
                detection_model,
                slice_height=SLICE_H,
                slice_width=SLICE_W,
                overlap_height_ratio=OVER_H,
                overlap_width_ratio=OVER_W,
                postprocess_type="GREEDYNMM",
                postprocess_match_metric="IOU",
                postprocess_match_threshold=0.5,
                verbose=0
            )

            img_h = result.image_height
            img_w = result.image_width

            
            with open(output_filepath, 'w') as output_f:
                for pred in result.object_prediction_list:
                    bbox = pred.bbox.to_voc_bbox()
                    x1, y1, x2, y2 = bbox
                    dw = 1. / img_w
                    dh = 1. / img_h
                    x_center = (x1 + x2) / 2.0
                    y_center = (y1 + y2) / 2.0
                    width = x2 - x1
                    height = y2 - y1

                    x_center_norm = x_center * dw
                    y_center_norm = y_center * dh
                    width_norm = width * dw
                    height_norm = height * dh

                    
                    class_id = pred.category.id
                    confidence = pred.score.value
                    output_f.write(f"{class_id} {x_center_norm:.6f} {y_center_norm:.6f} {width_norm:.6f} {height_norm:.6f} {confidence:.6f}\n")

        except Exception as e:
            print(f"\nError processing image {img_name}: {e}")

    print(f"\n Prediction generation complete. All files saved to the '{OUTPUT_PREDICTIONS_DIR}' directory.")


if __name__ == '__main__':
    main()




