from keyword import iskeyword
from string import printable

from hypothesis import assume
from hypothesis import strategies as st

import pyrameters
import utils.decorator


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
def valid_field_names(draw, exclude_names=None):
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

    assume(exclude_names is None or name not in exclude_names)

    # We've tried our best above, which should keep hypothesis generation happy, but
    # just to be safe, let Python decide if the name is an ok identifier.
    assume(name.isidentifier())
    assume(not iskeyword(name))

    # This a comprehensive list of field names we use in the decorator test util.
    # We need to exclude these here so that we don't accidentally overwrite them
    # in the local scope there.
    assume(name not in utils.decorator.RESERVED_NAMES)

    return name


@st.composite
def valid_fields(draw, exclude_names=None):
    """
    Generates valid pyrameters.Field objects.
    """
    name = draw(valid_field_names(exclude_names=exclude_names))
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
        # NaN breaks our equality tests
        st.floats(allow_nan=False),
        st.decimals(allow_nan=False),
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
def unique_field_lists(draw, max_size=20, exclude_fields=None):
    if exclude_fields is None:
        exclude_fields = []
    exclude_fields = set(exclude_fields)

    target_count = draw(st.integers(min_value=1, max_value=max_size))
    fields = []
    while len(fields) < target_count:
        f = draw(valid_fields(exclude_names=exclude_fields | {f.name for f in fields}))
        fields.append(f)

    return fields


@st.composite
def extra_fields(draw, definition_strategy, max_size=10):
    """
    Generates fields with names not in the given definition strategy.
    This is useful for generating new fields to test appending to existing Definitions.
    """
    # This is a shared strategy, so we should get the same fields as the definition
    # generated in the given this is called from.
    definition = draw(definition_strategy)

    # Handle both Definition and string-based
    if isinstance(definition, str):
        fields = [x.strip() for x in definition.split(",")]
    else:
        fields = [f for f in definition.fields]

    return draw(unique_field_lists(max_size=max_size, exclude_fields=fields))


@st.composite
def valid_definitions(draw, max_size=20):
    """
    Generates valid pyrameters.Definition objects, with at least one field, with or
    without default values,factories.

    Reduces on number of fields and whether they do or don't have defaults.
    """
    return pyrameters.Definition(*list(draw(unique_field_lists(max_size=max_size))))


@st.composite
def valid_definition_strings(draw, max_size=20, exclude_fields=None):
    """
    Generates definition strings (with field named) that contain at most
    max_size number of fields.
    """
    fields = draw(
        st.sets(
            valid_field_names(exclude_names=exclude_fields),
            min_size=1,
            max_size=max_size,
        )
    )

    if exclude_fields is not None:
        assume(not fields & set(exclude_fields))

    return ",".join(list(fields))


@st.composite
def valid_combination_definitions(draw, max_size=20, exclude_fields=None):
    """
    Generates combination definitions, which have a normal definition string
    a la @pytest.mark.parametrize, followed by one or more field overrides.
    """
    assert max_size > 1

    # This must leave room for at least one overriding field.
    base_definition = draw(
        valid_definition_strings(max_size=max_size - 1, exclude_fields=exclude_fields)
    )
    new_fields = [x.strip() for x in base_definition.split(",")]
    if exclude_fields is None:
        exclude_fields = []
    else:
        exclude_fields = list(exclude_fields)
    exclude_fields.extend(new_fields)

    field_count = len(new_fields)
    overrides = draw(
        unique_field_lists(
            max_size=max_size - field_count, exclude_fields=exclude_fields
        )
    )
    return pyrameters.Definition(base_definition, *list(overrides))


@st.composite
def valid_overridden_definitions(draw, max_size=20, exclude_fields=None):
    """
    Generates Defintions with field overrides.
    ie: Definition(Definition(...), Field(...), Field(...), ...)
    """
    assert max_size > 1

    definition = draw(
        valid_definitions(max_size=max_size - 1, exclude_fields=exclude_fields)
    )
    # Don't pass any exclude fields. This allows the following strategy to include both
    # added fields and overridden fields.
    new_fields = {
        f.name: f
        for f in draw(unique_field_lists(max_size=max_size - len(definition.fields)))
    }

    return pyrameters.Definition(definition, **new_fields)


@st.composite
def any_style_definitions(draw, max_size=20):
    return draw(
        st.one_of(
            valid_definition_strings(max_size=max_size),
            valid_definitions(max_size=max_size),
            valid_combination_definitions(max_size=max_size),
            valid_overridden_definitions(max_size=max_size),
        )
    )


@st.composite
def cases_for(
    draw,
    definition_strategy,
    min_count=1,
    max_count=10,
    tuples=True,
    mappings=None,
    use_defaults=None,
):
    """
    Generates cases to run through the decorator based on the fields in the given
    definition.
    """
    # This is a shared strategy, so we should get the same fields as the definition
    # generated in the given this is called from.
    definition = draw(definition_strategy)

    # Allow mappings if the definition can have defaults and the caller didn't
    # explicitly request otherwise.
    if mappings is None and isinstance(definition, pyrameters.Definition):
        mappings = True

    assert tuples or mappings, "One of tuples or mappings must be True"

    # Handle both Definition and string-based
    if isinstance(definition, str):
        fields = [x.strip() for x in definition.split(",")]
    else:
        fields = definition.fields

    generated = []
    count = draw(st.integers(min_value=min_count, max_value=max_count))
    for _ in range(count):
        # Choose Mapping or tuple version of field values
        should_tuple = tuples
        if tuples and mappings:
            should_tuple = draw(st.booleans(), label="should_tuple")
        should_mapping = not should_tuple

        if should_tuple:
            generated.append(tuple(draw(field_values(), label=f) for f in fields))

        elif should_mapping:

            def should_default(f):
                # Whether or not we should rely on defaults is a little complicated.
                # To allow exception flow testing, we need to passthrough the kwarg
                # when it's provided.
                # Otherwise, we should only rely on a default value if the definition
                # is the correct type, the default exists, and we draw a True from
                # hypothesis.
                if use_defaults is not None:
                    return use_defaults
                return (
                    isinstance(definition, pyrameters.Definition)
                    and fields[f].default[1]
                    and draw(st.booleans(), label="should_default")
                )

            generated.append(
                {
                    f: draw(field_values(), label=f)
                    for f in fields
                    if not should_default(f)
                }
            )

    # Make sure that we pass values without the wrapping tuple when parametrizing
    # a single field.
    if len(fields) == 1:
        generated = [g[0] if isinstance(g, tuple) else g for g in generated]

    return generated
