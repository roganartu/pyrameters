"""
Definition represents the definition of a pyrameters test, by which each provided
Case must adhere.
"""

from pyrameters.types.field import Field

# TODO setup logging

_NAMELESS_FIELD_ERROR = (
    "Nameless Field passed as arg to Definition. "
    "Add a name or pass it as a kwarg instead: {}"
)

_UNSUPPORTED_TYPE_ERROR = "Unsupported type. Expected str or pyrameters.Field, got {}"


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
                self.fields = dict(args[0].fields)

            else:
                skip_first_arg = False

            for i, arg in enumerate(args):
                if skip_first_arg and i == 0:
                    continue

                if isinstance(arg, str):
                    self.fields[arg] = Field.empty(name=arg)
                elif isinstance(arg, Field):
                    if not arg.name:
                        raise ValueError(_NAMELESS_FIELD_ERROR.format(arg))
                    if arg.name in self.fields:
                        raise ValueError('Duplicate field name "{}"'.format(arg.name))
                    self.fields[arg.name] = arg
                else:
                    raise TypeError(_UNSUPPORTED_TYPE_ERROR.format(type(arg)))

        for key, arg in kwargs.items():
            if key in self.fields:
                # TODO log warning
                pass

            if isinstance(arg, str):
                self.fields[key] = Field.empty(name=arg)
            elif isinstance(arg, Field):
                self.fields[key] = arg
            else:
                raise TypeError(_UNSUPPORTED_TYPE_ERROR.format(type(arg)))
