def pytest_configure(config):
    """Add custom markers."""
    config.addinivalue_line("markers", "balanced: tests for balanced designs")
    config.addinivalue_line("markers", "crossed: tests for crossed designs")
    config.addinivalue_line("markers", "nested: tests for nested designs")
    config.addinivalue_line("markers", "utils: tests for utility functions")
    config.addinivalue_line("markers", "missing: tests for designs with missing data")
    config.addinivalue_line("markers", "unbalanced: tests for unbalanced designs")