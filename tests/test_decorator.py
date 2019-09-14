from datetime import timedelta
from string import printable

import pytest
from hypothesis import assume, given, seed, settings
from hypothesis import strategies as st

import pyrameters
from utils.decorator import run_in_decorator
from utils.hypothesis import (cases_for, field_values,
                              valid_definition_strings, valid_definitions)


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


@given(
    st.shared(valid_definitions(), key="with_cases"),
    cases_for(
        st.shared(valid_definitions(), key="with_cases"), min_count=1, max_count=50
    ),
)
@settings(deadline=timedelta(milliseconds=1000))
def test_invocation_count_with_def_obj_and_tuples(testdir, definition, cases):
    """
    Verify that the wrapped method is invoked once per test case when using
    pyrameters.Definition.
    """
    # Make sure that the cases generated have the correct number of fields
    # Don't use assume for this, because a failure here is an error, and we don't want
    # hypothesis to workaround it to keep tests green.
    assert all(len(c) == len(definition.fields) for c in cases)

    result = run_in_decorator(testdir, definition, cases)

    # Assert we ran the expected number of tests
    passed, skipped, failed = result.listoutcomes()
    assert len(passed) == len(cases)
    assert len(passed) != 0
    assert len(skipped) == 0
    assert len(failed) == 0


@given(
    st.shared(valid_definition_strings(), key="with_cases"),
    cases_for(
        st.shared(valid_definition_strings(), key="with_cases"),
        min_count=1,
        max_count=50,
    ),
)
@settings(deadline=timedelta(milliseconds=1000))
def test_invocation_count_with_def_string_and_tuples(testdir, definition, cases):
    """
    Verify that the wrapped method is invoked once per test case when using
    a @pytest.mark.parametrize-style string-based definition.
    """
    result = run_in_decorator(testdir, definition, cases)

    # Assert we ran the expected number of tests
    passed, skipped, failed = result.listoutcomes()
    assert len(passed) == len(cases)
    assert len(passed) != 0
    assert len(skipped) == 0
    assert len(failed) == 0


# TODO add test for invocation count using Definition created via string with lists(valid_field_names) and join

# TODO add test for invocation count using Definition created via both string with lists(...) and overrides that are Fields via valid_fields()
