"""Unit tests for the symbolic reasoning service.

Tests the SymbolicReasoningService class for Prolog-based confidence
adjustment, including rule loading, modifier application, and file I/O.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parents[2] / "backend"))

from app.services.symbolic import SymbolicReasoningError, SymbolicReasoningService


class TestSymbolicReasoningService:
    """Test cases for SymbolicReasoningService."""
    
    @pytest.fixture
    def service(self):
        """Create SymbolicReasoningService instance."""
        return SymbolicReasoningService()
    
    @pytest.fixture
    def mock_storage_service(self):
        """Create mock storage service."""
        mock = Mock()
        return mock
    
    @pytest.fixture
    def sample_prolog_rules(self, tmp_path):
        """Create sample Prolog rules file."""
        rules_file = tmp_path / "rules.pl"
        rules_content = """
% Test rules for symbolic reasoning
confidence_modifier(ship, harbor, 1.25).
confidence_modifier(harbor, ship, 1.25).
confidence_modifier(plane, harbor, 0.2).
confidence_modifier(harbor, plane, 0.2).
"""
        rules_file.write_text(rules_content)
        return rules_file
    
    @pytest.fixture
    def sample_predictions(self, tmp_path):
        """Create sample NMS predictions directory."""
        nms_dir = tmp_path / "nms"
        nms_dir.mkdir()
        
        # Create prediction file with 2 objects
        pred_file = nms_dir / "test_image.txt"
        pred_content = """0 0.5 0.5 0.2 0.2 0.9
1 0.6 0.6 0.15 0.15 0.8
"""
        pred_file.write_text(pred_content)
        
        return nms_dir
    
    def test_load_prolog_engine_with_missing_file(self, service):
        """Test load_prolog_engine raises error for missing rules file."""
        with pytest.raises(SymbolicReasoningError, match="Prolog rules file not found"):
            service._load_prolog_engine(Path("/nonexistent/rules.pl"))
    
    @patch('pyswip.Prolog')
    def test_load_prolog_engine_success(self, mock_prolog_class, service, sample_prolog_rules):
        """Test successful Prolog engine loading."""
        mock_prolog = Mock()
        mock_prolog_class.return_value = mock_prolog
        
        result = service._load_prolog_engine(sample_prolog_rules)
        
        assert result == mock_prolog
        mock_prolog.consult.assert_called_once_with(str(sample_prolog_rules))
    
    def test_load_modifier_map(self, service):
        """Test loading modifier map from Prolog engine."""
        mock_prolog = Mock()
        mock_prolog.query.return_value = [
            {"A": "ship", "B": "harbor", "Weight": 1.25},
            {"A": "plane", "B": "harbor", "Weight": 0.2},
        ]
        
        modifier_map = service._load_modifier_map(mock_prolog)
        
        assert len(modifier_map) == 2
        assert modifier_map[("ship", "harbor")] == 1.25
        assert modifier_map[("plane", "harbor")] == 0.2
    
    def test_parse_predictions(self, service, sample_predictions):
        """Test parsing YOLO prediction files."""
        predictions = service._parse_predictions(sample_predictions)
        
        assert "test_image" in predictions
        assert len(predictions["test_image"]) == 2
        
        # Check first prediction
        pred1 = predictions["test_image"][0]
        assert pred1["category_id"] == 0
        assert pred1["confidence"] == 0.9
        assert "bbox" in pred1
        assert "bbox_yolo" in pred1
    
    def test_parse_predictions_empty_directory(self, service, tmp_path):
        """Test parsing predictions from empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        predictions = service._parse_predictions(empty_dir)
        
        assert len(predictions) == 0
    
    def test_parse_predictions_missing_directory(self, service):
        """Test parsing predictions from missing directory."""
        predictions = service._parse_predictions(Path("/nonexistent"))
        
        assert len(predictions) == 0
    
    def test_get_bbox_center(self, service):
        """Test bounding box center calculation."""
        bbox = [10, 20, 30, 40]
        center = service._get_bbox_center(bbox)
        
        assert center == (20.0, 30.0)
    
    def test_get_distance(self, service):
        """Test distance calculation between bounding boxes."""
        bbox_a = [0, 0, 10, 10]
        bbox_b = [30, 40, 50, 60]
        
        distance = service._get_distance(bbox_a, bbox_b)
        
        # Distance between centers (5, 5) and (40, 50)
        expected = (35**2 + 45**2) ** 0.5
        assert abs(distance - expected) < 0.001
    
    def test_get_bbox_diagonal(self, service):
        """Test bounding box diagonal calculation."""
        bbox = [0, 0, 3, 4]  # 3-4-5 triangle
        diagonal = service._get_bbox_diagonal(bbox)
        
        assert abs(diagonal - 5.0) < 0.001
    
    def test_get_bbox_area(self, service):
        """Test bounding box area calculation."""
        bbox = [0, 0, 10, 20]
        area = service._get_bbox_area(bbox)
        
        assert area == 200.0
    
    def test_get_intersection_area(self, service):
        """Test intersection area calculation."""
        bbox_a = [0, 0, 10, 10]
        bbox_b = [5, 5, 15, 15]
        
        intersection = service._get_intersection_area(bbox_a, bbox_b)
        
        # Intersection is 5x5 square
        assert intersection == 25.0
    
    def test_get_intersection_area_no_overlap(self, service):
        """Test intersection area with no overlap."""
        bbox_a = [0, 0, 10, 10]
        bbox_b = [20, 20, 30, 30]
        
        intersection = service._get_intersection_area(bbox_a, bbox_b)
        
        assert intersection == 0.0
    
    def test_apply_modifiers_boost(self, service):
        """Test applying boost modifier to nearby objects."""
        objects = [
            {
                "id": "det_0",
                "category_id": 1,  # ship
                "bbox": [0.4, 0.4, 0.6, 0.6],
                "bbox_yolo": [0.5, 0.5, 0.2, 0.2],
                "confidence": 0.7,
            },
            {
                "id": "det_1",
                "category_id": 7,  # harbor
                "bbox": [0.5, 0.5, 0.7, 0.7],
                "bbox_yolo": [0.6, 0.6, 0.2, 0.2],
                "confidence": 0.6,
            },
        ]
        
        modifier_map = {
            ("ship", "harbor"): 1.25,
        }
        
        class_map = {1: "ship", 7: "harbor"}
        
        modified_objects, change_log = service._apply_modifiers(objects, modifier_map, class_map)
        
        # Both objects should have boosted confidence
        assert len(modified_objects) == 2
        assert modified_objects[0]["confidence"] > 0.7
        assert modified_objects[1]["confidence"] > 0.6
        
        # Should have one log entry
        assert len(change_log) == 1
        assert change_log[0]["action"] == "BOOST"
    
    def test_apply_modifiers_penalty(self, service):
        """Test applying penalty modifier to overlapping objects."""
        objects = [
            {
                "id": "det_0",
                "category_id": 0,  # plane
                "bbox": [0.4, 0.4, 0.6, 0.6],
                "bbox_yolo": [0.5, 0.5, 0.2, 0.2],
                "confidence": 0.9,
            },
            {
                "id": "det_1",
                "category_id": 7,  # harbor
                "bbox": [0.45, 0.45, 0.65, 0.65],
                "bbox_yolo": [0.55, 0.55, 0.2, 0.2],
                "confidence": 0.3,
            },
        ]
        
        modifier_map = {
            ("plane", "harbor"): 0.2,
        }
        
        class_map = {0: "plane", 7: "harbor"}
        
        modified_objects, change_log = service._apply_modifiers(objects, modifier_map, class_map)
        
        # Lower confidence object should be penalized
        assert len(modified_objects) == 2
        harbor_obj = [obj for obj in modified_objects if obj["category_id"] == 7][0]
        assert harbor_obj["confidence"] < 0.3
        
        # Should have one log entry
        assert len(change_log) == 1
        assert change_log[0]["action"] == "PENALTY"
    
    def test_apply_modifiers_no_rules(self, service):
        """Test applying modifiers with no matching rules."""
        objects = [
            {
                "id": "det_0",
                "category_id": 0,
                "bbox": [0.4, 0.4, 0.6, 0.6],
                "bbox_yolo": [0.5, 0.5, 0.2, 0.2],
                "confidence": 0.7,
            },
        ]
        
        modifier_map = {}
        class_map = {0: "plane"}
        
        modified_objects, change_log = service._apply_modifiers(objects, modifier_map, class_map)
        
        # No changes should be made
        assert len(modified_objects) == 1
        assert modified_objects[0]["confidence"] == 0.7
        assert len(change_log) == 0
    
    def test_save_predictions(self, service, tmp_path):
        """Test saving predictions to YOLO format files."""
        predictions = {
            "image1": [
                {
                    "category_id": 0,
                    "bbox_yolo": [0.5, 0.5, 0.2, 0.2],
                    "confidence": 0.9,
                },
            ],
            "image2": [
                {
                    "category_id": 1,
                    "bbox_yolo": [0.3, 0.3, 0.1, 0.1],
                    "confidence": 0.8,
                },
            ],
        }
        
        output_dir = tmp_path / "output"
        service._save_predictions(predictions, output_dir)
        
        # Check files were created
        assert (output_dir / "image1.txt").exists()
        assert (output_dir / "image2.txt").exists()
        
        # Check content of first file
        content = (output_dir / "image1.txt").read_text()
        assert "0 0.5" in content
        assert "0.9" in content
    
    def test_save_explainability_report(self, service, tmp_path):
        """Test saving explainability report to CSV."""
        report = [
            {
                "image_name": "test.png",
                "action": "BOOST",
                "rule_pair": "ship<->harbor",
                "object_1": "ship",
                "conf_1_before": "0.70",
                "conf_1_after": "0.88",
                "object_2": "harbor",
                "conf_2_before": "0.60",
                "conf_2_after": "0.75",
            },
        ]
        
        report_file = tmp_path / "report.csv"
        service._save_explainability_report(report, report_file)
        
        assert report_file.exists()
        
        # Check CSV content
        content = report_file.read_text()
        assert "image_name" in content
        assert "BOOST" in content
        assert "ship<->harbor" in content
    
    def test_save_explainability_report_empty(self, service, tmp_path):
        """Test saving empty explainability report."""
        report = []
        report_file = tmp_path / "report.csv"
        
        service._save_explainability_report(report, report_file)
        
        # No file should be created for empty report
        assert not report_file.exists()
    
    @patch('app.services.symbolic.SymbolicReasoningService._load_prolog_engine')
    @patch('app.services.symbolic.SymbolicReasoningService._load_modifier_map')
    def test_apply_symbolic_reasoning_missing_rules(
        self,
        mock_load_modifiers,
        mock_load_prolog,
        service,
        tmp_path,
        mock_storage_service
    ):
        """Test symbolic reasoning with missing rules file."""
        # Setup paths
        job_id = "test-job-123"
        rules_file = tmp_path / "nonexistent.pl"
        
        result = service.apply_symbolic_reasoning(
            job_id=job_id,
            rules_file=rules_file,
            storage_service=mock_storage_service
        )
        
        # Should skip processing
        assert result["skipped"] is True
        assert "not found" in result["reason"].lower()
    
    @patch('app.services.symbolic.SymbolicReasoningService._load_prolog_engine')
    @patch('app.services.symbolic.SymbolicReasoningService._load_modifier_map')
    def test_apply_symbolic_reasoning_no_modifiers(
        self,
        mock_load_modifiers,
        mock_load_prolog,
        service,
        sample_prolog_rules,
        tmp_path,
        mock_storage_service
    ):
        """Test symbolic reasoning with no modifier rules loaded."""
        # Setup mocks
        mock_prolog = Mock()
        mock_load_prolog.return_value = mock_prolog
        mock_load_modifiers.return_value = {}  # No modifiers
        
        job_id = "test-job-123"
        
        result = service.apply_symbolic_reasoning(
            job_id=job_id,
            rules_file=sample_prolog_rules,
            storage_service=mock_storage_service
        )
        
        # Should skip processing
        assert result["skipped"] is True
        assert "no modifier rules" in result["reason"].lower()
    
    @patch('app.services.symbolic.settings')
    @patch('app.services.symbolic.SymbolicReasoningService._load_prolog_engine')
    @patch('app.services.symbolic.SymbolicReasoningService._load_modifier_map')
    def test_apply_symbolic_reasoning_success(
        self,
        mock_load_modifiers,
        mock_load_prolog,
        mock_settings,
        service,
        sample_prolog_rules,
        sample_predictions,
        tmp_path,
        mock_storage_service
    ):
        """Test successful symbolic reasoning application."""
        # Setup mocks
        mock_prolog = Mock()
        mock_load_prolog.return_value = mock_prolog
        mock_load_modifiers.return_value = {
            ("plane", "ship"): 1.15,  # Boost rule
        }
        
        # Setup paths
        job_id = "test-job-123"
        results_dir = tmp_path / "results" / job_id
        results_dir.mkdir(parents=True)
        
        # Copy sample predictions to nms directory
        nms_dir = results_dir / "nms"
        nms_dir.mkdir()
        for pred_file in sample_predictions.iterdir():
            (nms_dir / pred_file.name).write_text(pred_file.read_text())
        
        mock_settings.results_dir = tmp_path / "results"
        
        result = service.apply_symbolic_reasoning(
            job_id=job_id,
            rules_file=sample_prolog_rules,
            storage_service=mock_storage_service
        )
        
        # Should complete successfully
        assert "skipped" not in result or not result["skipped"]
        assert result["total_images"] == 1
        assert result["refined_images"] == 1
        assert isinstance(result["elapsed_time_seconds"], (int, float))
        
        # Check refined predictions were saved
        refined_dir = results_dir / "refined"
        assert refined_dir.exists()
        assert (refined_dir / "test_image.txt").exists()


class TestSymbolicReasoningIntegration:
    """Integration tests for symbolic reasoning with real Prolog files."""
    
    @pytest.fixture
    def real_prolog_rules(self, tmp_path):
        """Create realistic Prolog rules file based on DOTA dataset."""
        rules_file = tmp_path / "rules.pl"
        rules_content = """
% Vehicle categories
vehicle(plane).
vehicle(ship).
vehicle(large_vehicle).
vehicle(small_vehicle).
vehicle(helicopter).

% Infrastructure
infrastructure(harbor).
infrastructure(bridge).

% Confidence modifiers
confidence_modifier(ship, harbor, 1.25).
confidence_modifier(harbor, ship, 1.25).
confidence_modifier(plane, harbor, 0.2).
confidence_modifier(harbor, plane, 0.2).
confidence_modifier(ship, bridge, 0.1).
confidence_modifier(bridge, ship, 0.1).
"""
        rules_file.write_text(rules_content)
        return rules_file
    
    @pytest.mark.skipif(
        True,  # Skip by default as it requires pyswip/SWI-Prolog
        reason="Requires PySwip and SWI-Prolog installation"
    )
    def test_real_prolog_integration(self, service, real_prolog_rules):
        """Test with real Prolog engine (requires PySwip)."""
        prolog = service._load_prolog_engine(real_prolog_rules)
        modifier_map = service._load_modifier_map(prolog)
        
        # Should load multiple modifiers
        assert len(modifier_map) > 0
        assert ("ship", "harbor") in modifier_map
        assert modifier_map[("ship", "harbor")] == 1.25
