import dill as pickle

RESERVED_NAMES = {
    "Mapping",
    "pickle",
    "pytest",
    "pyrameters",
    "definition",
    "cases",
    "ω",
    "test_nested",
    "assert_msg",
    "fields",
    "f",
    "expected_val",
    "i",
}


def run_in_decorator(testdir, definition, cases):
    """
    Run the test through the decorator, calling a mock
    We can use the pytest testdir fixture to run a dynamically generated Python test
    file, and then assert the number of lines in the output is the number of cases we
    expected to run.
    The easiest way to achieve this is to simply pickle the fn variable, and then
    unpickle it into a function with the test_ prefix.
    We need this for more than just this test case, no reason to duplicate it.

    TODO this fails to serialize fields that have a factory
    """
    pickled_def = pickle.dumps(definition)
    pickled_cases = pickle.dumps(cases)
    return testdir.inline_runsource(
        """
        from collections.abc import Mapping
        import dill as pickle
        import pytest

        import pyrameters

        definition = pickle.loads({})
        cases = pickle.loads({})

        # Global counter, to allow us to easily access the current case
        # being executed via the cases var.
        # Needs to be a non alphanumeric char that is still a valid Python identifier
        # so that we can be sure it isn't overwritten by one of the args passed in.
        # Hypothesis is annoyingly good at finding these cases.
        ω = 0

        @pyrameters.test_cases(definition, cases)
        def test_nested({}):
            global ω
            assert_msg = "Case value for var {{}} does not match. Broken arg ordering?"
            try:
                if isinstance(definition, str):
                    fields = [x.strip() for x in definition.split(",")]
                else:
                    fields = list(definition.fields.keys())

                # Don't need to assert that cases is the right length, as this test
                # body will never be executed by pytest if that is incorrect.

                # No defaults, and there's only one field so there's no wrapping tuple:
                if len(fields) == 1:
                    f = fields[0]
                    expected_val = cases[ω].get(f, definition.fields[f].default[0]) if isinstance(cases[ω], Mapping) else cases[ω]
                    assert locals()[f] == expected_val, assert_msg.format(f)

                # No defaults, need to unwrap tuples
                elif len(fields) == len(cases[ω]):
                    for i, f in enumerate(fields):
                        expected_val = cases[ω][f] if isinstance(cases[ω], Mapping) else cases[ω][i]
                        assert locals()[f] == expected_val, assert_msg.format(f)

                # Fields doesn't match count, need to check defaults.
                else:
                    for f in fields:
                        expected_val = cases[ω].get(f, definition.fields[f].default[0])
                        assert locals()[f] == expected_val, assert_msg.format(f)

            finally:
                ω += 1
    """.format(
            pickled_def, pickled_cases, str(definition)
        ),
        "-qq",
    )
