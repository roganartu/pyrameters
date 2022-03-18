from datetime import timedelta
from string import printable

import pytest
from hypothesis import assume, given, seed, settings
from hypothesis import strategies as st

import pyrameters
from utils.decorator import run_in_decorator
from utils.hypothesis import any_style_definitions, cases_for, field_values


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
@settings(max_examples=settings().max_examples * 30)
@pyrameters.test_cases("x", [1, 2, 3])
def test_cases_unused_smoke_test(x, y):
    """Verify that unused args are pass through unconsumed."""
    assert isinstance(x, int)
    assert isinstance(y, str)


@given(st.text(printable))
@settings(max_examples=settings().max_examples * 30)
@pyrameters.test_cases("x,y", [(1, 2), (3, 4)])
def test_cases_unused_smoke_test_multi(x, y, z):
    """Verify that unused args are pass through unconsumed."""
    assert isinstance(x, int)
    assert isinstance(y, int)
    assert isinstance(z, str)


@given(
    st.shared(any_style_definitions(), key="with_cases"),
    cases_for(
        st.shared(any_style_definitions(), key="with_cases"), min_count=1, max_count=25
    ),
)
@settings(
    deadline=timedelta(milliseconds=2000), max_examples=settings().max_examples * 1
)
# TODO make a specific example of the following:
# definition='a', cases=[None, None]
def test_invocation_count_with_tuples(testdir, definition, cases):
    """
    Verify that the wrapped method is invoked once per test case when using
    pyrameters.Definition or a @pytest.mark.parametrize-style string-based definition.
    """
    result = run_in_decorator(testdir, definition, cases)
    assert result.ret == 0

    passed, skipped, failed = result.listoutcomes()
    assert len(passed) == len(cases)
    assert len(skipped) == 0
    assert len(failed) == 0


# TODO add a test to ensure we get the expected exception when a string definition is
# provided and Mapping test cases missing one or more of the definition values
# are provided.

# TODO add test that ensures that @pytest.parameter is passed through unaffected,
# same as a regular tuple param.
# Do this by adding a @pytest.parameter builds to cases_for
