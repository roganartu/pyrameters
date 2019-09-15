from string import printable

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pyrameters import Field
from utils.hypothesis import everything_except


@given(st.text(printable))
@settings(max_examples=settings().max_examples * 100)
def test_empty(name):
    actual = Field.empty(name=name)
    _, ok = actual.default

    assert actual.name == name
    assert ok == False


@given(everything_except(str, type(None)))
@settings(max_examples=settings().max_examples * 50)
def test_empty_failure(name):
    with pytest.raises(ValueError):
        actual = Field.empty(name=name)


@given(
    st.text(printable),
    everything_except(type(None)),
    st.functions(like=(lambda: None), returns=everything_except()),
)
@settings(max_examples=settings().max_examples * 25)
def test_bad_defaults(name, default, factory):
    with pytest.raises(ValueError):
        actual = Field(name=name, default=default, factory=factory)
