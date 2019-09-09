"""
Definition represents the definition of a pyrameters test, by which each provided
Case must adhere.
"""

from pyrameters.types.field import Field

# TODO setup logging


class Definition(object):
    __slots__ = ("fields",)

    def __init__(self, *args, **kwargs):
        self.fields = {}

        if args:
            skip_first_arg = True

            if isinstance(args[0], str):
                # pytest.mark.parametrize-style field definition.
                # Looks like:
                #     "foo,bar,baz"
                # Contains no other information.
                # TODO create a blank field for each, with no type and no default.
                # TODO find out how pytest.mark.parametrize handles whitespace and
                # quotes etc, and do it identically.
                pass

            elif isinstance(args[0], self.__class__):
                # User passed a definition directly. Swap out the fields and
                # continue processing to allow overrides.
                # eg:
                #    Definition(Definition("foo,bar"), foo=Field(...))
                # should override foo from the inner Definition with foo from the kwarg.
                # TODO this
                pass

            else:
                skip_first_arg = False

            for i, arg in enumerate(args):
                if skip_first_arg and i == 0:
                    continue

                # TODO check if it's a field or a string.
                # If it's a string, create an empty arg.
                # If it's a field, just store it in the fields dict.

        for key, arg in kwargs.items():
            # TODO check if it's a field or a string.
            # If it's a string, create an empty arg.
            # If it's a field, just store it in the fields dict.
            pass
