import pytest
from pyrameters import Definition, Field

from hypothesis import given
from hypothesis.strategies import text

from utils.hypothesis import everything_except


@given(text().filter(lambda x: x.strip()))
def test_str_args(args):
    actual = Definition(args)

