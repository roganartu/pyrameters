from datetime import timedelta
from string import printable

import dill as pickle
import pytest
from hypothesis import given, seed, settings
from hypothesis import strategies as st

import pyrameters
from utils.hypothesis import field_values, valid_definitions


@pyrameters.test_cases("x", [1, 2, 3])
def test_cases_smoke_test(x):
    """Verify that the decorator at least runs successfully."""
    assert isinstance(x, int)


@pyrameters.test_cases("x, y", [(1, "2"), (3, "4")])
def test_cases_smoke_test_multi(x, y):
    """Verify that the decorator at least runs successfully."""
    assert isinstance(x, int)
    assert isinstance(y, str)


@given(st.text(printable))
@pyrameters.test_cases("x", [1, 2, 3])
def test_cases_unused_smoke_test(x, y):
    """Verify that unused args are pass through unconsumed."""
    assert isinstance(x, int)
    assert isinstance(y, str)


@given(st.text(printable))
@pyrameters.test_cases("x,y", [(1, 2), (3, 4)])
def test_cases_unused_smoke_test_multi(x, y, z):
    """Verify that unused args are pass through unconsumed."""
    assert isinstance(x, int)
    assert isinstance(y, int)
    assert isinstance(z, str)


@given(valid_definitions(), st.integers(min_value=1, max_value=50), st.data())
@settings(deadline=timedelta(milliseconds=1000))
def test_invocation_count_via_tuples(testdir, definition, count, data):
    """
    Verify that the wrapped method is invoked once per test case when using
    pyrameters.Definition.
    """
    # Generate the input data for the invocations
    cases = []
    for _ in range(count):
        cases.append(
            tuple(data.draw(field_values(), label=f) for f in definition.fields)
        )

    # Run the test through the decorator, calling a mock
    # We can use the pytest testdir fixture to run a dynamically generated Python test
    # file, and then assert the number of lines in the output is the number of cases we
    # expected to run.
    # The easiest way to achieve this is to simply pickle the fn variable, and then
    # unpickle it into a function with the test_ prefix.
    # TODO this fails to serialize fields that have a factory
    pickled_def = pickle.dumps(definition)
    pickled_cases = pickle.dumps(cases)
    result = testdir.inline_runsource(
        """
        import dill as pickle
        import pytest

        import pyrameters

        definition = pickle.loads({})
        cases = pickle.loads({})

        @pyrameters.test_cases(definition, cases)
        def test_nested({}):
            assert True
    """.format(
            pickled_def, pickled_cases, str(definition)
        ),
        "-qq",
    )

    # Assert we ran the expected number of tests
    passed, skipped, failed = result.listoutcomes()
    assert len(passed) == count
    assert len(skipped) == 0
    assert len(failed) == 0


# TODO add test for invocation count using Definition created via string with lists(valid_field_names) and join

# TODO add test for invocation count using Definition created via both string with lists(...) and overrides that are Fields via valid_fields()
