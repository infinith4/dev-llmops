You are writing E2E (End-to-End) tests. Focus on user scenarios.

1. Identify user flow to test (e.g., login → create item → verify display).
2. Use Playwright (preferred) or Cypress for UI tests.
3. Use appropriate API testing tools for backend integration.
4. Implement proper wait strategies (avoid arbitrary sleeps).
5. Clean up test data after execution.

Test structure:
- Page Object Pattern for UI tests
- Arrange: Set up test data and navigate
- Act: Perform user actions
- Assert: Verify expected outcomes

Commands:
- `npx playwright test` - Run E2E tests
- `npx playwright test --ui` - Interactive mode
- `npx playwright show-report` - View report

Key considerations:
- Tests should be independent and repeatable
- Use test-specific environment variables
- Handle async operations properly
- Consider cross-browser compatibility
