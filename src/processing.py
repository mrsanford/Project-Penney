import numpy as np
import pandas as pd
import os
from src.datagen import latest_deck_file
from src.helpers import R, ALL_COMBOS, TO_LOAD_DIR, LOADED_DIR, TOTAL_COUNTS_FILE


def load_decks() -> np.ndarray:
    """
    Loads the most recent shuffled deck file from 'to_load' to 'loaded'
    """
    latest_file = latest_deck_file(TO_LOAD_DIR)
    if latest_file is None:
        raise FileNotFoundError("No shuffled decks found.")
    data = np.load(latest_file)
    decks = data["decks"]
    if decks.ndim == 1:
        decks = decks.reshape(1, -1)
    new_name = latest_file.name.replace("raw", "processed")
    new_location = LOADED_DIR / new_name
    os.rename(latest_file, new_location)
    print(f"Move and renamed {latest_file} to {new_location}")
    return decks


def combo_to_str(combo: tuple[int, int, int]) -> str:
    """
    Converts the numerical card combination into a string representation.
    ---
    Arguments:
        combo (tuple[int, int, int]): a tuple representing a card sequence
    Returns:
        str: a string where 'R' represents 0 values and 'B' represents 1 values
    """
    return "".join("R" if x == R else "B" for x in combo)


def find_sequences(
    deck: np.ndarray, P1_combo: tuple, P2_combo: tuple
) -> tuple[int, int]:
    """
    Identifies and scores sequences for both players.
    ---
    Arguments:
        deck (np.ndarray): the shuffled deck of cards
        P1_combo (np.ndarray): P1's combination
        P2_combo (np.ndarray): P2's combination
    Returns: tuple of the number of tricks and cards won per player
    """
    P1_cards = P2_cards = 0
    P1_tricks = P2_tricks = 0
    combo_length = len(P1_combo)
    i = 0
    while i <= deck.size - combo_length:
        if np.array_equal(deck[i : i + combo_length], P1_combo):
            P1_cards += combo_length
            P1_tricks += 1
            i += combo_length
        elif np.array_equal(deck[i : i + combo_length], P2_combo):
            P2_cards += combo_length
            P2_tricks += 1
            i += combo_length
        else:
            i += 1
    return P1_cards, P2_cards, P1_tricks, P2_tricks


def score_game(deck: np.ndarray, P1_combo: tuple, P2_combo: tuple) -> dict:
    """Scores a single game
    ---
    Arguments:
        Intakes the same arguments as find_sequences()
    Returns:
        dict: a dictionary containing the P1 and P2 combos, scores, and tricks
    """
    P1_cards, P2_cards, P1_tricks, P2_tricks = find_sequences(deck, P1_combo, P2_combo)
    return {
        "P1_combo": P1_combo,
        "P2_combo": P2_combo,
        "P1_score": P1_cards,
        "P2_score": P2_cards,
        "P1_tricks": P1_tricks,
        "P2_tricks": P2_tricks,
        "card_ties": int(P1_cards == P2_cards),
        "trick_ties": int(P1_tricks == P2_tricks),
    }


def simulate_games(
    decks: np.ndarray, P1_combos: tuple = ALL_COMBOS, P2_combos: tuple = ALL_COMBOS
) -> pd.DataFrame:
    """Simulates multiple games and stores results."""
    results = []
    for deck_id, deck in enumerate(decks):
        for P1_combo in P1_combos:
            for P2_combo in P2_combos:
                if np.array_equal(P1_combo, P2_combo):
                    continue
                game_result = score_game(deck, P1_combo, P2_combo)
                game_result["deck_id"] = deck_id
                results.append(game_result)
    total_count_df = pd.DataFrame(results)
    total_count_df.to_csv(
        TOTAL_COUNTS_FILE,
        mode="a",
        header=not os.path.exists(TOTAL_COUNTS_FILE),
        index=False,
    )
    return total_count_df
