from hypothesis import strategies as st


def everything_except(*args):
    """
    Hypothesis helper for generating values of any type except the given ones.
    """
    return (
        st.from_type(type)
        .flatmap(st.from_type)
        .filter(lambda x: not isinstance(x, args))
    )


def non_empty_string():
    return st.text().filter(lambda x: x.strip())
