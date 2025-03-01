from typing import Callable
from datetime import datetime as dt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
PLOTS_DIR = BASE_DIR / "plots"
LOGS_DIR = BASE_DIR / "logs"

LATEST_RESULTS_FILE = RESULTS_DIR / "testing.csv"
LATEST_DECK_FILE_PATTERN = DATA_DIR / "shuffled_decks_*.npz"


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
