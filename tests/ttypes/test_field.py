import pytest
from hypothesis import given
from hypothesis.strategies import text

from pyrameters import Field
from utils.hypothesis import everything_except


@given(text())
def test_empty(name):
    actual = Field.empty(name=name)
    _, ok = actual.default

    assert actual.name == name
    assert ok == False


@given(everything_except(str, type(None)))
def test_empty_failure(name):
    with pytest.raises(ValueError):
        actual = Field.empty(name=name)
