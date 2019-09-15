from collections.abc import Mapping
from typing import Any, Mapping, Sequence, Tuple, Union

import pytest

from pyrameters.types.definition import Definition


def test_cases(
    argnames: Union[str, Definition],
    argvalues: Sequence[Union[Any, Tuple[Any], Mapping]],
    indirect: Union[bool, Sequence[str]] = False,
    ids=None,
    scope=None,
):
    """
    Add new invocations to the underlying test function according to argnames and
    argvalues.

    This is a drop-in replacement for @pytest.mark.parametrize that adds extra features.

    It builds tests cases based on the arguments it receives, and passes them directly
    to @pytest.mark.parametrize which handles the actual parametrization.

    Parameters
    ----------
    argnames : Union[str, pyrameters.Definition]
        When a string value it is identical to @pytest.mark.parametrize(argnames, ...).
        Otherwise, a pyrameters.Definition describing the test case parameters accepted
        by the wrapped function, including any defaults or default factories etc.
    argvalues : Sequence[Union[Any, Tuple[Any], Mapping]]
        Accepts any of the following:
            - If argnames only contains a single argument, then it is either a list of
              values (one per test case) eg: `["input_val1", "input_val2", ...], or a
              list of collection.ABC.Mapping objects describing a test case eg:
              `[{"foo": "bar"}, {...}, ...]`
              The latter case isn't really that useful here, as it is more verbose
              than the former without any benefits when only using a single argument.
            - If argnames contains more than one argument, then it is a list of either
              tuples the same length as the number of arguments eg:
              `[("val1", "val2"), ("val3", "val4")]`, or a list of Mappings eg:
              `[dict(foo="val1", bar="val2"), ...]`.
    indirect : Union[bool, Sequence[str]] = False
        Passed through to @pytest.mark.parametrize unchanged. See pytest documentation
        for usage.
    ids = None
        Passed through to @pytest.mark.parametrize unchanged. See pytest documentation
        for usage.
    scope = None
        Passed through to @pytest.mark.parametrize unchanged. See pytest documentation
        for usage.
    """
    # Figure out the pytest.mark.parametrize-compatible list of args to pass
    if isinstance(argnames, str):
        definition_str = argnames
    elif isinstance(argnames, Definition):
        definition_str = str(argnames)

    # Build arg list, falling back to defaults where necessary
    # TODO add Groups that change namespacing, allowing you to have groups of defaults.
    #   eg: Group(x="1")(
    #           dict(y="2"),
    #           dict(x="3", y="4"),
    #       )
    #   would generate [("1", "2"), ("3", "4")]
    arglist = []
    for case_vals in argvalues:
        if not isinstance(argnames, Definition) or not isinstance(case_vals, Mapping):
            arglist.append(case_vals)
            continue

        # Check all the fields in the definition against the fields in the mapping,
        # Falling back to defaults where they are missing from the provided mapping.
        case = []
        for name, f in argnames.fields.items():
            # Can't use `.get` here because we won't know whether the returned val is
            # from our default, or whether it was the actual value.
            # Doing it this way allows a defaultdict provided as a test case to
            # override a Definition default. This is a weird use case, but logically
            # it makes sense to support.
            # TODO could use a custom type (like an enum) as the default value to
            # achieve this instead.
            use_default = True
            try:
                val = case_vals[name]
                use_default = False
            except KeyError:
                # Don't do the check for a default in here, otherwise we get a
                # nested exception which isn't a great experience for the user.
                pass
            if use_default:
                val, ok = f.default
                if not ok:
                    raise ValueError(
                        (
                            "No value provided for {key} in test case {} for test "
                            "function {}, and test case definition has no default. "
                            "Either define a default, or add a value for {key} to the "
                            "test case."
                        ).format(case_vals, f, key=name)
                    )
            case.append(val)
        arglist.append(tuple(case) if len(argnames.fields) > 1 else case[0])

    # This requires:
    # For each value:
    #    if it's not of type Mapping, just pass as-is.
    #    if it's of type Mapping then figure out whether it needs any defaults populated
    #    pass resulting cases on
    # TODO create tests for the above cases, with hypothesis magic.

    def wrapper(f):
        return pytest.mark.parametrize(
            definition_str, arglist, indirect=indirect, ids=ids, scope=scope
        )(f)

    return wrapper
