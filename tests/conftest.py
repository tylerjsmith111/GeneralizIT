def pytest_configure(config):
    """Add custom markers."""
    config.addinivalue_line("markers", "balanced: tests for balanced designs")
    config.addinivalue_line("markers", "nested: tests for nested designs")
    config.addinivalue_line("markers", "utils: tests for utility functions")