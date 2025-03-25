# GeneralizIT Test Suite

This directory contains the test suite for the GeneralizIT package, which implements Generalizability Theory analysis with both crossed and nested designs.

## Directory Structure

```
tests/
├── README.md                       # This file
├── conftest.py                     # Pytest configuration
├── design_test_base.py             # Base testing class
├── test_design_utils.py            # Tests for utility functions
├── balanced_designs/               # Tests for balanced designs
│   ├── crossed_designs/            # Tests for fully crossed designs
│   │   ├── test_design1.py         # person x item design
│   │   └── test_design3.py         # other crossed designs
│   ├── nested_designs/             # Tests for nested designs
│   │   ├── test_design2.py         # items:persons design
│   │   └── test_design4.py         # person x (r:t)
└── fixtures/                       # Test data fixtures
    ├── design1_fixtures.py         # Data for person x item design
    ├── design2_fixtures.py         # Data for items:persons design
    └── ...                         # Additional fixture files
```

## Testing Framework

The test suite is built on pytest with a custom base class architecture:

### DesignTestBase (in design_test_base.py)
Base class that provides shared testing functionality including:

- Methods for testing individual G-theory components (T values, variance, etc.)
- Helper methods for asserting expected values with configurable tolerance
- Method chaining for concise and readable tests
- Composite methods for comprehensive testing

### Test Fixtures (in /fixtures/)
Provide test data and expected values for different design types

### Test Categories
Organized using pytest markers:

- `balanced`: Tests for balanced designs
- `nested`: Tests for nested designs
- `utils`: Tests for utility functions

## Test Types

### Component Tests
Verify individual calculation steps:
- T values (uncorrected sum of squares)
- Variance components
- G-coefficients (rho², phi²)

### End-to-End Tests
Verify full analysis workflows:
- Full ANOVA table calculation
- Complete analysis including G-coefficients

## Running the Test Suite

Run all tests:
```bash
pytest
```

Run tests for a specific design type:
```bash
pytest -m balanced     # Only balanced designs
pytest -m nested       # Only nested designs
pytest -m utils        # Only utility functions
pytest -m "not nested" # Everything except nested designs
```

## Adding New Tests

To add a new design test:

1. Create a fixture file in /fixtures/ following the pattern in design1_fixtures.py
2. Create a test file in the appropriate directory using the existing tests as templates
3. Apply the appropriate markers for categorization

For utility tests, add parametrized tests to test_design_utils.py.

## Test Methodology

Tests follow a consistent pattern:

1. Construct a design from synthetic data
2. Apply the appropriate calculations
3. Compare results against known expected values
4. Verify full computation workflows

The method chaining pattern enables convenient and readable test code.