from typing import Callable
from datetime import datetime as dt
import pandas as pd
from pathlib import Path

HALF_DECK_SIZE = 26
ALL_COMBOS = ["000", "001", "010", "011", "100", "101", "110", "111"]
VALID_COMBOS = [
    (P1_combo, P2_combo)
    for P1_combo in ALL_COMBOS
    for P2_combo in ALL_COMBOS
    if P1_combo != P2_combo
]

# defining Path directories
DATA_DIR = Path("data")
TO_LOAD_DIR = DATA_DIR / "to_load"
LOADED_DIR = DATA_DIR / "loaded"
MASTER_CSV_PATH = DATA_DIR / "total_counts"
PLOTS_DIR = Path("plots")
LOGS_DIR = Path("logs")
USED_SEEDS = Path(DATA_DIR / "used_seeds")

# ensuring directories exist
for directory in [DATA_DIR, TO_LOAD_DIR, LOADED_DIR, PLOTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# string representations of paths
MASTER_CSV_FILE = "./data/total_counts/total_counts.csv"

# defining total counts CSV file path
TOTAL_COUNTS_FILE = MASTER_CSV_PATH / "total_counts.csv"
TOTAL_COUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
if not TOTAL_COUNTS_FILE.exists():
    print(f"{TOTAL_COUNTS_FILE} not found. Creating new file...")
    # Define the columns for the CSV file
    columns = [
        "P1_index",
        "P2_index",
        "P1_tricks",
        "P2_tricks",
        "P1_cards",
        "P2_cards",
        "trick_tie",
        "card_tie",
    ]
    # create and write to empty DataFrame with the defined columns
    df = pd.DataFrame(columns=columns)
    df.to_csv(TOTAL_COUNTS_FILE, index=False)
    print(f"{TOTAL_COUNTS_FILE} created successfully!")
else:
    print(f"{TOTAL_COUNTS_FILE} already exists.")


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
