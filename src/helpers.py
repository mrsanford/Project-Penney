from typing import Callable
from datetime import datetime as dt

# Constants
ALL_COMBOS = ['000', '001', '010', '011', '100', '101', '110', '111']
HALF_DECK_SIZE = 26
PATH_DATA_DECKS = 'data/decks'
PATH_DATA_SEEDS = 'data/seeds'
PATH_DATA = 'data'
PATH_PLOTS = 'plots'

# debugger decorator
def debugger_factory(show_args=True) -> Callable:
    def debugger(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            if show_args:
                print(f"{func.__name__} was called with:")
                print("Positional Args:\n", args)
                print("Keyword Args:\n", kwargs)
            t0 = dt.now()
            results = func(*args, **kwargs)
            print(f"{func.__name__} ran for {dt.now() - t0}")
            return results
        return wrapper
    return debugger