import numpy as np
from typing import Callable
from datetime import datetime as dt
from pathlib import Path

R, B = 0, 1  # Red and Black
HALF_DECK_SIZE = 26  # this can be changed
# there are 8 possible P1 combos
ALL_COMBOS = np.array(
    [
        (R, R, R),
        (R, R, B),
        (R, B, R),
        (R, B, B),
        (B, R, R),
        (B, R, B),
        (B, B, R),
        (B, B, B),
    ],
    dtype=object,
)

# Defining the directories
DATA_DIR = Path("data")
TO_LOAD_DIR = Path(DATA_DIR / "to_load")
LOADED_DIR = Path(DATA_DIR / "loaded")
PLOTS_DIR = Path("plots")
LOGS_DIR = Path("logs")

# Ensuring the directories exist
for directory in [DATA_DIR, TO_LOAD_DIR, LOADED_DIR, PLOTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Defining the file paths
TOTAL_COUNTS_FILE = DATA_DIR / "total_counts.csv"
LATEST_TO_LOAD_FILE = TO_LOAD_DIR / "raw_shuffled_decks_*.npz"


# Debugger Decorator
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
