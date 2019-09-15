import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from pyrameters import Definition, Field
from utils.hypothesis import (everything_except, extra_fields,
                              non_empty_strings, valid_definition_strings)


def extract_args(arg_def):
    return [x.strip() for x in arg_def.split(",") if x.strip()]


@given(valid_definition_strings())
@settings(max_examples=settings().max_examples * 10)
def test_str_args(arg_def):
    actual = Definition(arg_def)
    assert len(actual.fields) == len(extract_args(arg_def))


@given(
    st.shared(valid_definition_strings(), key="with_kwargs"),
    extra_fields(st.shared(valid_definition_strings(), key="with_kwargs"), max_size=10),
)
@settings(max_examples=settings().max_examples * 10)
def test_with_kwargs(arg_def, extra_fields):
    kwargs = {f.name: f for f in extra_fields}
    actual = Definition(arg_def, **kwargs)
    assert len(actual.fields) == len(extract_args(arg_def)) + len(kwargs)


@given(
    st.shared(valid_definition_strings(), key="all_pos"),
    extra_fields(st.shared(valid_definition_strings(), key="all_pos"), max_size=10),
    st.data(),
)
@settings(max_examples=settings().max_examples * 10)
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
    st.shared(valid_definition_strings(), key="overwrites"),
    extra_fields(st.shared(valid_definition_strings(), key="overwrites"), max_size=10),
    st.data(),
)
@settings(max_examples=settings().max_examples * 10)
def test_kwarg_overwrites_arg_field(arg_def, extra_fields, data):
    kwargs = {f.name: f for f in extra_fields}
    i = data.draw(st.integers(min_value=0, max_value=len(extra_fields) - 1))
    arg_field = extra_fields[i].name

    actual = Definition(arg_def, arg_field, **kwargs)
    assert len(actual.fields) == len(extract_args(arg_def)) + len(extra_fields)


@given(
    st.dictionaries(
        # This usage of shared may seem unintuitive, but in practice it appears to cut
        # the number of invalid examples that the `assume` in the first line of the test
        # func identifies by approximately half (from ~500 invalids to ~200-250).
        # This improves generation speed a little.
        st.shared(non_empty_strings(), key="a"),
        st.shared(non_empty_strings(), key="b"),
        min_size=1,
    )
)
@settings(max_examples=settings().max_examples * 10)
def test_bad_kwargs(kwargs):
    assume(any(k != v for k, v in kwargs.items()))

    with pytest.raises(ValueError):
        actual = Definition(**kwargs)
