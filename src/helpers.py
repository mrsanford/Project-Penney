from typing import Callable
from datetime import datetime as dt
from pathlib import Path
import pandas as pd

R, B = 0, 1  # Red and Black
HALF_DECK_SIZE = 26  # this can be changed
# there are 8 possible P1 combos
ALL_COMBOS = ["000", "001", "010", "011", "100", "101", "110", "111"]

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
if not TOTAL_COUNTS_FILE.exists():
    print(f"{TOTAL_COUNTS_FILE} not found. Creating an empty file...")
    pd.DataFrame(
        columns=[
            "P1_combo",
            "P2_combo",
            "P1_tricks",
            "P2_tricks",
            "P1_cards",
            "P2_cards",
            "trick_draw",
            "card_draw",
        ]
    ).to_csv(TOTAL_COUNTS_FILE, index=False)
LATEST_TO_LOAD_FILE = TO_LOAD_DIR / "raw_shuffled_decks_*.npz"


# Debugger Decorator
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
