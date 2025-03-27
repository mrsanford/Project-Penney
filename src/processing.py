import numpy as np
import pandas as pd
from pathlib import Path
import glob
import os
import re
from src.helpers import (
    TO_LOAD_DIR,
    LOADED_DIR,
    VALID_COMBOS,
    MASTER_CSV_FILE,
    MASTER_CSV_PATH,
)


def get_num_decks(target_dir: Path = LOADED_DIR) -> int:
    """
    Gets the total number of decks that have been processed
    ---
    Args: target_dir (Path) points to loaded folder
    Returns: int value of the total number of decks
    """
    total_decks = 0
    pattern = re.compile(r"processed_(\d+)_decks_.*_part\d+\.npz")
    for file in target_dir.glob("processed_*_decks_*_part*.npz"):
        match = pattern.search(file.name)
        if match:
            total_decks += int(match.group(1))
    return total_decks


def find_seq(decks: str, combo: str, start: int = 0):
    """
    Finds the first occurrence of a combo in the deck
    ---
    Returns: int: index of first occurrence
    """
    if isinstance(decks, np.ndarray):
        decks = "".join(map(str, decks))
    idx = decks.find(combo, start)
    return idx


def score_deck(decks: str, P1_combo: str, P2_combo: str) -> dict:
    """
    Scores a single game and returns combos, trick and card wins
    ---
    Returns: dict: results of a single game (player combos, trick and card wins, and any ties)
    """
    P1_pos = find_seq(decks, P1_combo)
    P2_pos = find_seq(decks, P2_combo)
    # initializing the counters
    P1_cards = P2_cards = 0
    P1_tricks = P2_tricks = 0
    trick_tie = card_tie = 0
    pos = 0
    while P1_pos != -1 and P2_pos != -1:
        if P1_pos == P2_pos:
            continue
        elif P1_pos < P2_pos:
            P1_cards += P1_pos + 3 - pos
            P1_tricks += 1
            pos = P1_pos + 3
        elif P2_pos < P1_pos:
            P2_cards += P2_pos + 3 - pos
            P2_tricks += 1
            pos = P2_pos + 3
        P1_pos = find_seq(decks, P1_combo, pos)
        P2_pos = find_seq(decks, P2_combo, pos)
    # checking for trick and card ties AFTER the game ends
    trick_tie = 1 if P1_tricks == P2_tricks else 0
    card_tie = 1 if P1_cards == P2_cards else 0
    return {
        "P1_combo": P1_combo,
        "P2_combo": P2_combo,
        "P1_tricks": P1_tricks,
        "P2_tricks": P2_tricks,
        "P1_cards": P1_cards,
        "P2_cards": P2_cards,
        "trick_tie": trick_tie,
        "card_tie": card_tie,
    }


def process_decks(decks_str: np.ndarray) -> tuple[dict, dict, dict, dict, int]:
    """
    Processes all decks, scores them, updates total_counts.csv, and summarizes results
    ---
    Args: decks_str (np.ndarray): string representations of decks stored in np.arrays
    Returns: tuple: (DataFrame with detailed scores, number of decks processed)
    """
    # initializing counters and dicts for separate win and tie stats
    trick_wins = {}
    card_wins = {}
    trick_ties = {}
    card_ties = {}
    # generating valid (P1_combo, P2_combo) pairs
    for deck_str in decks_str:
        for P1_combo, P2_combo in VALID_COMBOS:
            score = score_deck(deck_str, P1_combo, P2_combo)
            # initializes combinations if they don't exist in the dict
            if (P1_combo, P2_combo) not in trick_wins:
                trick_wins[(P1_combo, P2_combo)] = {"P1_tricks": 0, "P2_tricks": 0}
                card_wins[(P1_combo, P2_combo)] = {"P1_cards": 0, "P2_cards": 0}
                trick_ties[(P1_combo, P2_combo)] = {"trick_tie": 0}
                card_ties[(P1_combo, P2_combo)] = {"card_tie": 0}
            # accumulating tricks and cards per player
            trick_wins[(P1_combo, P2_combo)]["P1_tricks"] += score["P1_tricks"]
            trick_wins[(P1_combo, P2_combo)]["P2_tricks"] += score["P2_tricks"]
            card_wins[(P1_combo, P2_combo)]["P1_cards"] += score["P1_cards"]
            card_wins[(P1_combo, P2_combo)]["P2_cards"] += score["P2_cards"]
            # incrementing tie counters
            if score["P1_tricks"] == score["P2_tricks"]:
                trick_ties[(P1_combo, P2_combo)]["trick_tie"] += 1
            if score["P1_cards"] == score["P2_cards"]:
                card_ties[(P1_combo, P2_combo)]["card_tie"] += 1
    return trick_wins, card_wins, trick_ties, card_ties


def update_counts(
    trick_wins: dict,
    card_wins: dict,
    trick_ties: dict,
    card_ties: dict,
    master_csv_path: Path = MASTER_CSV_PATH,
    master_csv_file: str = MASTER_CSV_FILE,
) -> pd.DataFrame:
    """
    Updates the master CSV with trick and card win/loss/tie counts
    Note: combos have been encoded as numeric indices
    ---
    Args:
        trick_wins, card_wins, trick_ties, card_ties (dict) contains trick and card wins, trick and card ties
        master_csv_path (Path) to the total_counts.csv
    Returns: pd.DataFrame of the updated dataframe
    """
    combined_data = []
    # collecting all the unique (P1, P2 combo) pairs from all dictionaries
    all_combos = (
        set(trick_wins.keys())
        | set(card_wins.keys())
        | set(trick_ties.keys())
        | set(card_ties.keys())
    )
    for P1_combo, P2_combo in all_combos:
        row = {
            "P1_index": int(P1_combo, 2),
            "P2_index": int(P2_combo, 2),
            "P1_tricks": trick_wins.get((P1_combo, P2_combo), {}).get("P1_tricks", 0),
            "P2_tricks": trick_wins.get((P1_combo, P2_combo), {}).get("P2_tricks", 0),
            "P1_cards": card_wins.get((P1_combo, P2_combo), {}).get("P1_cards", 0),
            "P2_cards": card_wins.get((P1_combo, P2_combo), {}).get("P2_cards", 0),
            "trick_tie": trick_ties.get((P1_combo, P2_combo), {}).get("trick_tie", 0),
            "card_tie": card_ties.get((P1_combo, P2_combo), {}).get("card_tie", 0),
        }
        combined_data.append(row)
    df_new = pd.DataFrame(combined_data)
    column_order = [
        "P1_index",
        "P2_index",
        "P1_tricks",
        "P2_tricks",
        "P1_cards",
        "P2_cards",
        "trick_tie",
        "card_tie",
    ]  # ensuring correct column order
    df_new = df_new[column_order]

    # ensuring master CSV exists
    if master_csv_path.exists():
        df_existing = pd.read_csv(master_csv_file)
        # checking proper column alignment
        missing_columns = set(column_order) - set(df_existing.columns)
        if missing_columns:
            print(f"Warning: Missing columns in existing CSV: {missing_columns}")
        # appending the new data
        df_updated = pd.concat([df_existing, df_new], ignore_index=True)
    else:  # first-time creation
        df_updated = df_new
    # saving to csv
    df_updated.to_csv(master_csv_file, index=False)
    print(f"Successfully updated {master_csv_file} with new results.")
    moving_files()
    return df_updated


def moving_files(
    to_load_dir: Path = TO_LOAD_DIR, loaded_dir: Path = LOADED_DIR
) -> None:
    """
    Moves raw files from TO_LOAD_DIR to LOADED_DIR
    once processed and appends processed tag
    """
    loaded_dir.mkdir(parents=True, exist_ok=True)
    for npz_file in to_load_dir.glob("*.npz"):
        new_filename = npz_file.name.replace("raw_", "processed_")
        target_file = loaded_dir / new_filename
        os.rename(npz_file, target_file)
        print(f"Moved and renamed {npz_file} to {target_file}")
        return None
