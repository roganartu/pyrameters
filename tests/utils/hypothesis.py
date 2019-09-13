from string import printable

from hypothesis import assume
from hypothesis import strategies as st

import pyrameters


def everything_except(*args):
    """
    Hypothesis helper for generating values of any type except the given ones.
    """
    return (
        st.from_type(type)
        .flatmap(st.from_type)
        .filter(lambda x: not isinstance(x, args))
    )


def non_empty_strings():
    return st.text(printable).filter(lambda x: x.strip())


@st.composite
def valid_field_names(draw):
    """
    Generates valid field names, which are the same as valid Python identifier names.

    These are documented here:
    https://docs.python.org/3.3/reference/lexical_analysis.html#identifiers
    """
    ok_chars = list("_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    numbers = list("0123456789")
    first_char = draw(st.sampled_from(ok_chars))
    remaining_chars = draw(st.lists(st.sampled_from(ok_chars + numbers), max_size=1000))
    name = "{}{}".format(first_char, "".join(remaining_chars))

    # We've tried our best above, which should keep hypothesis generation happy, but
    # just to be safe, let Python decide if the name is an ok identifier.
    assume(name.isidentifier())

    return name


@st.composite
def valid_fields(draw, exclude_names=None):
    """
    Generates valid pyrameters.Field objects.
    """
    name = draw(valid_field_names())
    assume(exclude_names is None or name not in exclude_names)
    should_default = draw(st.booleans())
    should_factory = draw(st.booleans())

    default = pyrameters.types.field.defaultValues.NO_DEFAULT
    factory = None
    if should_default:
        # Make sure we don't have both a factory and a static default val
        if not should_factory:
            default = draw(field_values())
        else:
            # Can't create factories, they break a bunch of things in the hypothesis
            # tests still.
            # TODO fix these
            # factory = draw(st.functions(like=(lambda: None), returns=field_values()))
            pass

    return pyrameters.Field(name, default=default, factory=factory)


def field_values():
    return st.one_of(
        st.none(),
        st.booleans(),
        st.integers(),
        st.floats(),
        st.decimals(),
        st.dates(),
        st.times(),
        st.datetimes(),
        st.timedeltas(),
        st.text(printable),
    )


@st.composite
def valid_json(draw, max_leaves=10):
    return draw(
        st.recursive(
            st.none() | st.booleans() | st.floats() | st.text(printable),
            lambda children: st.lists(children, 1)
            | st.dictionaries(st.text(printable), children, min_size=1),
            max_leaves=max_leaves,
        )
    )


@st.composite
def valid_definitions(draw, max_size=20):
    """
    Generates valid pyrameters.Definition objects, with at least one field, with or
    without default values,factories.

    Reduces on number of fields and whether they do or don't have defaults.
    """
    fields = list(draw(st.sets(valid_fields(), min_size=1, max_size=20)))

    # Make sure we have no dupes.
    # For some reason drawing from `st.sets` above doesn't work, even if we define
    # Field.__hash__ to simple return hash(f.name).
    field_names = set(f.name for f in fields)
    assume(len(field_names) == len(fields))

    return pyrameters.Definition(*list(fields))
