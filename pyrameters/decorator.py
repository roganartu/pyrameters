from typing import Any, Sequence, Tuple, Union

import pytest

from pyrameters.types.case import Case
from pyrameters.types.definition import Definition


def test_cases(
    argnames: Union[str, Definition],
    argvalues: Sequence[Union[Any, Tuple[Any], Case]],
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
    argvalues : Sequence[Union[Any, Tuple[Any], Case]]
        Accepts any of the following:
            - If argnames only contains a single argument, then it is either a list of
              values (one per test case) eg: `["input_val1", "input_val2", ...], or a
              list of pyrameters.Case objects describing a test case eg:
              `[pyrameters.Case(foo="bar"), pyrameters.Case(...), ...]`
              The latter case isn't really that useful here, as it is more verbose
              than the former without any benefits when only using a single argument.
            - If argnames contains more than one argument, then it is a list of either
              tuples the same length as the number of arguments eg:
              `[("val1", "val2"), ("val3", "val4")]`, or a list of pyrameters.Case eg:
              `[pyrameters.case(foo="val1", bar="val2", ...]`.
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
    # TODO build argstring
    # TODO build arg list
    # TODO pass built argstring and arglist to parametrize
    def wrapper(f):
        return pytest.mark.parametrize(
            argnames, argvalues, indirect=indirect, ids=ids, scope=scope
        )(f)

    return wrapper
