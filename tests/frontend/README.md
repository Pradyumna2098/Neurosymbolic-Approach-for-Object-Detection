# Frontend Tests

This directory contains tests for the frontend subproject.

## Structure

```
tests/frontend/
├── unit/                 # Unit tests for components (planned)
├── integration/          # Integration tests (planned)
└── e2e/                  # End-to-end tests (planned)
```

## Running Tests

```bash
# Run all frontend tests
pytest tests/frontend/ -v    # For Python-based tests
# or
npm test                     # For JavaScript/TypeScript tests

# Run specific test type
npm run test:unit
npm run test:integration
npm run test:e2e
```

## Test Requirements

When implementing frontend tests, ensure:
1. Unit tests for individual components
2. Integration tests for component interactions
3. E2E tests for critical user workflows
4. Accessibility testing
5. Responsive design testing
6. Cross-browser compatibility

## Tools (Proposed)

- **Unit Testing**: Jest, Vitest, or Testing Library
- **E2E Testing**: Playwright, Cypress, or Selenium
- **Component Testing**: Storybook with visual regression testing
- **Coverage**: Istanbul or c8

## Related

- See [Frontend README](../../frontend/README.md) for frontend architecture
- See main [Testing Instructions](.github/instructions/tests.instructions.md) for testing guidelines
