"""Unit tests for the inference service.

Tests the InferenceService class for SAHI-based YOLO inference,
including model loading, prediction, and error handling.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parents[2] / "backend"))

from app.services.inference import InferenceError, InferenceService


class TestInferenceService:
    """Test cases for InferenceService."""
    
    @pytest.fixture
    def service(self):
        """Create InferenceService instance."""
        return InferenceService()
    
    @pytest.fixture
    def mock_storage_service(self):
        """Create mock storage service."""
        mock = Mock()
        mock.get_job.return_value = {
            "job_id": "test-job-123",
            "status": "processing",
            "files": [
                {
                    "file_id": "file-1",
                    "filename": "test_image.jpg",
                    "stored_filename": "abc123.jpg",
                }
            ]
        }
        return mock
    
    def test_detect_device_with_cuda(self, service):
        """Test device detection returns cuda when available."""
        with patch('torch.cuda.is_available', return_value=True):
            with patch('torch.cuda.get_device_name', return_value='NVIDIA RTX 3090'):
                device = service._detect_device()
                assert device == 'cuda'
    
    def test_detect_device_without_cuda(self, service):
        """Test device detection returns cpu when cuda unavailable."""
        with patch('torch.cuda.is_available', return_value=False):
            device = service._detect_device()
            assert device == 'cpu'
    
    def test_load_model_with_invalid_path(self, service):
        """Test load_model raises error for non-existent model."""
        with pytest.raises(InferenceError, match="Model file not found"):
            service.load_model("/nonexistent/model.pt")
    
    def test_load_model_with_invalid_extension(self, service, tmp_path):
        """Test load_model raises error for wrong file extension."""
        invalid_model = tmp_path / "model.txt"
        invalid_model.write_text("not a model")
        
        with pytest.raises(InferenceError, match="Invalid model file extension"):
            service.load_model(str(invalid_model))
    
    @patch('sahi.AutoDetectionModel')
    @patch('torch.cuda.is_available', return_value=False)
    def test_load_model_success(self, mock_cuda, mock_auto_model, service, tmp_path):
        """Test successful model loading."""
        # Create fake model file
        model_path = tmp_path / "model.pt"
        model_path.write_bytes(b"fake model data")
        
        # Mock AutoDetectionModel
        mock_model = Mock()
        mock_auto_model.from_pretrained.return_value = mock_model
        
        # Load model
        result = service.load_model(str(model_path))
        
        # Verify model was loaded
        assert result == mock_model
        mock_auto_model.from_pretrained.assert_called_once_with(
            model_type='yolov8',
            model_path=str(model_path),
            confidence_threshold=0.01,
            device='cpu',
        )
    
    @patch('sahi.AutoDetectionModel')
    @patch('torch.cuda.is_available', return_value=False)
    def test_load_model_caching(self, mock_cuda, mock_auto_model, service, tmp_path):
        """Test model caching works correctly."""
        model_path = tmp_path / "model.pt"
        model_path.write_bytes(b"fake model")
        
        mock_model = Mock()
        mock_auto_model.from_pretrained.return_value = mock_model
        
        # Load model first time
        result1 = service.load_model(str(model_path))
        
        # Load model second time (should use cache)
        result2 = service.load_model(str(model_path))
        
        # Verify same model returned
        assert result1 == result2
        
        # Verify from_pretrained called only once
        assert mock_auto_model.from_pretrained.call_count == 1
    
    @patch('sahi.AutoDetectionModel')
    @patch('torch.cuda.is_available', return_value=False)
    def test_load_model_force_reload(self, mock_cuda, mock_auto_model, service, tmp_path):
        """Test force_reload bypasses cache."""
        model_path = tmp_path / "model.pt"
        model_path.write_bytes(b"fake model")
        
        mock_model = Mock()
        mock_auto_model.from_pretrained.return_value = mock_model
        
        # Load model first time
        service.load_model(str(model_path))
        
        # Force reload
        service.load_model(str(model_path), force_reload=True)
        
        # Verify from_pretrained called twice
        assert mock_auto_model.from_pretrained.call_count == 2
    
    def test_extract_predictions_filters_by_confidence(self, service):
        """Test _extract_predictions filters low confidence predictions."""
        # Mock SAHI result
        mock_result = Mock()
        mock_result.image_height = 1000
        mock_result.image_width = 1000
        
        # Create mock predictions
        pred1 = Mock()
        pred1.score.value = 0.9
        pred1.category.id = 0
        pred1.bbox.to_voc_bbox.return_value = (100, 100, 200, 200)
        
        pred2 = Mock()
        pred2.score.value = 0.1  # Low confidence
        pred2.category.id = 1
        pred2.bbox.to_voc_bbox.return_value = (300, 300, 400, 400)
        
        mock_result.object_prediction_list = [pred1, pred2]
        
        # Extract with threshold 0.25
        predictions = service._extract_predictions(mock_result, 0.25)
        
        # Should only keep high confidence prediction
        assert len(predictions) == 1
        assert predictions[0]['confidence'] == 0.9
        assert predictions[0]['class_id'] == 0
    
    def test_extract_predictions_converts_to_yolo_format(self, service):
        """Test _extract_predictions converts coordinates correctly."""
        mock_result = Mock()
        mock_result.image_height = 1000
        mock_result.image_width = 2000
        
        # Create mock prediction with known bbox
        pred = Mock()
        pred.score.value = 0.8
        pred.category.id = 5
        # VOC bbox: x1=100, y1=200, x2=300, y2=400
        pred.bbox.to_voc_bbox.return_value = (100, 200, 300, 400)
        
        mock_result.object_prediction_list = [pred]
        
        predictions = service._extract_predictions(mock_result, 0.5)
        
        assert len(predictions) == 1
        p = predictions[0]
        
        # Expected values:
        # x_center = (100 + 300) / 2 = 200
        # y_center = (200 + 400) / 2 = 300
        # width = 300 - 100 = 200
        # height = 400 - 200 = 200
        # Normalized by image dimensions (2000x1000)
        assert p['class_id'] == 5
        assert p['x_center'] == pytest.approx(200 / 2000)  # 0.1
        assert p['y_center'] == pytest.approx(300 / 1000)  # 0.3
        assert p['width'] == pytest.approx(200 / 2000)     # 0.1
        assert p['height'] == pytest.approx(200 / 1000)    # 0.2
        assert p['confidence'] == 0.8
    
    def test_save_predictions_to_txt(self, service, tmp_path):
        """Test _save_predictions_to_txt saves correct format."""
        predictions = [
            {
                'class_id': 0,
                'x_center': 0.5,
                'y_center': 0.5,
                'width': 0.2,
                'height': 0.3,
                'confidence': 0.95
            },
            {
                'class_id': 1,
                'x_center': 0.3,
                'y_center': 0.7,
                'width': 0.15,
                'height': 0.25,
                'confidence': 0.87
            }
        ]
        
        output_path = tmp_path / "predictions.txt"
        service._save_predictions_to_txt(predictions, output_path)
        
        # Read file and verify format
        assert output_path.exists()
        lines = output_path.read_text().strip().split('\n')
        assert len(lines) == 2
        
        # First prediction
        parts1 = lines[0].split()
        assert len(parts1) == 6
        assert parts1[0] == '0'
        assert float(parts1[1]) == pytest.approx(0.5)
        assert float(parts1[5]) == pytest.approx(0.95)
        
        # Second prediction
        parts2 = lines[1].split()
        assert parts2[0] == '1'
        assert float(parts2[1]) == pytest.approx(0.3)
    
    def test_save_predictions_empty_list(self, service, tmp_path):
        """Test _save_predictions_to_txt handles empty predictions."""
        output_path = tmp_path / "empty.txt"
        service._save_predictions_to_txt([], output_path)
        
        assert output_path.exists()
        content = output_path.read_text()
        assert content == ""
    
    @patch('sahi.predict.get_sliced_prediction')
    @patch.object(InferenceService, 'load_model')
    @patch('torch.cuda.is_available', return_value=False)
    def test_run_inference_success(
        self, 
        mock_cuda, 
        mock_load_model, 
        mock_sliced_pred,
        service, 
        mock_storage_service,
        tmp_path
    ):
        """Test successful inference run."""
        # Setup paths
        job_id = "test-job-123"
        upload_dir = tmp_path / "uploads" / job_id
        upload_dir.mkdir(parents=True)
        results_dir = tmp_path / "results" / job_id / "raw"
        results_dir.mkdir(parents=True)
        
        # Create test image
        test_image = upload_dir / "abc123.jpg"
        test_image.write_bytes(b"fake image data")
        
        # Mock settings
        with patch('app.services.inference.settings') as mock_settings:
            mock_settings.uploads_dir = tmp_path / "uploads"
            mock_settings.results_dir = tmp_path / "results"
            
            # Mock model
            mock_model = Mock()
            mock_load_model.return_value = mock_model
            
            # Mock SAHI result
            mock_result = Mock()
            mock_result.image_height = 1000
            mock_result.image_width = 1000
            
            pred = Mock()
            pred.score.value = 0.9
            pred.category.id = 0
            pred.bbox.to_voc_bbox.return_value = (100, 100, 200, 200)
            
            mock_result.object_prediction_list = [pred]
            mock_sliced_pred.return_value = mock_result
            
            # Run inference
            stats = service.run_inference(
                job_id=job_id,
                model_path=str(tmp_path / "model.pt"),
                confidence_threshold=0.25,
                iou_threshold=0.45,
                sahi_config={
                    'slice_width': 640,
                    'slice_height': 640,
                    'overlap_ratio': 0.2
                },
                storage_service=mock_storage_service,
            )
            
            # Verify statistics
            assert stats['total_images'] == 1
            assert stats['processed_images'] == 1
            assert stats['total_detections'] >= 0
            
            # Verify prediction file created
            pred_file = results_dir / "test_image.txt"
            assert pred_file.exists()
    
    @patch.object(InferenceService, 'load_model')
    def test_run_inference_no_files(
        self,
        mock_load_model,
        service,
        mock_storage_service
    ):
        """Test run_inference raises error when no files found."""
        mock_storage_service.get_job.return_value = {
            "job_id": "test-job",
            "files": []
        }
        
        with pytest.raises(InferenceError, match="No files found"):
            service.run_inference(
                job_id="test-job",
                model_path="/fake/model.pt",
                confidence_threshold=0.25,
                iou_threshold=0.45,
                sahi_config={},
                storage_service=mock_storage_service,
            )
    
    @patch.object(InferenceService, 'load_model')
    def test_run_inference_model_loading_failure(
        self,
        mock_load_model,
        service,
        mock_storage_service
    ):
        """Test run_inference handles model loading failures."""
        mock_load_model.side_effect = InferenceError("Model load failed")
        
        with pytest.raises(InferenceError, match="Model load failed"):
            service.run_inference(
                job_id="test-job",
                model_path="/fake/model.pt",
                confidence_threshold=0.25,
                iou_threshold=0.45,
                sahi_config={},
                storage_service=mock_storage_service,
            )
    
    def test_apply_nms_post_processing_success(self, service, mock_storage_service, tmp_path):
        """Test successful NMS post-processing."""
        job_id = "test-job-456"
        
        # Setup directories
        raw_dir = tmp_path / "results" / job_id / "raw"
        nms_dir = tmp_path / "results" / job_id / "nms"
        raw_dir.mkdir(parents=True)
        
        # Create raw prediction file with overlapping detections
        pred_file = raw_dir / "test_image.txt"
        pred_file.write_text(
            "0 0.5 0.5 0.2 0.2 0.95\n"  # High confidence
            "0 0.51 0.51 0.19 0.19 0.85\n"  # Overlapping, lower confidence
            "1 0.3 0.3 0.1 0.1 0.9\n"  # Different class
        )
        
        # Mock settings
        with patch('app.services.inference.settings') as mock_settings:
            mock_settings.results_dir = tmp_path / "results"
            
            # Run NMS
            stats = service.apply_nms_post_processing(
                job_id=job_id,
                iou_threshold=0.5,
                storage_service=mock_storage_service
            )
            
            # Verify statistics
            assert stats['total_before'] == 3
            assert stats['total_after'] == 2  # One overlapping detection removed
            assert stats['reduction_count'] == 1
            assert stats['reduction_percentage'] > 0
            assert 'elapsed_time_seconds' in stats
            
            # Verify NMS directory created
            assert nms_dir.exists()
            
            # Verify NMS filtered file created
            nms_file = nms_dir / "test_image.txt"
            assert nms_file.exists()
            
            # Verify filtered predictions
            lines = nms_file.read_text().strip().split('\n')
            assert len(lines) == 2  # Only 2 detections after NMS
    
    def test_apply_nms_post_processing_no_raw_predictions(self, service, mock_storage_service, tmp_path):
        """Test NMS with no raw predictions directory."""
        job_id = "test-job-789"
        
        with patch('app.services.inference.settings') as mock_settings:
            mock_settings.results_dir = tmp_path / "results"
            
            # Should raise error
            with pytest.raises(InferenceError, match="Raw predictions directory not found"):
                service.apply_nms_post_processing(
                    job_id=job_id,
                    iou_threshold=0.5,
                    storage_service=mock_storage_service
                )
    
    def test_apply_nms_post_processing_empty_predictions(self, service, mock_storage_service, tmp_path):
        """Test NMS with empty raw predictions directory."""
        job_id = "test-job-empty"
        
        # Setup empty raw directory
        raw_dir = tmp_path / "results" / job_id / "raw"
        raw_dir.mkdir(parents=True)
        
        with patch('app.services.inference.settings') as mock_settings:
            mock_settings.results_dir = tmp_path / "results"
            
            # Run NMS
            stats = service.apply_nms_post_processing(
                job_id=job_id,
                iou_threshold=0.5,
                storage_service=mock_storage_service
            )
            
            # Verify statistics for empty case
            assert stats['total_before'] == 0
            assert stats['total_after'] == 0
            assert stats['reduction_count'] == 0
            assert stats['reduction_percentage'] == 0.0
    
    def test_save_nms_predictions(self, service, tmp_path):
        """Test _save_nms_predictions saves correct format."""
        predictions_dict = {
            "image1.png": [
                {
                    'category_id': 0,
                    'bbox_yolo': [0.5, 0.5, 0.2, 0.2],
                    'confidence': 0.95
                },
                {
                    'category_id': 1,
                    'bbox_yolo': [0.3, 0.3, 0.15, 0.15],
                    'confidence': 0.87
                }
            ],
            "image2.png": [
                {
                    'category_id': 0,
                    'bbox_yolo': [0.6, 0.7, 0.1, 0.1],
                    'confidence': 0.92
                }
            ]
        }
        
        output_dir = tmp_path / "nms"
        output_dir.mkdir()
        
        service._save_nms_predictions(predictions_dict, output_dir)
        
        # Verify files created
        file1 = output_dir / "image1.txt"
        file2 = output_dir / "image2.txt"
        assert file1.exists()
        assert file2.exists()
        
        # Verify file1 content
        lines1 = file1.read_text().strip().split('\n')
        assert len(lines1) == 2
        parts1 = lines1[0].split()
        assert len(parts1) == 6
        assert parts1[0] == '0'
        assert float(parts1[1]) == pytest.approx(0.5)
        assert float(parts1[5]) == pytest.approx(0.95)
        
        # Verify file2 content
        lines2 = file2.read_text().strip().split('\n')
        assert len(lines2) == 1
        parts2 = lines2[0].split()
        assert parts2[0] == '0'
        assert float(parts2[5]) == pytest.approx(0.92)
    
    def test_apply_nms_reduces_overlapping_same_class(self, service, mock_storage_service, tmp_path):
        """Test NMS correctly removes overlapping detections of the same class."""
        job_id = "test-job-overlap"
        
        # Setup directories
        raw_dir = tmp_path / "results" / job_id / "raw"
        raw_dir.mkdir(parents=True)
        
        # Create prediction file with highly overlapping detections (same class)
        pred_file = raw_dir / "overlap_test.txt"
        pred_file.write_text(
            "0 0.5 0.5 0.2 0.2 0.95\n"  # Detection 1
            "0 0.505 0.505 0.21 0.21 0.90\n"  # Highly overlapping with det 1
            "0 0.8 0.8 0.1 0.1 0.85\n"  # Different location, same class
        )
        
        with patch('app.services.inference.settings') as mock_settings:
            mock_settings.results_dir = tmp_path / "results"
            
            stats = service.apply_nms_post_processing(
                job_id=job_id,
                iou_threshold=0.5,
                storage_service=mock_storage_service
            )
            
            # Should reduce from 3 to 2 (one overlapping removed)
            assert stats['total_before'] == 3
            assert stats['total_after'] == 2
    
    def test_apply_nms_keeps_different_classes(self, service, mock_storage_service, tmp_path):
        """Test NMS preserves overlapping detections of different classes."""
        job_id = "test-job-multiclass"
        
        # Setup directories
        raw_dir = tmp_path / "results" / job_id / "raw"
        raw_dir.mkdir(parents=True)
        
        # Create prediction file with overlapping detections (different classes)
        pred_file = raw_dir / "multiclass_test.txt"
        pred_file.write_text(
            "0 0.5 0.5 0.2 0.2 0.95\n"  # Class 0
            "1 0.51 0.51 0.19 0.19 0.90\n"  # Class 1, overlapping location
            "2 0.52 0.52 0.18 0.18 0.85\n"  # Class 2, overlapping location
        )
        
        with patch('app.services.inference.settings') as mock_settings:
            mock_settings.results_dir = tmp_path / "results"
            
            stats = service.apply_nms_post_processing(
                job_id=job_id,
                iou_threshold=0.5,
                storage_service=mock_storage_service
            )
            
            # All should be kept (different classes)
            assert stats['total_before'] == 3
            assert stats['total_after'] == 3
            assert stats['reduction_count'] == 0
