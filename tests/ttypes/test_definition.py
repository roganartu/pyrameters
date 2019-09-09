import pytest
from pyrameters import Definition, Field

from hypothesis import given, strategies as st

from utils.hypothesis import everything_except, non_empty_string


def valid_definition_str():
    return non_empty_string().filter(lambda x: x.replace(",", "").strip())


@given(valid_definition_str())
def test_str_args(args):
    actual = Definition(args)


@given(
    valid_definition_str(),
    st.dictionaries(
        st.shared(non_empty_string(), key="field"),
        st.shared(non_empty_string(), key="field"),
        min_size=1,
    ),
)
def test_with_kwargs(args, kwargs):
    actual = Definition(**kwargs)
    assert len(actual.fields) > 0
