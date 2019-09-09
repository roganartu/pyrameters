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
                # Perhaps surprisingly, this isn't as intelligent as I expected.
                # I initially expected this to support complex CSV (eg: quoted fields),
                # but looking at the pytest source revealed it only supports basic
                # CSV and makes no attempt to do anything but strip whitespace:
                # https://github.com/pytest-dev/pytest/blob/8ccc0177c8be85c0725981b3a9e867baeebfbe33/src/_pytest/mark/structures.py#L97-L104
                # Oh well, makes life easier here!
                argnames = [x.strip() for x in args[0].split(",") if x.strip()]
                for arg in argnames:
                    self.fields[arg] = Field.empty(name=arg)

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
                # TODO log warning that an arg field is being overidden by a kwarg one.
                pass

            if isinstance(arg, str):
                self.fields[key] = Field.empty(name=arg)
            elif isinstance(arg, Field):
                self.fields[key] = arg
            else:
                raise TypeError(_UNSUPPORTED_TYPE_ERROR.format(type(arg)))

        if not self.fields:
            raise ValueError("No fields provided")
