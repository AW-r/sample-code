'''
This program contains the Timer and Memoize function.
'''

import time
from functools import wraps

def Timer(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        start = time.time()
        res = function(*args, **kwargs)
        end = time.time()
        print(f'{function}: {end - start} seconds')
        return res
    return wrapped
# define the Timer function in order to implement it as a decorator.

dict = {}

def Memoize(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        key = (function, str(args), str(kwargs))
        result = dict.get(key)
        if not result:
            dict[key] = function(*args)
        return dict[key]
    return wrapped
