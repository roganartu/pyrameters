def assert_pytest_outcomes(result, passes=0, skips=0, failures=0):
    """Helper to assert that the nested pytest run had the given number of results."""
    passed, skipped, failed = result.listoutcomes()
    assert len(passed) == passes
    assert len(skipped) == skips
    assert len(failed) == failures
