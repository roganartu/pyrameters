import pytest
from hypothesis import given
from hypothesis import strategies as st

import pyrameters


@pyrameters.test_cases("x", [1, 2, 3])
def test_cases_smoke_test(x):
    """Verify that the decorator at least runs successfully."""
    assert isinstance(x, int)


@pyrameters.test_cases("x, y", [(1, "2"), (3, "4")])
def test_cases_smoke_test_multi(x, y):
    """Verify that the decorator at least runs successfully."""
    assert isinstance(x, int)
    assert isinstance(y, str)


@given(st.text())
@pyrameters.test_cases("x", [1, 2, 3])
def test_cases_unused_smoke_test(x, y):
    """Verify that unused args are pass through unconsumed."""
    assert isinstance(x, int)
    assert isinstance(y, str)


@given(st.text())
@pyrameters.test_cases("x,y", [(1, 2), (3, 4)])
def test_cases_unused_smoke_test_multi(x, y, z):
    """Verify that unused args are pass through unconsumed."""
    assert isinstance(x, int)
    assert isinstance(y, int)
    assert isinstance(z, str)
