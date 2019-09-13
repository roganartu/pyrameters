import os

import hypothesis

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
