"""Unit tests for the visualization service.

Tests the visualization service functions for generating annotated images
with bounding boxes and labels.
"""

import importlib.util
import sys
from pathlib import Path

import pytest
from PIL import Image

# Add backend to path
backend_path = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(backend_path))


@pytest.fixture(autouse=True)
def mock_settings(tmp_path):
    """Mock backend.app.core.settings for all tests."""
    from unittest.mock import Mock
    
    mock_settings_obj = Mock()
    mock_settings_obj.results_dir = tmp_path / "results"
    mock_settings_obj.uploads_dir = tmp_path / "uploads"
    mock_settings_obj.visualizations_dir = tmp_path / "visualizations"
    
    # Ensure directories exist
    mock_settings_obj.results_dir.mkdir(parents=True, exist_ok=True)
    mock_settings_obj.uploads_dir.mkdir(parents=True, exist_ok=True)
    mock_settings_obj.visualizations_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock backend.app.core module to avoid importing pydantic_settings
    mock_core = Mock()
    mock_core.settings = mock_settings_obj
    sys.modules['backend.app.core'] = mock_core
    
    # Reload the visualization module to pick up the mocked settings
    if 'backend.app.services.visualization' in sys.modules:
        viz_module = sys.modules['backend.app.services.visualization']
        # Update the settings reference in the already loaded module
        viz_module.settings = mock_settings_obj
    
    return mock_settings_obj


# Load visualization module directly to avoid importing heavy dependencies
viz_spec = importlib.util.spec_from_file_location(
    "backend.app.services.visualization",
    backend_path / "app" / "services" / "visualization.py"
)
viz_module = importlib.util.module_from_spec(viz_spec)
sys.modules['backend.app.services.visualization'] = viz_module
viz_spec.loader.exec_module(viz_module)

# Import what we need from the loaded module
CLASS_COLORS = viz_module.CLASS_COLORS
DEFAULT_CLASS_MAP = viz_module.DEFAULT_CLASS_MAP
VisualizationError = viz_module.VisualizationError
VisualizationService = viz_module.VisualizationService
adapt_style_to_image_size = viz_module.adapt_style_to_image_size
generate_color_from_name = viz_module.generate_color_from_name
get_class_color = viz_module.get_class_color
get_label_position = viz_module.get_label_position
get_line_width = viz_module.get_line_width
parse_yolo_predictions = viz_module.parse_yolo_predictions
yolo_to_pixel_coords = viz_module.yolo_to_pixel_coords


class TestColorFunctions:
    """Tests for color-related functions."""
    
    def test_get_class_color_known_class(self):
        """Test getting color for known DOTA class."""
        color = get_class_color('plane')
        assert color == (255, 0, 0)  # Red
        
        color = get_class_color('ship')
        assert color == (0, 255, 0)  # Green
    
    def test_get_class_color_with_underscores(self):
        """Test class name with underscores."""
        color = get_class_color('large_vehicle')
        assert color == (255, 128, 128)  # Light Red
    
    def test_get_class_color_with_hyphens(self):
        """Test class name with hyphens."""
        color = get_class_color('large-vehicle')
        assert color == (255, 128, 128)  # Light Red
    
    def test_get_class_color_unknown_class(self):
        """Test generating color for unknown class."""
        color = get_class_color('unknown_class')
        assert isinstance(color, tuple)
        assert len(color) == 3
        assert all(0 <= c <= 255 for c in color)
    
    def test_generate_color_deterministic(self):
        """Test that color generation is deterministic."""
        color1 = generate_color_from_name('test_class')
        color2 = generate_color_from_name('test_class')
        assert color1 == color2
    
    def test_generate_color_minimum_brightness(self):
        """Test that generated colors have minimum brightness."""
        color = generate_color_from_name('dark_class')
        assert all(c >= 64 for c in color)


class TestLineWidthFunction:
    """Tests for line width calculation."""
    
    def test_line_width_very_high_confidence(self):
        """Test line width for very high confidence."""
        width = get_line_width(0.95, base_width=2)
        assert width == 4  # base_width * 2, capped at max_width
    
    def test_line_width_capped_at_max(self):
        """Test that line width is capped at max_width."""
        # With base_width=4, confidence 0.95 would give 8, but should be capped at 4
        width = get_line_width(0.95, base_width=4, max_width=4)
        assert width == 4
    
    def test_line_width_high_confidence(self):
        """Test line width for high confidence."""
        width = get_line_width(0.75, base_width=2)
        assert width == 2  # base_width
    
    def test_line_width_medium_confidence(self):
        """Test line width for medium confidence."""
        width = get_line_width(0.55, base_width=2)
        assert width == 1  # base_width - 1
    
    def test_line_width_low_confidence(self):
        """Test line width for low confidence."""
        width = get_line_width(0.3, base_width=2)
        assert width == 1  # minimum


class TestStyleAdaptation:
    """Tests for style adaptation based on image size."""
    
    def test_small_image_style(self):
        """Test style for small images."""
        style = adapt_style_to_image_size(640, 480)
        assert style['line_width'] == 1
        assert style['font_size'] == 10
        assert style['label_padding'] == 2
    
    def test_medium_image_style(self):
        """Test style for medium images."""
        style = adapt_style_to_image_size(1024, 1024)
        assert style['line_width'] == 2
        assert style['font_size'] == 14
        assert style['label_padding'] == 3
    
    def test_large_image_style(self):
        """Test style for large images."""
        style = adapt_style_to_image_size(2048, 2048)
        assert style['line_width'] == 3
        assert style['font_size'] == 18
        assert style['label_padding'] == 4
    
    def test_very_large_image_style(self):
        """Test style for very large images."""
        style = adapt_style_to_image_size(4096, 4096)
        assert style['line_width'] == 4
        assert style['font_size'] == 24
        assert style['label_padding'] == 6


class TestPredictionParsing:
    """Tests for YOLO prediction file parsing."""
    
    def test_parse_yolo_predictions_valid_file(self, tmp_path):
        """Test parsing valid YOLO prediction file."""
        # Create test prediction file
        pred_file = tmp_path / "test.txt"
        pred_content = [
            "0 0.5 0.5 0.2 0.3 0.95",
            "1 0.3 0.7 0.15 0.25 0.87",
            "0 0.8 0.2 0.1 0.1 0.76"
        ]
        pred_file.write_text("\n".join(pred_content))
        
        # Parse predictions
        detections = parse_yolo_predictions(pred_file)
        
        # Verify
        assert len(detections) == 3
        
        # Check first detection
        det1 = detections[0]
        assert det1['class_id'] == 0
        assert det1['class_name'] == 'plane'
        assert det1['x_center'] == 0.5
        assert det1['y_center'] == 0.5
        assert det1['width'] == 0.2
        assert det1['height'] == 0.3
        assert det1['confidence'] == 0.95
        assert det1['format'] == 'yolo'
    
    def test_parse_yolo_predictions_custom_class_map(self, tmp_path):
        """Test parsing with custom class map."""
        pred_file = tmp_path / "test.txt"
        pred_file.write_text("0 0.5 0.5 0.2 0.3 0.95\n")
        
        custom_map = {0: "custom_class"}
        detections = parse_yolo_predictions(pred_file, class_map=custom_map)
        
        assert len(detections) == 1
        assert detections[0]['class_name'] == 'custom_class'
    
    def test_parse_yolo_predictions_invalid_lines(self, tmp_path):
        """Test parsing file with invalid lines."""
        pred_file = tmp_path / "test.txt"
        pred_content = [
            "0 0.5 0.5 0.2 0.3 0.95",  # Valid
            "invalid line",             # Invalid
            "1 0.3 0.7 0.15",           # Invalid (too few fields)
            "2 0.4 0.4 0.3 0.3 0.88"    # Valid
        ]
        pred_file.write_text("\n".join(pred_content))
        
        detections = parse_yolo_predictions(pred_file)
        
        # Should only parse valid lines
        assert len(detections) == 2
        assert detections[0]['class_id'] == 0
        assert detections[1]['class_id'] == 2
    
    def test_parse_yolo_predictions_nonexistent_file(self, tmp_path):
        """Test parsing non-existent file."""
        pred_file = tmp_path / "nonexistent.txt"
        detections = parse_yolo_predictions(pred_file)
        
        # Should return empty list
        assert detections == []
    
    def test_parse_yolo_predictions_empty_file(self, tmp_path):
        """Test parsing empty file."""
        pred_file = tmp_path / "empty.txt"
        pred_file.write_text("")
        
        detections = parse_yolo_predictions(pred_file)
        assert detections == []


class TestCoordinateConversion:
    """Tests for coordinate conversion functions."""
    
    def test_yolo_to_pixel_coords(self):
        """Test converting YOLO normalized coords to pixels."""
        detection = {
            'x_center': 0.5,
            'y_center': 0.5,
            'width': 0.2,
            'height': 0.3
        }
        
        bbox = yolo_to_pixel_coords(detection, img_width=1000, img_height=1000)
        
        # Expected: center at (500, 500), size (200, 300)
        # So bbox should be (400, 350, 600, 650)
        assert bbox == (400, 350, 600, 650)
    
    def test_yolo_to_pixel_coords_edge_case(self):
        """Test coordinate conversion at image edges."""
        detection = {
            'x_center': 0.1,
            'y_center': 0.1,
            'width': 0.2,
            'height': 0.2
        }
        
        bbox = yolo_to_pixel_coords(detection, img_width=1000, img_height=1000)
        
        # Center at (100, 100), size (200, 200)
        # Bbox: (0, 0, 200, 200)
        assert bbox == (0, 0, 200, 200)


class TestLabelPositioning:
    """Tests for label position calculation."""
    
    def test_label_position_above_box(self):
        """Test label placement above box when there's space."""
        bbox = (100, 100, 200, 200)
        image_height = 500
        
        position = get_label_position(bbox, image_height)
        
        # Should be above the box
        assert position[0] == 100  # x_min
        assert position[1] == 80   # y_min - 20
    
    def test_label_position_inside_box(self):
        """Test label placement inside box when no space above."""
        bbox = (100, 10, 200, 100)
        image_height = 500
        
        position = get_label_position(bbox, image_height)
        
        # Should be inside the box
        assert position[0] == 105  # x_min + 5
        assert position[1] == 15   # y_min + 5


def create_test_image(width: int = 640, height: int = 480, format: str = "PNG") -> bytes:
    """Helper to create a test image.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        format: Image format (PNG, JPEG)
        
    Returns:
        Image data as bytes
    """
    img = Image.new('RGB', (width, height), color='blue')
    buffer = BytesIO()
    img.save(buffer, format=format)
    return buffer.getvalue()


class TestVisualizationService:
    """Tests for the VisualizationService class."""
    
    @pytest.fixture
    def service(self):
        """Create visualization service instance."""
        return VisualizationService()
    
    @pytest.fixture
    def test_image_with_predictions(self, tmp_path):
        """Create test image and prediction file."""
        # Create test image
        image_path = tmp_path / "test_image.png"
        img = Image.new('RGB', (640, 480), color='white')
        img.save(image_path)
        
        # Create prediction file
        pred_file = tmp_path / "test_image.txt"
        pred_content = [
            "0 0.5 0.5 0.2 0.3 0.95",  # plane at center
            "1 0.3 0.3 0.15 0.2 0.87"  # ship at top-left area
        ]
        pred_file.write_text("\n".join(pred_content))
        
        return image_path, pred_file
    
    def test_visualize_image_success(self, service, test_image_with_predictions, tmp_path):
        """Test successful image visualization."""
        image_path, pred_file = test_image_with_predictions
        output_path = tmp_path / "output" / "annotated.png"
        
        # Visualize
        stats = service.visualize_image(
            image_path,
            pred_file,
            output_path,
            show_labels=True,
            show_confidence=True
        )
        
        # Verify output file exists
        assert output_path.exists()
        
        # Verify stats
        assert stats['image_name'] == 'test_image.png'
        assert stats['detection_count'] == 2
        assert stats['image_width'] == 640
        assert stats['image_height'] == 480
        assert 'output_path' in stats
        
        # Verify output is valid image
        output_img = Image.open(output_path)
        assert output_img.size == (640, 480)
    
    def test_visualize_image_no_detections(self, service, tmp_path):
        """Test visualization with no detections."""
        # Create test image
        image_path = tmp_path / "test_image.png"
        img = Image.new('RGB', (640, 480), color='white')
        img.save(image_path)
        
        # Create empty prediction file
        pred_file = tmp_path / "test_image.txt"
        pred_file.write_text("")
        
        output_path = tmp_path / "output" / "annotated.png"
        
        # Visualize
        stats = service.visualize_image(image_path, pred_file, output_path)
        
        # Should still save the image
        assert output_path.exists()
        assert stats['detection_count'] == 0
    
    def test_visualize_image_missing_image(self, service, tmp_path):
        """Test error when image file doesn't exist."""
        image_path = tmp_path / "nonexistent.png"
        pred_file = tmp_path / "test.txt"
        pred_file.write_text("0 0.5 0.5 0.2 0.3 0.95\n")
        output_path = tmp_path / "output.png"
        
        # Should raise error
        with pytest.raises(VisualizationError, match="Image file not found"):
            service.visualize_image(image_path, pred_file, output_path)
    
    def test_visualize_image_without_labels(self, service, test_image_with_predictions, tmp_path):
        """Test visualization without labels."""
        image_path, pred_file = test_image_with_predictions
        output_path = tmp_path / "output" / "annotated.png"
        
        # Visualize without labels
        stats = service.visualize_image(
            image_path,
            pred_file,
            output_path,
            show_labels=False
        )
        
        # Should still work
        assert output_path.exists()
        assert stats['detection_count'] == 2
    
    def test_visualize_image_grayscale_conversion(self, service, tmp_path):
        """Test that grayscale images are converted to RGB."""
        # Create grayscale image
        image_path = tmp_path / "gray_image.png"
        img = Image.new('L', (640, 480), color=128)
        img.save(image_path)
        
        # Create prediction file
        pred_file = tmp_path / "gray_image.txt"
        pred_file.write_text("0 0.5 0.5 0.2 0.3 0.95\n")
        
        output_path = tmp_path / "output" / "annotated.png"
        
        # Visualize
        service.visualize_image(image_path, pred_file, output_path)
        
        # Verify output is RGB
        assert output_path.exists()
        output_img = Image.open(output_path)
        assert output_img.mode == 'RGB'


class TestVisualizationJobProcessing:
    """Tests for visualize_job method."""
    
    @pytest.fixture
    def service(self):
        """Create visualization service instance."""
        return VisualizationService()
    
    def test_visualize_job_with_multiple_images(self, service, mock_settings, tmp_path):
        """Test visualizing multiple images in a job."""
        job_id = "test-job-123"
        
        # Create directories
        upload_dir = mock_settings.uploads_dir / job_id
        upload_dir.mkdir(parents=True)
        
        predictions_dir = mock_settings.results_dir / job_id / "refined"
        predictions_dir.mkdir(parents=True)
        
        # Create test images and predictions
        for i in range(3):
            img = Image.new('RGB', (640, 480), color='white')
            img_path = upload_dir / f"test-{i}.png"
            img.save(img_path)
            
            # Create predictions
            pred_file = predictions_dir / f"test-{i}.txt"
            pred_content = [
                f"0 0.5 0.5 0.2 0.3 0.{90 + i}",
                f"1 0.3 0.3 0.15 0.2 0.{85 + i}"
            ]
            pred_file.write_text("\n".join(pred_content))
        
        # Create mock storage service
        from unittest.mock import Mock
        mock_storage = Mock()
        mock_storage.get_job.return_value = {
            'files': [
                {'stored_filename': f'test-{i}.png', 'file_id': f'test-{i}'} 
                for i in range(3)
            ]
        }
        
        # Visualize job
        stats = service.visualize_job(
            job_id=job_id,
            stage="refined",
            storage_service=mock_storage
        )
        
        # Verify statistics
        assert stats['total_images'] == 3
        assert stats['visualized_images'] == 3
        assert stats['failed_images'] == 0
        assert stats['total_detections'] == 6  # 2 detections per image
        
        # Verify output files exist
        viz_dir = mock_settings.visualizations_dir / job_id
        assert viz_dir.exists()
        assert len(list(viz_dir.glob("*.png"))) == 3
    
    def test_visualize_job_with_missing_predictions(self, service, mock_settings, tmp_path):
        """Test handling of missing prediction files."""
        job_id = "test-job-456"
        
        # Create directories
        upload_dir = mock_settings.uploads_dir / job_id
        upload_dir.mkdir(parents=True)
        
        predictions_dir = mock_settings.results_dir / job_id / "nms"
        predictions_dir.mkdir(parents=True)
        
        # Create image but no prediction file
        img = Image.new('RGB', (640, 480), color='white')
        img_path = upload_dir / "test.png"
        img.save(img_path)
        
        # Create mock storage service
        from unittest.mock import Mock
        mock_storage = Mock()
        mock_storage.get_job.return_value = {
            'files': [{'stored_filename': 'test.png', 'file_id': 'test'}]
        }
        
        # Visualize job (should handle missing prediction gracefully)
        stats = service.visualize_job(
            job_id=job_id,
            stage="nms",
            storage_service=mock_storage
        )
        
        # Should report failed image
        assert stats['total_images'] == 1
        assert stats['visualized_images'] == 0
        assert stats['failed_images'] == 1


class TestVisualizationIntegration:
    """Integration tests for visualization pipeline."""
    
    @pytest.mark.skip(reason="Full integration test covered in test_visualization_endpoint.py")
    def test_visualize_multiple_images(self, mock_job_structure):
        """Test visualizing multiple images in a job.
        
        This placeholder is skipped as full integration testing
        for multi-image visualization is covered in the endpoint tests.
        """
        pass



