import numpy as np
import pandas as pd
from pathlib import Path
from src.helpers import ALL_COMBOS, TOTAL_COUNTS_FILE


def score_probability(total_counts_csv: str | Path = TOTAL_COUNTS_FILE):
    """
    Calculates the probabilities of P2 winning tricks and cards.
    ---
    Args:
        total_counts_csv (str): Path to the CSV file containing aggregated counts.
    Returns:
        tuple[np.ndarray, np.ndarray]: Two 2D arrays of win percentages for tricks and cards.
    """
    results_df = pd.read_csv(total_counts_csv, dtype={"P1_combo": str, "P2_combo": str})
    trick_array = np.zeros((8, 8))
    card_array = np.zeros((8, 8))
    for i, P1_combo in enumerate(ALL_COMBOS):  # filtering dataframe on p1
        for j, P2_combo in enumerate(ALL_COMBOS):  # filtering dataframe on p2
            if P1_combo == P2_combo:  # skipping same combo matchups
                continue
            df_subset = results_df[
                (results_df["P1_combo"] == P1_combo)
                & (results_df["P2_combo"] == P2_combo)
            ]  # ensuring combo matchups
            total_matches = len(df_subset)  # total instances for the matchup
            if total_matches > 0:
                # counts wins and draws
                p2_trick_wins = (df_subset["P2_tricks"] > df_subset["P1_tricks"]).sum()
                p2_card_wins = (df_subset["P2_cards"] > df_subset["P1_cards"]).sum()
                # calculates probabilities
                trick_array[i, j] = p2_trick_wins / total_matches
                card_array[i, j] = p2_card_wins / total_matches
            else:
                trick_array[i, j] = np.nan
                card_array[i, j] = np.nan
    return trick_array, card_array
