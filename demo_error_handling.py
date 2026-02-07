#!/usr/bin/env python3
"""
Demonstration script for error handling utilities.

This script demonstrates the error code definitions, error messages,
and retry logic without requiring FastAPI dependencies.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.errors import (
    ErrorCode,
    get_error_message,
    should_retry,
    get_retry_delay,
    ERROR_MESSAGES,
)


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print('=' * 80)


def demo_error_codes():
    """Demonstrate error code definitions."""
    print_section("Error Code Definitions")
    
    print("\n📋 Available Error Codes:")
    for code in ErrorCode:
        print(f"  • {code.value}")
    
    print(f"\n✅ Total: {len(list(ErrorCode))} error codes defined")


def demo_error_messages():
    """Demonstrate error message mapping."""
    print_section("Error Messages")
    
    # Show a sample of error messages
    sample_errors = [
        ErrorCode.FILE_NOT_FOUND,
        ErrorCode.MODEL_LOAD_ERROR,
        ErrorCode.RATE_LIMIT_EXCEEDED,
        ErrorCode.VALIDATION_ERROR,
    ]
    
    print("\n📝 Sample Error Messages:")
    for code in sample_errors:
        message = get_error_message(code)
        print(f"\n  {code.value}:")
        print(f"    \"{message}\"")
    
    # Demonstrate custom message
    print("\n  With custom details:")
    custom = "Model path: /models/yolov11.pt not found"
    message = get_error_message(ErrorCode.MODEL_LOAD_ERROR, custom)
    print(f"    \"{message}\"")


def demo_retry_logic():
    """Demonstrate retry determination logic."""
    print_section("Retry Logic")
    
    # Retriable errors
    print("\n✅ Retriable Errors (will retry automatically):")
    retriable = [
        ErrorCode.INTERNAL_ERROR,
        ErrorCode.STORAGE_ERROR,
        ErrorCode.MEMORY_ERROR,
        ErrorCode.CUDA_OOM,
        ErrorCode.RATE_LIMIT_EXCEEDED,
        ErrorCode.INFERENCE_ERROR,
    ]
    
    for code in retriable:
        print(f"  • {code.value}")
    
    # Non-retriable errors
    print("\n❌ Non-Retriable Errors (permanent failures):")
    non_retriable = [
        ErrorCode.FILE_NOT_FOUND,
        ErrorCode.INVALID_REQUEST,
        ErrorCode.VALIDATION_ERROR,
        ErrorCode.JOB_NOT_FOUND,
        ErrorCode.MODEL_NOT_FOUND,
    ]
    
    for code in non_retriable:
        print(f"  • {code.value}")


def demo_retry_delays():
    """Demonstrate retry delay calculation."""
    print_section("Retry Delays (Exponential Backoff)")
    
    # Standard exponential backoff
    print("\n⏱️  Standard Errors (exponential backoff):")
    for attempt in range(1, 4):
        delay = get_retry_delay(ErrorCode.INTERNAL_ERROR, attempt)
        print(f"  Attempt {attempt}: {delay} seconds")
    
    # Rate limiting special case
    print("\n⏱️  Rate Limiting (fixed delay):")
    for attempt in range(1, 4):
        delay = get_retry_delay(ErrorCode.RATE_LIMIT_EXCEEDED, attempt)
        print(f"  Attempt {attempt}: {delay} seconds")


def demo_error_categories():
    """Demonstrate error categorization."""
    print_section("Error Categories")
    
    categories = {
        "File/Upload": [
            ErrorCode.FILE_NOT_FOUND,
            ErrorCode.FILE_TOO_LARGE,
            ErrorCode.INVALID_FILE_FORMAT,
            ErrorCode.UPLOAD_FAILED,
        ],
        "Job": [
            ErrorCode.JOB_NOT_FOUND,
            ErrorCode.JOB_ALREADY_RUNNING,
            ErrorCode.JOB_FAILED,
        ],
        "Model/Inference": [
            ErrorCode.MODEL_NOT_FOUND,
            ErrorCode.MODEL_LOAD_ERROR,
            ErrorCode.INFERENCE_ERROR,
        ],
        "Resource": [
            ErrorCode.STORAGE_ERROR,
            ErrorCode.MEMORY_ERROR,
            ErrorCode.CUDA_OOM,
        ],
    }
    
    for category, codes in categories.items():
        print(f"\n📦 {category} Errors:")
        for code in codes:
            retriable = "✅ Retriable" if should_retry(code) else "❌ Not retriable"
            print(f"  • {code.value:30} {retriable}")


def demo_workflow_example():
    """Demonstrate a typical error handling workflow."""
    print_section("Example Workflow")
    
    print("\n🔄 Simulated Error Handling Flow:")
    print("\n1. API call fails with CUDA_OOM error")
    
    error_code = ErrorCode.CUDA_OOM
    message = get_error_message(error_code)
    
    print(f"   Error Code: {error_code.value}")
    print(f"   Message: \"{message}\"")
    print(f"   Retriable: {should_retry(error_code)}")
    
    if should_retry(error_code):
        print("\n2. Retry schedule:")
        for attempt in range(1, 4):
            delay = get_retry_delay(error_code, attempt)
            print(f"   Attempt {attempt}: Wait {delay}s before retry")
        print("\n3. After 3 failed retries, show error to user")
    else:
        print("\n2. Error is not retriable - show error to user immediately")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 80)
    print("  Error Handling System Demonstration")
    print("  Neurosymbolic Object Detection")
    print("=" * 80)
    
    demo_error_codes()
    demo_error_messages()
    demo_retry_logic()
    demo_retry_delays()
    demo_error_categories()
    demo_workflow_example()
    
    print("\n" + "=" * 80)
    print("  ✅ Demonstration Complete")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
