from itertools import count

import pytest

from opendatabo.common import retry_on


def test_retry_on_basic():
    raise_count = count()

    @retry_on(KeyError, retries=5)
    def subject(a, b):
        assert a == 1
        assert b == 2
        if next(raise_count) < 4:
            raise KeyError()
        return a + b

    r = subject(1, 2)

    assert next(raise_count) == 5
    assert r == 3


def test_retry_on_different_type():
    raise_count = count()

    @retry_on(KeyError, retries=5)
    def subject():
        next(raise_count)
        raise ValueError

    with pytest.raises(ValueError):
        r = subject()

        assert next(raise_count) == 1
        assert r == 3
