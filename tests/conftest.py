import os

import hypothesis
import pytest

# Provides the testdir fixture
pytest_plugins = "pytester", "hypothesis"

# Change some hypothesis settings
hypothesis.settings.register_profile("ci", max_examples=1000, print_blob=True)
hypothesis.settings.register_profile("dev", max_examples=10)
hypothesis.settings.register_profile(
    "debug", max_examples=10, verbosity=hypothesis.Verbosity.verbose, print_blob=True
)
hypothesis.settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))

# Register the utils module as a helper so that pytest knows to monkey-patch assert
# to give nice diffs on failure.
pytest.register_assert_rewrite("utils")

# Make sure that pytester testdir runs are done as subprocess instead of inprocess.
# Something we (or maybe hypothesis?) does isn't properly cleared by the testdir
# fixture cleanup, so we get erroneous failures when using inprocess.
# This method for accessing config is deprecated, but I can't see another way without
# requiring the user to remember a cmdline arg.
# The alternative to this is always passing --runpytest subprocess
def pytest_configure(config):
    config.option.__dict__["runpytest"] = "subprocess"
