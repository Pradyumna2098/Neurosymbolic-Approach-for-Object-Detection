# Backend Tests

This directory contains tests for the backend subproject.

## Structure

```
tests/backend/
├── test_api.py           # API endpoint tests (planned)
├── test_auth.py          # Authentication tests (planned)
├── test_job_management.py # Job queue tests (planned)
└── test_models.py        # Database model tests (planned)
```

## Running Tests

```bash
# Run all backend tests
pytest tests/backend/ -v

# Run specific test file
pytest tests/backend/test_api.py -v

# Run with coverage
pytest tests/backend/ --cov=backend
```

## Test Requirements

When implementing backend tests, ensure:
1. Use mocking for external dependencies (database, APIs)
2. Test both success and error scenarios
3. Validate input validation and error handling
4. Test authentication and authorization
5. Include integration tests for API endpoints

## Related

- See [Backend README](../../backend/README.md) for backend architecture
- See main [Testing Instructions](../../.github/instructions/tests.instructions.md) for testing guidelines
