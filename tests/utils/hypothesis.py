from hypothesis.strategies import from_type


def everything_except(*args):
    """
    Hypothesis helper for generating values of any type except the given ones.
    """
    return from_type(type).flatmap(from_type).filter(lambda x: not isinstance(x, args))
