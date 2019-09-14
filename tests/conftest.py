import os

import hypothesis
import pytest

# Provides the testdir fixture
pytest_plugins = "pytester"

# Change some hypothesis settings
hypothesis.settings.register_profile("default", max_examples=50)
hypothesis.settings.register_profile("ci", max_examples=1000)
hypothesis.settings.register_profile("dev", max_examples=10)
hypothesis.settings.register_profile(
    "debug", max_examples=10, verbosity=hypothesis.Verbosity.verbose
)
hypothesis.settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "default"))

# Register the utils module as a helper so that pytest knows to monkey-patch assert
# to give nice diffs on failure.
pytest.register_assert_rewrite("utils")
