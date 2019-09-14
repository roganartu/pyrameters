import dill as pickle


def run_in_decorator(testdir, definition, cases):
    """
    Run the test through the decorator, calling a mock
    We can use the pytest testdir fixture to run a dynamically generated Python test
    file, and then assert the number of lines in the output is the number of cases we
    expected to run.
    The easiest way to achieve this is to simply pickle the fn variable, and then
    unpickle it into a function with the test_ prefix.
    TODO this fails to serialize fields that have a factory
    TODO pull this into a separate helper function that takes a definition and some
    cases and returns the result of running them.
    We need this for more than just this test case, no reason to duplicate it.
    """
    pickled_def = pickle.dumps(definition)
    pickled_cases = pickle.dumps(cases)
    return testdir.inline_runsource(
        """
        import dill as pickle
        import pytest

        import pyrameters

        definition = pickle.loads({})
        cases = pickle.loads({})

        @pyrameters.test_cases(definition, cases)
        def test_nested({}):
            assert True
    """.format(
            pickled_def, pickled_cases, str(definition)
        ),
        "-qq",
    )
