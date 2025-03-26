import numpy as np
import pandas as pd
from pathlib import Path
import glob
import os
from src.helpers import ALL_COMBOS, TO_LOAD_DIR


def load_decks():
    """
    Loads all shuffled deck files from the 'to_load' directory
    ---
    Args: None
    Returns: None
    """
    files = [file for file in Path(TO_LOAD_DIR).glob("*.npz")]
    if not files:
        print("No new decks to process.")
        return []
    return [np.load(file)["decks_str"] for file in files]


def find_seq(decks_str: str, combo: str, start: int = 0):
    """
    Finds the first occurrence of a combo in the deck
    ---
    Args:
        deck (str): the shuffled deck of cards as a string
        combo (str): the pattern to search for (e.g., "000")
        start (int): the index of the first position to search
    Returns:
        tuple: (index of first occurrence, total count)
    """
    if isinstance(decks_str, np.ndarray):
        decks_str = "".join(map(str, decks_str))
    idx = decks_str.find(combo, start)
    return idx


def score_deck(deck_str: str, P1_combo: str, P2_combo: str) -> list:
    """
    Scores a single deck by checking every P1 vs P2 combination.
    ---
    Args:
        deck (str): the shuffled deck of cards.
        P1_combo (str): the string representation of P1_combo
        P2_combo (str): the string representation of P2_combo
    Returns:
        list: Results containing player combos, trick and card wins, and ties.
    """
    P1_pos = find_seq(deck_str, P1_combo)
    P2_pos = find_seq(deck_str, P2_combo)
    # initialize the counters
    P1_cards = P2_cards = 0
    P1_tricks = P2_tricks = 0
    trick_tie = card_tie = 0
    pos = 0
    while P1_pos != -1 and P2_pos != -1:
        if P1_pos < P2_pos:
            P1_cards += P1_pos + 3 - pos
            P1_tricks += 1
            pos = P1_pos + 3
        elif P2_pos < P1_pos:
            P2_cards += P2_pos + 3 - pos
            P2_tricks += 1
            pos = P2_pos + 3
        P1_pos = find_seq(deck_str, P1_combo, pos)
        P2_pos = find_seq(deck_str, P2_combo, pos)
    if P1_tricks == P2_tricks:  # check for trick ties
        trick_tie += 1
    if P1_cards == P2_cards:  # check for card ties after all tricks are counted
        card_tie += 1
    return (
        P1_combo,
        P2_combo,
        P1_tricks,
        P2_tricks,
        P1_cards,
        P2_cards,
        trick_tie,
        card_tie,
    )


def process_decks(decks_str: np.ndarray):
    """
    Processes all decks, scores them, updates total_counts.csv, and moves files
    ---
    Args:
        decks_str (np.ndarray): string representations of decks stored in np arrays
    """
    scores = []
    for deck_str in decks_str:
        for P1_combo in ALL_COMBOS:
            for P2_combo in ALL_COMBOS:
                if P1_combo != P2_combo:
                    score = score_deck(deck_str, P1_combo, P2_combo)
                    scores.append(score)
    df_scores = pd.DataFrame(  # convert the output to dataframe
        scores,
        columns=[
            "P1_combo",
            "P2_combo",
            "P1_tricks",
            "P2_tricks",
            "P1_cards",
            "P2_cards",
            "trick_tie",
            "card_tie",
        ],
    )
    return df_scores


def update_counts(
    df_scores: pd.DataFrame,
    master_csv_file: str = "testing.csv",
    to_load_dir="data/to_load",
    loaded_dir="data/loaded",
) -> None:
    """
    Updates a master CSV file with the output df_scores from process_decks.
    Aggregates trick, card, and tie counts while keeping the combos constant.
    ---
    Args:
        df_scores (pd.DataFrame): contains the new scores from process_decks
        master_csv_file (str): the CSV file to update
    Returns: None
    """
    if not isinstance(master_csv_file, str):  # ensuring master_csv_file is a valid path
        raise ValueError(f"Expected a file path string, got: {type(master_csv_file)}")
    if not isinstance(
        df_scores, pd.DataFrame
    ):  # ensuring df_scores is a dataframe object
        raise ValueError(f"Expected a DataFrame for df_scores, got: {type(df_scores)}")

    # IMPORTANT in preventing the string combinations from not returning a 3-bit length
    df_scores["P1_combo"] = df_scores["P1_combo"].apply(lambda x: f"{int(x, 2):03b}")
    df_scores["P2_combo"] = df_scores["P2_combo"].apply(lambda x: f"{int(x, 2):03b}")

    # turns master_csv_file isntance into Path object for handling
    master_csv_path = Path(master_csv_file)

    if master_csv_path.exists():  # checking if master csv file exists
        # reading existing data from master csv into dataframe
        df_existing = pd.read_csv(
            master_csv_path, dtype={"P1_combo": str, "P2_combo": str}
        )
        print(f"Loaded existing file: {master_csv_path}")
    else:  # creates new master csv if the file doesn't exist
        print(f"{master_csv_path} does not exist, creating a new one.")
        df_existing = pd.DataFrame(
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
        )
        df_existing.to_csv(master_csv_path, index=False)

    df_updated = pd.concat([df_existing, df_scores], ignore_index=True)
    df_updated = df_updated.groupby(["P1_combo", "P2_combo"], as_index=False).sum()

    # save updated DataFrame to master CSV
    df_updated.to_csv(master_csv_path, index=False)
    print(f"Updated {master_csv_file} successfully!")

    # moves files from 'to_load' to 'loaded' once processed
    to_load_path = Path(to_load_dir)
    loaded_path = Path(loaded_dir)
    loaded_path.mkdir(parents=True, exist_ok=True)
    files_to_process = glob.glob(os.path.join(to_load_dir, "*.npz"))
    for npz_file in files_to_process:
        new_filename = npz_file.replace("raw_decks_", "processed_decks_")
        target_file = loaded_path / new_filename
        os.rename(npz_file, target_file)
        print(f"Moved and renamed {npz_file} to {target_file}")
    return
