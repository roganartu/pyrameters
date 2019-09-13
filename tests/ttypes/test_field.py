from string import printable

import pytest
from hypothesis import given
from hypothesis import strategies as st

from pyrameters import Field
from utils.hypothesis import everything_except, valid_json


@given(st.text(printable))
def test_empty(name):
    actual = Field.empty(name=name)
    _, ok = actual.default

    assert actual.name == name
    assert ok == False


@given(everything_except(str, type(None)))
def test_empty_failure(name):
    with pytest.raises(ValueError):
        actual = Field.empty(name=name)


@given(
    st.text(printable),
    everything_except(type(None)),
    st.functions(like=(lambda: None), returns=valid_json()),
)
def test_bad_defaults(name, default, factory):
    with pytest.raises(ValueError):
        actual = Field(name=name, default=default, factory=factory)
