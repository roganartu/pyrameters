import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from pyrameters import Definition, Field
from utils.hypothesis import (everything_except, extra_fields,
                              non_empty_strings, valid_definition_strings)


def extract_args(arg_def):
    return [x.strip() for x in arg_def.split(",") if x.strip()]


@given(valid_definition_strings())
def test_str_args(arg_def):
    actual = Definition(arg_def)
    assert len(actual.fields) == len(extract_args(arg_def))


@given(
    st.shared(valid_definition_strings(), key="with_kwargs"),
    extra_fields(st.shared(valid_definition_strings(), key="with_kwargs"), max_size=10),
)
def test_with_kwargs(arg_def, extra_fields):
    kwargs = {f.name: f for f in extra_fields}
    actual = Definition(arg_def, **kwargs)
    assert len(actual.fields) == len(extract_args(arg_def)) + len(kwargs)


@given(
    st.shared(valid_definition_strings(), key="all_pos"),
    extra_fields(st.shared(valid_definition_strings(), key="all_pos"), max_size=10),
    st.data(),
)
def test_all_field_positions(arg_def, extras, data):
    args = []
    kwargs = {}
    for f in extras:
        if data.draw(st.booleans(), label="as_arg"):
            args.append(f.name)
        else:
            kwargs[f.name] = f

    actual = Definition(arg_def, *args, **kwargs)
    assert len(actual.fields) == len(extract_args(arg_def)) + len(extras)


@given(
    valid_definition_strings(), st.shared(non_empty_strings(), key="field"), st.data()
)
def test_kwarg_overwrites_arg_field(arg_def, arg_field, data):
    args = extract_args(arg_def)
    kwargs = {
        k: k
        for k in data.draw(
            st.sets(st.shared(non_empty_strings(), key="field"), min_size=1)
        )
    }

    assume(arg_field not in args)
    assume(not any(a in kwargs for a in args))

    actual = Definition(arg_def, arg_field, **kwargs)
    assert len(actual.fields) == len(args) + len(kwargs)


@given(st.dictionaries(non_empty_strings(), non_empty_strings(), min_size=1))
def test_bad_kwargs(kwargs):
    assume(any(k != v for k, v in kwargs.items()))

    with pytest.raises(ValueError):
        actual = Definition(**kwargs)
