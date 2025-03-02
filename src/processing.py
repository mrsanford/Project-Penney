import numpy as np
import pandas as pd
from pathlib import Path
import os
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
from src.datagen import latest_deck_file
from src.helpers import P1_COMBOS, R, B
from src.helpers import PLOTS_DIR


def load_decks(directory: str = "./data") -> np.ndarray:
    """Dynamically loads the most recent deck file dynamically
    ---
    Arguments: directory (str)
    Returns: np.ndarray of loaded decks from the most recent '.npz' file
    Raises: FileNotFoundError: if no shuffled deck files are found
    """
    latest_file = latest_deck_file(directory)
    if latest_file is None:
        raise FileNotFoundError("No shuffled decks found.")
    data = np.load(latest_file)
    return data["decks"]


def combo_to_str(combo: tuple[int, int, int]) -> str:
    return "".join("R" if x == R else "B" for x in combo)


def combo_from_str(combo_str: str) -> tuple[int, int, int]:
    return tuple(R if ch == "R" else B for ch in combo_str)


def find_tricks(deck: np.ndarray, P1_combo: tuple, P2_combo: tuple) -> tuple[int, int]:
    """
    Scans the deck to find/count tricks for each player. After the trick is found,
    the sequence gets cut and continues at the next card.
    ---
    Arguments:
    deck (np.ndarray): the shuffled deck of cards
    P1_combo (np.ndarray): P1's combination
    P2_combo (np.ndarray): P2's combination
    Returns: tuple of the number of tricks won per player
    """
    P1_tricks = P2_tricks = 0
    combo_length = len(P1_combo)
    assert combo_length == 3
    i = 0
    while i <= len(deck) - combo_length:
        if np.array_equal(P1_combo, P2_combo):
            # P1 and P2 have the same sequence, P1 always wins these
            if np.array_equal(deck[i : i + combo_length], P1_combo):
                P1_tricks += 1
                i += combo_length
            else:
                i += 1
        else:
            if np.array_equal(deck[i : i + combo_length], P1_combo):
                P1_tricks += 1
                i += combo_length
            elif np.array_equal(deck[i : i + combo_length], P2_combo):
                P2_tricks += 1
                i += combo_length
            else:
                i += 1
    return P1_tricks, P2_tricks


def count_cards(deck: np.ndarray, P1_combo: tuple, P2_combo: tuple) -> tuple[int, int]:
    """
    Counts total cards won per player (including unclaimed cards between tricks).
    ---
    Arguments:
        deck (np.ndarray): the shuffled deck of cards
        P1_combo (np.ndarray): P1's combination
        P2_combo (np.ndarray): P2's combination
    Returns:
        tuple: (P1_cards, P2_cards)
    """
    combo_length = len(P1_combo)
    windows = np.lib.stride_tricks.sliding_window_view(deck, combo_length)
    P1_matches = np.all(windows == P1_combo, axis=1)
    P2_matches = np.all(windows == P2_combo, axis=1)
    P1_cards = P2_cards = 0
    last_claimed_index = -1
    i = 0
    while i < len(P1_matches):
        if P1_matches[i]:
            if i <= last_claimed_index:
                i += 1
                continue
            won_cards = (i - last_claimed_index) + combo_length - 1
            P1_cards += won_cards
            last_claimed_index = i + combo_length - 1
            i += combo_length
        elif P2_matches[i]:
            if i <= last_claimed_index:
                i += 1
                continue
            won_cards = (i - last_claimed_index) + combo_length - 1
            P2_cards += won_cards
            last_claimed_index = i + combo_length - 1
            i += combo_length
        else:
            i += 1
    return P1_cards, P2_cards


# check the path constants here
def simulate_combos(
    decks: np.ndarray, P1_combos: tuple, P2_combos: tuple
) -> pd.DataFrame:
    """
    Simulate the game for all combinations and all available shuffled decks
    ---
    Arguments:
    deck_file (str): path to the file of shuffled decks
    P1_combos (np.ndarray): P1's possible combinations in an array
    P2_combos (np.ndarray): P2's possible combinations in an array
    Return:
    np.ndarray: A 2D array of shape (n_combinations * n_decks, 7) containing the results for each combination
    (deck_id, P1_combo, P2_combo, P1_tricks, P2_tricks, P1_cards, P2_cards).
    """
    decks = load_decks(directory="./data")
    results = []
    for deck_id, deck in enumerate(decks):
        for P1_combo in P1_combos:
            for P2_combo in P2_combos:
                if np.array_equal(P1_combo, P2_combo):
                    continue
                P1_tricks, P2_tricks = find_tricks(deck, P1_combo, P2_combo)
                P1_cards, P2_cards = count_cards(deck, P1_combo, P2_combo)
                trick_tie = 1 if P1_tricks == P2_tricks else 0
                card_tie = 1 if P1_cards == P2_cards else 0
                results.append(
                    {
                        "deck_id": deck_id,
                        "P1_combo": combo_to_str(P1_combo),
                        "P2_combo": combo_to_str(P2_combo),
                        "P1_tricks": P1_tricks,
                        "P2_tricks": P2_tricks,
                        "trick_tie": trick_tie,
                        "P1_cards": P1_cards,
                        "P2_cards": P2_cards,
                        "card_tie": card_tie,
                    }
                )
    df = pd.DataFrame(results)
    os.makedirs("./results", exist_ok=True)
    output_file = "./results/testing.csv"
    if os.path.exists(output_file):
        df.to_csv(output_file, mode="a", header=False, index=False)
    else:
        df.to_csv(output_file, index=False)
    return df


# update the Path with constant here
def score_summarize(results_file: str | Path = Path("./results/testing.csv")):
    """
    Reads the game results from a CSV file, computes trick and card win percentages,
    and writes/updates the summary CSV with those statistics. The outputs are used for the heatmaps.
    ---
    Arguments:
    results_file (str): Path to the raw game results CSV.
    summary_file (str): Path to the summary file to append results.
    """
    results_df = pd.read_csv(results_file)
    COMBO_STRINGS = [combo_to_str(combo) for combo in P1_COMBOS]
    p2_trick_pct = np.zeros((8, 8), dtype=float)
    p2_card_pct = np.zeros((8, 8), dtype=float)
    for i, p1_combo_str in enumerate(COMBO_STRINGS):
        for j, p2_combo_str in enumerate(COMBO_STRINGS):
            if p1_combo_str == p2_combo_str:
                p2_trick_pct[j, i] = np.nan
                p2_card_pct[j, i] = np.nan
                continue
            matchup = results_df[
                (results_df["P1_combo"] == p1_combo_str)
                & (results_df["P2_combo"] == p2_combo_str)
            ]
            if len(matchup) == 0:
                p2_trick_pct[j, i] = np.nan
                p2_card_pct[j, i] = np.nan
                continue
            p2_trick_wins = np.sum(matchup["P2_tricks"] > matchup["P1_tricks"])
            p2_card_wins = np.sum(matchup["P2_cards"] > matchup["P1_cards"])

            p2_trick_pct[j, i] = (p2_trick_wins / len(matchup)) * 100
            p2_card_pct[j, i] = (p2_card_wins / len(matchup)) * 100
    return p2_trick_pct, p2_card_pct


def plot_heatmaps(p2_trick_pct, p2_card_pct, save: bool = True, show: bool = False):
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    mask = np.eye(len(P1_COMBOS), dtype=bool)
    cmap = sns.color_palette("coolwarm", as_cmap=True)
    cmap = cmap.with_extremes(bad="lightgrey")
    labels = ["".join(["R" if x == R else "B" for x in combo]) for combo in P1_COMBOS]

    fig, axes = plt.subplots(1, 2, figsize=(18, 8), dpi=100)

    heatmap_kws = {
        "annot": True,
        "fmt": ".1f",
        "xticklabels": labels,
        "yticklabels": labels,
        "vmin": 0,
        "vmax": 100,
        "cbar_kws": {"shrink": 0.8},
        "cmap": cmap,
        "mask": mask,
    }
    sns.heatmap(p2_trick_pct, ax=axes[0], **heatmap_kws)
    axes[0].set_title("P2 Trick Win Probability (%)")
    axes[0].set_xlabel("Player 1 Combination")
    axes[0].set_ylabel("Player 2 Combination")

    sns.heatmap(p2_card_pct, ax=axes[1], **heatmap_kws)
    axes[1].set_title("P2 Card Win Probability (%)")
    axes[1].set_xlabel("Player 1 Combination")
    axes[1].set_ylabel("Player 2 Combination")
    plt.tight_layout()
    if save:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        plot_path = PLOTS_DIR / f"heatmap_{timestamp}.png"
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        print(f"Saved heatmap to: {plot_path}")
    if show:
        plt.show()
    else:
        plt.close()
