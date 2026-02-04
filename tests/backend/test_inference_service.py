"""Unit tests for the inference service.

Tests model loading, SAHI prediction, progress updates, and error handling.
"""

import sys
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from PIL import Image

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parents[2] / "backend"))

from app.services.inference import InferenceService, ModelCache
from app.services import storage_service


def create_test_image(width: int = 640, height: int = 480, format: str = "PNG") -> bytes:
    """Helper to create a test image.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        format: Image format (PNG, JPEG, TIFF)
        
    Returns:
        Image data as bytes
    """
    img = Image.new('RGB', (width, height), color='blue')
    buffer = BytesIO()
    img.save(buffer, format=format)
    return buffer.getvalue()


@pytest.fixture
def mock_model():
    """Create a mock SAHI AutoDetectionModel."""
    model = Mock()
    return model


@pytest.fixture
def mock_prediction_result():
    """Create a mock SAHI prediction result."""
    result = Mock()
    result.image_height = 480
    result.image_width = 640
    
    # Create mock prediction object
    pred1 = Mock()
    pred1.category.id = 0
    pred1.category.name = "car"
    pred1.score.value = 0.95
    pred1.bbox.to_voc_bbox.return_value = [10, 20, 100, 80]
    
    pred2 = Mock()
    pred2.category.id = 1
    pred2.category.name = "person"
    pred2.score.value = 0.87
    pred2.bbox.to_voc_bbox.return_value = [150, 200, 250, 400]
    
    result.object_prediction_list = [pred1, pred2]
    
    return result


@pytest.fixture
def test_job_with_images(tmp_path):
    """Create a test job with uploaded images.
    
    Returns:
        Tuple of (job_id, uploaded_files)
    """
    # Create test images
    image1_data = create_test_image(640, 480, "PNG")
    image2_data = create_test_image(800, 600, "JPEG")
    
    # Create job
    job_id = storage_service.create_job(status="uploaded")
    
    # Save images
    file1_id, path1, _ = storage_service.save_upload(
        job_id, "test_image1.png", image1_data
    )
    file2_id, path2, _ = storage_service.save_upload(
        job_id, "test_image2.jpg", image2_data
    )
    
    return job_id, [(file1_id, path1), (file2_id, path2)]


class TestModelCache:
    """Tests for ModelCache class."""
    
    def test_cache_initialization(self):
        """Test that cache initializes empty."""
        cache = ModelCache()
        assert cache._cache == {}
    
    @patch('app.services.inference.AutoDetectionModel.from_pretrained')
    @patch('app.services.inference.torch.cuda.is_available', return_value=False)
    def test_load_model_cpu(self, mock_cuda, mock_from_pretrained, mock_model):
        """Test loading model on CPU."""
        mock_from_pretrained.return_value = mock_model
        
        cache = ModelCache()
        model = cache.get_or_load("/path/to/model.pt", 0.25, device="cpu")
        
        assert model == mock_model
        mock_from_pretrained.assert_called_once()
        
        # Check cache key
        assert len(cache._cache) == 1
    
    @patch('app.services.inference.AutoDetectionModel.from_pretrained')
    @patch('app.services.inference.torch.cuda.is_available', return_value=True)
    def test_load_model_gpu(self, mock_cuda, mock_from_pretrained, mock_model):
        """Test loading model on GPU when available."""
        mock_from_pretrained.return_value = mock_model
        
        cache = ModelCache()
        model = cache.get_or_load("/path/to/model.pt", 0.25, device=None)
        
        assert model == mock_model
        
        # Verify GPU device was used
        call_args = mock_from_pretrained.call_args
        assert call_args[1]['device'] == "cuda:0"
    
    @patch('app.services.inference.AutoDetectionModel.from_pretrained')
    def test_cache_hit(self, mock_from_pretrained, mock_model):
        """Test that cached model is returned on second call."""
        mock_from_pretrained.return_value = mock_model
        
        cache = ModelCache()
        
        # First call - should load
        model1 = cache.get_or_load("/path/to/model.pt", 0.25, device="cpu")
        assert mock_from_pretrained.call_count == 1
        
        # Second call - should use cache
        model2 = cache.get_or_load("/path/to/model.pt", 0.25, device="cpu")
        assert mock_from_pretrained.call_count == 1  # Not called again
        assert model1 == model2
    
    @patch('app.services.inference.AutoDetectionModel.from_pretrained')
    def test_cache_different_params(self, mock_from_pretrained):
        """Test that different parameters result in different cache entries."""
        mock_from_pretrained.side_effect = [Mock(), Mock()]
        
        cache = ModelCache()
        
        # Load with different confidence thresholds
        model1 = cache.get_or_load("/path/to/model.pt", 0.25, device="cpu")
        model2 = cache.get_or_load("/path/to/model.pt", 0.5, device="cpu")
        
        assert mock_from_pretrained.call_count == 2
        assert model1 != model2
        assert len(cache._cache) == 2
    
    @patch('app.services.inference.AutoDetectionModel.from_pretrained')
    def test_load_model_error(self, mock_from_pretrained):
        """Test error handling when model loading fails."""
        mock_from_pretrained.side_effect = RuntimeError("Model file corrupt")
        
        cache = ModelCache()
        
        with pytest.raises(RuntimeError, match="Unable to load YOLO model"):
            cache.get_or_load("/path/to/bad_model.pt", 0.25)
    
    @patch('app.services.inference.AutoDetectionModel.from_pretrained')
    def test_clear_cache(self, mock_from_pretrained, mock_model):
        """Test clearing the model cache."""
        mock_from_pretrained.return_value = mock_model
        
        cache = ModelCache()
        
        # Load a model
        cache.get_or_load("/path/to/model.pt", 0.25)
        assert len(cache._cache) == 1
        
        # Clear cache
        cache.clear()
        assert len(cache._cache) == 0


class TestInferenceService:
    """Tests for InferenceService class."""
    
    def test_service_initialization(self):
        """Test inference service initialization."""
        service = InferenceService()
        assert service.model_cache is not None
    
    @patch('app.services.inference.get_sliced_prediction')
    def test_predict_image_with_sahi(self, mock_get_sliced, mock_prediction_result, tmp_path):
        """Test predicting on a single image with SAHI enabled."""
        mock_get_sliced.return_value = mock_prediction_result
        
        # Create test image
        image_path = tmp_path / "test.png"
        image_data = create_test_image(640, 480)
        image_path.write_bytes(image_data)
        
        # Create mock model
        mock_model = Mock()
        
        service = InferenceService()
        predictions = service._predict_image(
            image_path=image_path,
            model=mock_model,
            sahi_enabled=True,
            slice_height=320,
            slice_width=320,
            overlap_ratio=0.2,
            iou_threshold=0.45
        )
        
        # Verify predictions
        assert len(predictions) == 2
        
        # Check first prediction
        assert predictions[0]["class_id"] == 0
        assert predictions[0]["class_name"] == "car"
        assert predictions[0]["confidence"] == 0.95
        assert "bbox_normalized" in predictions[0]
        assert "bbox_voc" in predictions[0]
        
        # Verify get_sliced_prediction was called with correct params
        mock_get_sliced.assert_called_once()
        call_kwargs = mock_get_sliced.call_args[1]
        assert call_kwargs['slice_height'] == 320
        assert call_kwargs['slice_width'] == 320
        assert call_kwargs['overlap_height_ratio'] == 0.2
    
    @patch('app.services.inference.get_sliced_prediction')
    def test_predict_image_without_sahi(self, mock_get_sliced, mock_prediction_result, tmp_path):
        """Test predicting on a single image with SAHI disabled."""
        mock_get_sliced.return_value = mock_prediction_result
        
        # Create test image
        image_path = tmp_path / "test.png"
        image_data = create_test_image(640, 480)
        image_path.write_bytes(image_data)
        
        mock_model = Mock()
        
        service = InferenceService()
        predictions = service._predict_image(
            image_path=image_path,
            model=mock_model,
            sahi_enabled=False,  # Disabled
            slice_height=640,
            slice_width=640,
            overlap_ratio=0.2,
            iou_threshold=0.45
        )
        
        # Verify predictions
        assert len(predictions) == 2
        
        # When SAHI is disabled, should use large slice dimensions
        call_kwargs = mock_get_sliced.call_args[1]
        assert call_kwargs['slice_height'] == 10000
        assert call_kwargs['slice_width'] == 10000
    
    @patch('app.services.inference.get_sliced_prediction')
    def test_predict_image_error_handling(self, mock_get_sliced, tmp_path):
        """Test error handling during prediction."""
        mock_get_sliced.side_effect = RuntimeError("CUDA out of memory")
        
        # Create test image
        image_path = tmp_path / "test.png"
        image_data = create_test_image(640, 480)
        image_path.write_bytes(image_data)
        
        mock_model = Mock()
        
        service = InferenceService()
        
        with pytest.raises(RuntimeError, match="Prediction failed"):
            service._predict_image(
                image_path=image_path,
                model=mock_model,
                sahi_enabled=True
            )
    
    def test_save_predictions(self, test_job_with_images):
        """Test saving predictions to results directory."""
        job_id, _ = test_job_with_images
        
        # Create test predictions
        predictions = {
            "test_image1.png": [
                {
                    "class_id": 0,
                    "class_name": "car",
                    "confidence": 0.95,
                    "bbox_normalized": [0.5, 0.5, 0.2, 0.3],
                    "bbox_voc": [320, 240, 448, 384]
                }
            ],
            "test_image2.jpg": [
                {
                    "class_id": 1,
                    "class_name": "person",
                    "confidence": 0.87,
                    "bbox_normalized": [0.3, 0.4, 0.15, 0.25],
                    "bbox_voc": [192, 192, 288, 312]
                }
            ]
        }
        
        service = InferenceService()
        service._save_predictions(job_id, predictions)
        
        # Verify .txt files were created
        results_dir = storage_service._get_job_results_dir(job_id, stage="raw")
        
        txt_file1 = results_dir / "test_image1.txt"
        txt_file2 = results_dir / "test_image2.txt"
        
        assert txt_file1.exists()
        assert txt_file2.exists()
        
        # Verify content of first file
        content1 = txt_file1.read_text()
        assert "0 0.500000 0.500000 0.200000 0.300000 0.950000" in content1
        
        # Verify JSON was also saved
        json_result = storage_service.get_result(job_id, stage="raw")
        assert json_result is not None
        assert "test_image1.png" in json_result
    
    @patch('app.services.inference.AutoDetectionModel.from_pretrained')
    @patch('app.services.inference.get_sliced_prediction')
    def test_run_inference_success(
        self, 
        mock_get_sliced, 
        mock_from_pretrained,
        mock_prediction_result, 
        test_job_with_images,
        tmp_path
    ):
        """Test complete inference pipeline."""
        job_id, image_paths = test_job_with_images
        
        # Create mock model
        mock_model = Mock()
        mock_from_pretrained.return_value = mock_model
        mock_get_sliced.return_value = mock_prediction_result
        
        # Create a fake model file
        model_path = tmp_path / "model.pt"
        model_path.write_text("fake model")
        
        service = InferenceService()
        result = service.run_inference(
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
        
        # Verify result
        assert result["job_id"] == job_id
        assert result["processed_images"] == 2
        assert result["total_detections"] == 4  # 2 predictions per image
        assert "elapsed_time" in result
        
        # Verify job status was updated
        job_data = storage_service.get_job(job_id)
        assert job_data["status"] == "completed"
        assert job_data["progress"]["percentage"] == 100
        assert job_data["progress"]["processed_images"] == 2
    
    @patch('app.services.inference.AutoDetectionModel.from_pretrained')
    def test_run_inference_model_not_found(self, mock_from_pretrained, test_job_with_images):
        """Test error handling when model file doesn't exist."""
        job_id, _ = test_job_with_images
        
        service = InferenceService()
        
        with pytest.raises(FileNotFoundError, match="Model not found"):
            service.run_inference(
                job_id=job_id,
                model_path="/nonexistent/model.pt",
                confidence_threshold=0.25
            )
        
        # Verify job status was updated to failed
        job_data = storage_service.get_job(job_id)
        assert job_data["status"] == "failed"
        assert "Model not found" in job_data["error"]
    
    def test_run_inference_job_not_found(self):
        """Test error handling when job doesn't exist."""
        fake_job_id = "00000000-0000-0000-0000-000000000000"
        
        service = InferenceService()
        
        with pytest.raises(ValueError, match="Job not found"):
            service.run_inference(
                job_id=fake_job_id,
                model_path="/path/to/model.pt",
                confidence_threshold=0.25
            )
    
    def test_run_inference_no_files(self, tmp_path):
        """Test error handling when job has no uploaded files."""
        # Create job with no files
        job_id = storage_service.create_job(status="uploaded")
        
        # Create fake model file
        model_path = tmp_path / "model.pt"
        model_path.write_text("fake model")
        
        service = InferenceService()
        
        with pytest.raises(ValueError, match="No files found"):
            service.run_inference(
                job_id=job_id,
                model_path=str(model_path),
                confidence_threshold=0.25
            )
        
        # Verify job status was updated to failed
        job_data = storage_service.get_job(job_id)
        assert job_data["status"] == "failed"
    
    @patch('app.services.inference.AutoDetectionModel.from_pretrained')
    @patch('app.services.inference.get_sliced_prediction')
    def test_run_inference_progress_updates(
        self,
        mock_get_sliced,
        mock_from_pretrained,
        mock_prediction_result,
        test_job_with_images,
        tmp_path
    ):
        """Test that progress is updated during inference."""
        job_id, _ = test_job_with_images
        
        mock_model = Mock()
        mock_from_pretrained.return_value = mock_model
        mock_get_sliced.return_value = mock_prediction_result
        
        # Create fake model file
        model_path = tmp_path / "model.pt"
        model_path.write_text("fake model")
        
        service = InferenceService()
        service.run_inference(
            job_id=job_id,
            model_path=str(model_path),
            confidence_threshold=0.25
        )
        
        # Check final progress
        job_data = storage_service.get_job(job_id)
        progress = job_data["progress"]
        
        assert progress["stage"] == "completed"
        assert progress["percentage"] == 100
        assert progress["total_images"] == 2
        assert progress["processed_images"] == 2
        assert "total_detections" in progress
        assert "elapsed_time" in progress
    
    @patch('app.services.inference.AutoDetectionModel.from_pretrained')
    @patch('app.services.inference.get_sliced_prediction')
    def test_run_inference_with_defaults(
        self,
        mock_get_sliced,
        mock_from_pretrained,
        mock_prediction_result,
        test_job_with_images,
        tmp_path
    ):
        """Test inference with default SAHI configuration."""
        job_id, _ = test_job_with_images
        
        mock_model = Mock()
        mock_from_pretrained.return_value = mock_model
        mock_get_sliced.return_value = mock_prediction_result
        
        # Create fake model file
        model_path = tmp_path / "model.pt"
        model_path.write_text("fake model")
        
        service = InferenceService()
        result = service.run_inference(
            job_id=job_id,
            model_path=str(model_path),
            confidence_threshold=0.25,
            sahi_config=None  # Use defaults
        )
        
        assert result["processed_images"] == 2
        
        # Verify default SAHI params were used (640x640, 0.2 overlap)
        # Check first call to get_sliced_prediction
        call_kwargs = mock_get_sliced.call_args_list[0][1]
        assert call_kwargs['slice_height'] == 640
        assert call_kwargs['slice_width'] == 640
        assert call_kwargs['overlap_height_ratio'] == 0.2
