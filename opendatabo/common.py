from typing import Type, Callable

import time


class DataNotAvailableException(Exception):
    pass


def retry_on(exception_type: Type, retries: int = 1, delay: Callable[[int], float] = lambda i: 0.0):
    if retries < 0:
        raise ValueError('retries >= 0')

    def wrapper(func):
        def wrapped(*args, **kwargs):
            culprit = None
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except exception_type as e:
                    t = delay(i)
                    time.sleep(t)
                    culprit = e
                    continue
            raise culprit

        return wrapped

    return wrapper
