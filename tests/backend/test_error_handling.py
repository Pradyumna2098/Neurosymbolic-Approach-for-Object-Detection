"""Tests for error handling utilities.

Tests error codes, error messages, and retry logic.
"""

import pytest
from backend.app.core.errors import (
    ErrorCode,
    get_error_message,
    should_retry,
    get_retry_delay,
    ERROR_MESSAGES,
)


class TestErrorCodes:
    """Test error code definitions and utilities."""

    def test_error_code_enum_values(self):
        """Test that all error codes are properly defined."""
        # Check some key error codes exist
        assert ErrorCode.INTERNAL_ERROR == "INTERNAL_ERROR"
        assert ErrorCode.FILE_NOT_FOUND == "FILE_NOT_FOUND"
        assert ErrorCode.INVALID_CONFIG == "INVALID_CONFIG"
        assert ErrorCode.RATE_LIMIT_EXCEEDED == "RATE_LIMIT_EXCEEDED"
        
    def test_all_error_codes_have_messages(self):
        """Test that every error code has a corresponding message."""
        for code in ErrorCode:
            assert code in ERROR_MESSAGES, f"Missing message for {code}"
            assert ERROR_MESSAGES[code], f"Empty message for {code}"
            assert isinstance(ERROR_MESSAGES[code], str)

    def test_error_messages_are_user_friendly(self):
        """Test that error messages are user-friendly."""
        # Messages should be descriptive and not contain technical jargon
        for code, message in ERROR_MESSAGES.items():
            assert len(message) > 10, f"Message too short for {code}: {message}"
            assert not message.startswith("Error:"), f"Generic error prefix for {code}"
            # Should not contain Python exception class names
            assert "Exception" not in message
            assert "Error:" not in message


class TestGetErrorMessage:
    """Test error message retrieval."""

    def test_get_error_message_basic(self):
        """Test basic error message retrieval."""
        message = get_error_message(ErrorCode.FILE_NOT_FOUND)
        assert message == ERROR_MESSAGES[ErrorCode.FILE_NOT_FOUND]
        assert "file" in message.lower()

    def test_get_error_message_with_custom(self):
        """Test error message with custom addition."""
        base_message = ERROR_MESSAGES[ErrorCode.MODEL_LOAD_ERROR]
        custom = "Model path: /path/to/model.pt"
        
        message = get_error_message(ErrorCode.MODEL_LOAD_ERROR, custom)
        
        assert base_message in message
        assert custom in message

    def test_get_error_message_with_internal_error(self):
        """Test error message retrieval for internal error code."""
        message = get_error_message(ErrorCode.INTERNAL_ERROR)
        assert "error" in message.lower()
        assert len(message) > 0


class TestShouldRetry:
    """Test retry determination logic."""

    def test_retriable_errors(self):
        """Test that transient errors are marked as retriable."""
        retriable = [
            ErrorCode.INTERNAL_ERROR,
            ErrorCode.STORAGE_ERROR,
            ErrorCode.MEMORY_ERROR,
            ErrorCode.CUDA_OOM,
            ErrorCode.RATE_LIMIT_EXCEEDED,
            ErrorCode.INFERENCE_ERROR,
        ]
        
        for code in retriable:
            assert should_retry(code), f"{code} should be retriable"

    def test_non_retriable_errors(self):
        """Test that permanent errors are not retriable."""
        non_retriable = [
            ErrorCode.FILE_NOT_FOUND,
            ErrorCode.INVALID_REQUEST,
            ErrorCode.VALIDATION_ERROR,
            ErrorCode.JOB_NOT_FOUND,
            ErrorCode.MODEL_NOT_FOUND,
            ErrorCode.INVALID_CONFIG,
        ]
        
        for code in non_retriable:
            assert not should_retry(code), f"{code} should not be retriable"


class TestGetRetryDelay:
    """Test retry delay calculation."""

    def test_exponential_backoff(self):
        """Test exponential backoff for retries."""
        # First retry: 5 seconds
        assert get_retry_delay(ErrorCode.INTERNAL_ERROR, 1) == 5
        
        # Second retry: 15 seconds (5 * 3^1)
        assert get_retry_delay(ErrorCode.INTERNAL_ERROR, 2) == 15
        
        # Third retry: 45 seconds (5 * 3^2)
        assert get_retry_delay(ErrorCode.INTERNAL_ERROR, 3) == 45

    def test_rate_limit_fixed_delay(self):
        """Test that rate limiting has a fixed 60-second delay."""
        # Rate limiting should always return 60 seconds regardless of attempt
        assert get_retry_delay(ErrorCode.RATE_LIMIT_EXCEEDED, 1) == 60
        assert get_retry_delay(ErrorCode.RATE_LIMIT_EXCEEDED, 2) == 60
        assert get_retry_delay(ErrorCode.RATE_LIMIT_EXCEEDED, 3) == 60

    def test_different_error_types_backoff(self):
        """Test that different error types use the same exponential backoff."""
        errors = [
            ErrorCode.STORAGE_ERROR,
            ErrorCode.MEMORY_ERROR,
            ErrorCode.INFERENCE_ERROR,
        ]
        
        for error in errors:
            # All should use same exponential backoff
            assert get_retry_delay(error, 1) == 5
            assert get_retry_delay(error, 2) == 15
            assert get_retry_delay(error, 3) == 45


class TestErrorCodeCategories:
    """Test error code categorization."""

    def test_file_errors(self):
        """Test file-related error codes."""
        file_errors = [
            ErrorCode.FILE_NOT_FOUND,
            ErrorCode.FILE_TOO_LARGE,
            ErrorCode.INVALID_FILE_FORMAT,
            ErrorCode.UPLOAD_FAILED,
        ]
        
        for code in file_errors:
            message = get_error_message(code)
            assert "file" in message.lower() or "upload" in message.lower()

    def test_job_errors(self):
        """Test job-related error codes."""
        job_errors = [
            ErrorCode.JOB_NOT_FOUND,
            ErrorCode.JOB_ALREADY_RUNNING,
            ErrorCode.JOB_FAILED,
            ErrorCode.INVALID_JOB_STATUS,
        ]
        
        for code in job_errors:
            message = get_error_message(code)
            assert "job" in message.lower()

    def test_model_errors(self):
        """Test model/inference error codes."""
        model_errors = [
            ErrorCode.MODEL_NOT_FOUND,
            ErrorCode.MODEL_LOAD_ERROR,
            ErrorCode.INFERENCE_ERROR,
        ]
        
        for code in model_errors:
            message = get_error_message(code)
            assert any(word in message.lower() for word in ["model", "detection", "inference"])

    def test_resource_errors(self):
        """Test resource-related error codes."""
        resource_errors = [
            ErrorCode.MEMORY_ERROR,
            ErrorCode.CUDA_OOM,
            ErrorCode.STORAGE_ERROR,
        ]
        
        for code in resource_errors:
            message = get_error_message(code)
            assert any(word in message.lower() for word in ["memory", "storage", "gpu"])



