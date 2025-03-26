from typing import Callable
from datetime import datetime as dt
import pandas as pd
from pathlib import Path

HALF_DECK_SIZE = 26
ALL_COMBOS = ["000", "001", "010", "011", "100", "101", "110", "111"]

# defining Path directories
DATA_DIR = Path("data")
TO_LOAD_DIR = DATA_DIR / "to_load"
LOADED_DIR = DATA_DIR / "loaded"
PLOTS_DIR = Path("plots")
LOGS_DIR = Path("logs")

# ensuring directories exist
for directory in [DATA_DIR, TO_LOAD_DIR, LOADED_DIR, PLOTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# defining total counts CSV file path
TOTAL_COUNTS_FILE = Path("testing.csv")  # DATA_DIR /

# creating empty total_counts.csv, if none exists
if not TOTAL_COUNTS_FILE.is_file():
    print(f"{TOTAL_COUNTS_FILE} not found. Creating an empty file...")
    pd.DataFrame(
        columns=[
            "P1_combo",
            "P2_combo",
            "P1_tricks",
            "P2_tricks",
            "P1_cards",
            "P2_cards",
            "trick_tie",
            "card_tie",
        ]
    ).to_csv(TOTAL_COUNTS_FILE, index=False)


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
