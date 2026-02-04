#!/usr/bin/env python
"""Manual test script for SAHI inference service.

This script creates a test scenario to verify the inference service works correctly.
It mocks the SAHI and YOLO components to test the integration logic.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch
from io import BytesIO

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from PIL import Image

from app.services import storage_service, inference_service


def create_test_image(width: int = 640, height: int = 480) -> bytes:
    """Create a test image."""
    img = Image.new('RGB', (width, height), color='green')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def mock_prediction_result():
    """Create a mock SAHI prediction result."""
    result = Mock()
    result.image_height = 480
    result.image_width = 640
    
    # Create mock predictions
    pred1 = Mock()
    pred1.category.id = 0
    pred1.category.name = "car"
    pred1.score.value = 0.95
    pred1.bbox.to_voc_bbox.return_value = [100, 100, 200, 200]
    
    pred2 = Mock()
    pred2.category.id = 1
    pred2.category.name = "person"
    pred2.score.value = 0.87
    pred2.bbox.to_voc_bbox.return_value = [300, 200, 400, 400]
    
    result.object_prediction_list = [pred1, pred2]
    return result


def test_inference_service():
    """Test the inference service with mocked SAHI."""
    
    print("=" * 70)
    print("Testing SAHI Inference Service")
    print("=" * 70)
    
    # Step 1: Create a test job with images
    print("\n1. Creating test job with images...")
    
    image1_data = create_test_image(640, 480)
    image2_data = create_test_image(800, 600)
    
    job_id = storage_service.create_job(status="uploaded")
    print(f"   ✓ Created job: {job_id}")
    
    storage_service.save_upload(job_id, "test1.png", image1_data)
    storage_service.save_upload(job_id, "test2.png", image2_data)
    print(f"   ✓ Uploaded 2 test images")
    
    # Step 2: Mock SAHI components
    print("\n2. Setting up SAHI mocks...")
    
    with patch('app.services.inference.AutoDetectionModel.from_pretrained') as mock_model_load, \
         patch('app.services.inference.get_sliced_prediction') as mock_predict:
        
        # Setup mock model
        mock_model = Mock()
        mock_model_load.return_value = mock_model
        print("   ✓ Mocked model loading")
        
        # Setup mock predictions
        mock_predict.return_value = mock_prediction_result()
        print("   ✓ Mocked SAHI predictions")
        
        # Step 3: Create a fake model file
        print("\n3. Creating fake model file...")
        from pathlib import Path
        model_path = Path("/tmp/test_model.pt")
        model_path.write_text("fake model weights")
        print(f"   ✓ Created fake model at {model_path}")
        
        try:
            # Step 4: Run inference
            print("\n4. Running inference...")
            
            result = inference_service.run_inference(
                job_id=job_id,
                model_path=str(model_path),
                confidence_threshold=0.25,
                iou_threshold=0.45,
                sahi_config={
                    "enabled": True,
                    "slice_height": 320,
                    "slice_width": 320,
                    "overlap_ratio": 0.2
                }
            )
            
            print(f"   ✓ Inference completed successfully")
            print(f"   • Processed images: {result['processed_images']}")
            print(f"   • Total detections: {result['total_detections']}")
            print(f"   • Elapsed time: {result['elapsed_time']:.2f}s")
            
            # Step 5: Verify results
            print("\n5. Verifying results...")
            
            # Check job status
            job_data = storage_service.get_job(job_id)
            assert job_data["status"] == "completed", "Job status should be 'completed'"
            print(f"   ✓ Job status: {job_data['status']}")
            
            # Check progress
            progress = job_data["progress"]
            assert progress["percentage"] == 100, "Progress should be 100%"
            assert progress["processed_images"] == 2, "Should have processed 2 images"
            print(f"   ✓ Progress: {progress['percentage']}%")
            print(f"   ✓ Processed: {progress['processed_images']}/{progress['total_images']} images")
            
            # Check predictions were saved
            results_dir = storage_service._get_job_results_dir(job_id, stage="raw")
            txt_files = list(results_dir.glob("*.txt"))
            assert len(txt_files) == 2, "Should have 2 prediction .txt files"
            print(f"   ✓ Saved {len(txt_files)} prediction files")
            
            # Check JSON results
            json_results = storage_service.get_result(job_id, stage="raw")
            assert json_results is not None, "JSON results should exist"
            assert "test1.png" in json_results, "Results should include test1.png"
            assert "test2.png" in json_results, "Results should include test2.png"
            print(f"   ✓ JSON results saved")
            
            # Check prediction format
            preds = json_results["test1.png"]
            assert len(preds) == 2, "Should have 2 predictions for first image"
            
            pred = preds[0]
            assert "class_id" in pred
            assert "class_name" in pred
            assert "confidence" in pred
            assert "bbox_normalized" in pred
            assert "bbox_voc" in pred
            print(f"   ✓ Prediction format is correct")
            
            # Check .txt file format
            txt_file = results_dir / "test1.txt"
            content = txt_file.read_text()
            lines = content.strip().split('\n')
            assert len(lines) == 2, "Should have 2 prediction lines"
            
            # Parse first line (YOLO format: class_id cx cy w h conf)
            parts = lines[0].split()
            assert len(parts) == 6, "Each line should have 6 values"
            assert parts[0] == "0", "First class_id should be 0"
            print(f"   ✓ .txt file format is correct (YOLO OBB)")
            
            print("\n" + "=" * 70)
            print("✅ ALL TESTS PASSED!")
            print("=" * 70)
            
            return True
            
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            return False
        
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Cleanup
            model_path.unlink(missing_ok=True)


def test_error_handling():
    """Test error handling scenarios."""
    
    print("\n" + "=" * 70)
    print("Testing Error Handling")
    print("=" * 70)
    
    # Test 1: Model not found
    print("\n1. Testing model not found...")
    job_id = storage_service.create_job(status="uploaded")
    image_data = create_test_image()
    storage_service.save_upload(job_id, "test.png", image_data)
    
    try:
        inference_service.run_inference(
            job_id=job_id,
            model_path="/nonexistent/model.pt",
            confidence_threshold=0.25
        )
        print("   ❌ Should have raised FileNotFoundError")
        return False
    except FileNotFoundError:
        print("   ✓ Correctly raised FileNotFoundError")
        
        # Check job status
        job_data = storage_service.get_job(job_id)
        assert job_data["status"] == "failed", "Job should be marked as failed"
        assert "Model not found" in job_data["error"]
        print("   ✓ Job status updated to 'failed'")
    
    # Test 2: Job not found
    print("\n2. Testing job not found...")
    fake_job_id = "00000000-0000-0000-0000-000000000000"
    
    with patch('app.services.inference.AutoDetectionModel.from_pretrained') as mock_load:
        # Mock the model loading to avoid actual YOLO loading
        mock_model = Mock()
        mock_load.return_value = mock_model
        
        # Create a fake model file for this test
        from pathlib import Path
        model_path = Path("/tmp/test_model_job_not_found.pt")
        model_path.write_text("fake model")
        
        try:
            inference_service.run_inference(
                job_id=fake_job_id,
                model_path=str(model_path),
                confidence_threshold=0.25
            )
            print("   ❌ Should have raised ValueError")
            return False
        except ValueError as e:
            assert "Job not found" in str(e)
            print("   ✓ Correctly raised ValueError for missing job")
        finally:
            model_path.unlink(missing_ok=True)
    
    print("\n" + "=" * 70)
    print("✅ ERROR HANDLING TESTS PASSED!")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    print("\n🚀 Starting SAHI Inference Service Tests\n")
    
    success = True
    
    # Run main test
    success = test_inference_service() and success
    
    # Run error handling tests
    success = test_error_handling() and success
    
    if success:
        print("\n✅ All manual tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
