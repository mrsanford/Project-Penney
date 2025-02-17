from typing import Callable
from datetime import datetime as dt

# consider putting all the path information in a dictionary so its easily accessible by key?
# PATH_INFO = {PATH_DATA:'Users/michellesanford/Documents/Github/Project-Penney/data',
#             PATH_FIGURES:'Users/michellesanford/Documents/Github/Project-Penney/figures'}

def debugger_factory(show_args=True) -> Callable:
    def debugger(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            if show_args:
                print(f"{func.__name__} was called with:")
                print("Positional arguments:\n", args)
                print("Keyword arguments:\n", kwargs)
            t0 = dt.now()
            results = func(*args, **kwargs)
            print(f"{func.__name__} ran for {dt.now() - t0}")
            return results
        return wrapper
    return debugger