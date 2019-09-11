import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from pyrameters import Definition, Field
from utils.hypothesis import everything_except, non_empty_string


def extract_args(arg_def):
    return [x.strip() for x in arg_def.split(",") if x.strip()]


def no_dupes(arg_def):
    args = extract_args(arg_def)
    return len(set(args)) == len(args)


def valid_definition_str():
    return (
        non_empty_string().filter(lambda x: x.replace(",", "").strip()).filter(no_dupes)
    )


@given(valid_definition_str())
def test_str_args(arg_def):
    actual = Definition(arg_def)
    assert len(actual.fields) == len(extract_args(arg_def))


@given(valid_definition_str(), st.data())
def test_with_kwargs(arg_def, data):
    args = extract_args(arg_def)
    kwargs = {k: k for k in data.draw(st.sets(non_empty_string(), min_size=1))}

    assume(not any(a in kwargs for a in args))

    actual = Definition(arg_def, **kwargs)
    assert len(actual.fields) == len(extract_args(arg_def)) + len(kwargs)


@given(valid_definition_str(), non_empty_string(), st.data())
def test_all_field_positions(arg_def, arg_field, data):
    args = extract_args(arg_def)
    kwargs = {k: k for k in data.draw(st.sets(non_empty_string(), min_size=1))}

    assume(arg_field not in args)
    assume(arg_field not in kwargs)
    assume(not any(a in kwargs for a in args))

    actual = Definition(arg_def, arg_field, **kwargs)
    assert len(actual.fields) == len(args) + len(kwargs) + 1


@given(valid_definition_str(), st.shared(non_empty_string(), key="field"), st.data())
def test_kwarg_overwrites_arg_field(arg_def, arg_field, data):
    args = extract_args(arg_def)
    kwargs = {
        k: k
        for k in data.draw(
            st.sets(st.shared(non_empty_string(), key="field"), min_size=1)
        )
    }

    assume(arg_field not in args)
    assume(not any(a in kwargs for a in args))

    actual = Definition(arg_def, arg_field, **kwargs)
    assert len(actual.fields) == len(args) + len(kwargs)


@given(st.dictionaries(non_empty_string(), non_empty_string(), min_size=1))
def test_bad_kwargs(kwargs):
    assume(any(k != v for k, v in kwargs.items()))

    with pytest.raises(ValueError):
        actual = Definition(**kwargs)
