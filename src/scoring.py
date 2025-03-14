import numpy as np
import pandas as pd
from pathlib import Path
from src.helpers import ALL_COMBOS, TOTAL_COUNTS_FILE
from src.processing import combo_to_str


def score_summarize(
    results_file: str | Path = TOTAL_COUNTS_FILE,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Reads game results from CSV, computes win percentages for tricks and cards, and returns summary.
    ---
    Arguments:
        results_file (str | Path): path to the CSV file containing total counts
    Returns:
        tuple[np.ndarray, np.ndarray]: two 2D arrays of win percentages for tricks and cards
    """
    results_df = pd.read_csv(results_file)
    num_combos = len(ALL_COMBOS)
    COMBO_STRINGS = [combo_to_str(combo) for combo in ALL_COMBOS]
    trick_win_prob = np.zeros((num_combos, num_combos), dtype=float)
    card_win_prob = np.zeros((num_combos, num_combos), dtype=float)

    # iterating over all possible matchups
    for i, p1_combo_str in enumerate(COMBO_STRINGS):
        for j, p2_combo_str in enumerate(COMBO_STRINGS):
            # skipping if the same combo
            if p1_combo_str == p2_combo_str:
                trick_win_prob[j, i] = np.nan
                card_win_prob[j, i] = np.nan
                continue
            matchup = results_df[
                (results_df["P1_combo"] == p1_combo_str)
                & (results_df["P2_combo"] == p2_combo_str)
            ]
            if len(matchup) == 0:
                trick_win_prob[j, i] = np.nan
                card_win_prob[j, i] = np.nan
                continue
            # computing win percentages for P2
            p2_trick_wins = np.sum(matchup["P2_tricks"] > matchup["P1_tricks"])
            p2_card_wins = np.sum(matchup["P2_cards"] > matchup["P1_cards"])

            trick_win_prob[j, i] = (p2_trick_wins / len(matchup)) * 100
            card_win_prob[j, i] = (p2_card_wins / len(matchup)) * 100

    return trick_win_prob, card_win_prob
