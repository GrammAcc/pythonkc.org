from contextlib import contextmanager

import pytest


@contextmanager
def does_not_raise(exception):
    """The opposite of `pytest.raises`."""

    try:
        yield
    except exception:
        raise pytest.fail("Raised {0}".format(exception))
