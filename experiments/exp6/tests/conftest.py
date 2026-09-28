def pytest_configure(config) -> None:
    config.addinivalue_line("markers", "slow: regenerates item files or exercises real git (slow)")
