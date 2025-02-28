import numpy as np
import os
import glob
import pandas as pd
import itertools
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
# from src.datagen import PATH_INFO

HALF_DECK_SIZE = 5
R, B = 0, 1  # Red and Black

# there are 8 possible P1 combos
P1_COMBOS = np.array(
    [
        [R, R, R],
        [R, R, B],
        [R, B, R],
        [R, B, B],
        [B, R, R],
        [B, R, B],
        [B, B, R],
        [B, B, B],
    ]
)


def get_decks(
    n_decks: int = 1000, seed: int = 42, half_deck_size: int = HALF_DECK_SIZE
) -> tuple[np.ndarray, np.ndarray]:
    """Efficiently generate `n_decks` shuffled decks using NumPy.
    Returns: decks (np.ndarray): 2D array of shape (n_decks, num_cards), each row is a shuffled deck."""
    init_deck = [R] * half_deck_size + [B] * half_deck_size
    decks = np.tile(init_deck, (int(n_decks), 1))
    rng = np.random.default_rng(seed)
    rng.permuted(decks, axis=1, out=decks)
    seeds = np.arange(seed, seed + n_decks, 1)
    return decks, seeds


def latest_seed(filepath: str) -> int:
    """Loads the latest seed that was last used based on the most recently saved file's datetime.
    If the file path isn't found, this is defaulted to random_state 42."""
    files = sorted(Path(filepath).glob("shuffled_decks_*.npz"))
    if not files:
        return 42
    data = np.load(files[-1])
    return data["seeds"][-1] + 1


def latest_deck(filepath: str) -> Path | None:
    files = sorted(Path(filepath).glob("shuffled_decks_*.npz"))
    return files[-1] if files else None


def store_decks(
    decks: np.ndarray,
    seeds: np.ndarray,
    filepath: str = "./data",
    append_file: bool = True,
) -> None:
    """Stores shuffled decks and respective seeds in the .npz file."""
    os.makedirs(filepath, exist_ok=True)
    latest_file = latest_deck(filepath)
    if append_file and latest_file:
        data = np.load(latest_file)
        if "decks" in data.files and "seeds" in data.files:
            stored_decks = data["decks"]
            stored_seeds = data["seeds"]
            latest_used_seed = stored_seeds[-1]
            new_seeds = np.arange(
                latest_used_seed + 1, latest_used_seed + 1 + len(decks)
            )
            decks = np.vstack((stored_decks, decks))
            seeds = np.concatenate((stored_seeds, new_seeds))
        np.savez_compressed(latest_file, decks=decks, seeds=seeds)
        print(f"Appended decks to {latest_file}")
    else:
        new_index = len(list(Path(filepath).glob("shuffled_decks_*.npz"))) + 1
        new_file = os.path.join(filepath, f"shuffled_decks_{new_index}.npz")
        np.savez_compressed(new_file, decks=decks, seeds=seeds)
        print(f"Stored new deck file: {new_file}")


def load_decks(filepath: str) -> np.ndarray:
    """Loads the most recent deck file dynamically in preparation for Monte Carlo"""
    latest_file = latest_deck(filepath)
    print(f"Looking for latest deck file in: {filepath}")
    if latest_file is None:
        raise FileNotFoundError("No shuffled decks found.")
    print(f"Loading deck file: {latest_file}")
    return np.load(latest_file)["decks"]


def count_tricks(deck, P1_combo: np.ndarray, P2_combo: np.ndarray):
    print(f"Deck: {deck}")
    P1_tricks = P2_tricks = 0
    combo_length = len(P1_combo)
    i = 0
    while i <= len(deck) - combo_length:
        triplet = deck[i : i + combo_length]
        if np.array_equal(triplet, P1_combo):
            P1_tricks += 1
            i += combo_length
        elif np.array_equal(triplet, P2_combo):
            P2_tricks += 1
            i += combo_length
        else:
            i += 1
    return P1_tricks, P2_tricks


def count_cards(deck, P1_combo: np.ndarray, P2_combo: np.ndarray):
    P1_cards = P2_cards = 0
    unwon_cards = 0
    combo_length = len(P1_combo)
    i = 0
    while i <= len(deck) - combo_length:
        triplet = deck[i : i + combo_length]
        if np.array_equal(triplet, P1_combo):
            P1_cards += combo_length + unwon_cards
            unwon_cards = 0
            i += combo_length
        elif np.array_equal(triplet, P2_combo):
            P2_cards += combo_length + unwon_cards
            unwon_cards = 0
            i += combo_length
        else:
            unwon_cards += 1
            i += 1
    return P1_cards, P2_cards


def simulate_combos(
    deck_file: str, P1_combos: np.ndarray, P2_combos: np.ndarray
) -> np.ndarray:
    """Simulate the game for all combinations and all shuffled decks."""
    decks = load_decks(deck_file)
    # print(f"Decks loaded: {decks.shape}")
    all_results = []
    for deck_id, deck in enumerate(decks):
        for P1_combo in P1_combos:
            for P2_combo in P2_combos:
                # print(
                #     f"Simulating deck {deck_id} with combination {P1_combo} vs {P2_combo}"
                # )
                P1_tricks, P2_tricks = count_tricks(deck, P1_combo, P2_combo)
                P1_cards, P2_cards = count_cards(deck, P1_combo, P2_combo)
                result_row = np.array(
                    [
                        deck_id,
                        P1_combo,
                        P2_combo,
                        P1_tricks,
                        P2_tricks,
                        P1_cards,
                        P2_cards,
                    ],
                    dtype=object,
                )
                all_results.append(result_row)
        all_results_arr = np.vstack(all_results)
        print(f"Simulate Combos Output Shape: {np.vstack(all_results).shape}")
        return all_results_arr


def score_game(results: np.ndarray):
    """Tallies the points for P1 and P2 based on tricks and cards, computes percentages"""
    # Count Trick Wins
    trick_winner = np.where(results[:, 3] == 1, 1, np.where(results[:, 3] == 2, 2, 0))
    P1_trick_wins = np.sum(trick_winner == 1)
    P2_trick_wins = np.sum(trick_winner == 2)
    # Count Card Wins
    card_winner = np.where(results[:, 5] == 1, 1, np.where(results[:, 5] == 2, 2, 0))
    P1_card_wins = np.sum(card_winner == 1)
    P2_card_wins = np.sum(card_winner == 2)
    # Calculate win percentages based on tricks and cards
    total_games = len(results)
    # Trick and Card Percentages
    P1_trick_pct = (P1_trick_wins / total_games) * 100
    P2_trick_pct = (P2_trick_wins / total_games) * 100
    P1_card_pct = (P1_card_wins / total_games) * 100
    P2_card_pct = (P2_card_wins / total_games) * 100
    # Draw Percentage (both trick and card are ties)
    draw_pct = np.sum((trick_winner == 0) & (card_winner == 0)) / total_games * 100
    # Return all statistics in a dictionary or tuple for easy access
    return {
        "P1_trick_pct": P1_trick_pct,
        "P2_trick_pct": P2_trick_pct,
        "P1_card_pct": P1_card_pct,
        "P2_card_pct": P2_card_pct,
        "draw_pct": draw_pct,
    }


def plot_heatmaps(p1_trick_pct, p1_card_pct):
    """Plot heatmaps for Player 1 vs Player 2 win probabilities based on tricks and cards."""
    print(f"Player 1 Trick %:\n{p1_trick_pct}")
    print(f"Player 1 Card %:\n{p1_card_pct}")
    # Mask out invalid diagonal cells (same combo vs same combo)
    mask = np.eye(len(P1_COMBOS), dtype=bool)
    # Ensure that win percentages are between 0 and 100 (scale if needed)
    p1_trick_pct = np.clip(p1_trick_pct, 0, 100)
    p1_card_pct = np.clip(p1_card_pct, 0, 100)
    # Color palette for heatmaps
    cmap = sns.color_palette("coolwarm", as_cmap=True)
    cmap.set_bad(color="lightgrey")  # This makes the diagonal grey
    # Generate the labels dynamically based on binary values
    labels = ["".join(["R" if x == R else "B" for x in combo]) for combo in P1_COMBOS]
    # Set up figure for two subplots
    fig, axes = plt.subplots(1, 2, figsize=(18, 8), dpi=100)
    # Common heatmap settings
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
    # Plot Player Trick Win Probability Heatmap
    sns.heatmap(p1_trick_pct, ax=axes[0], **heatmap_kws)
    axes[0].set_title("Player Trick Win Probability (%)")
    axes[0].set_xlabel("Player 2 Combination")
    axes[0].set_ylabel("Player 1 Combination")
    # Plot Player Card Win Probability Heatmap
    sns.heatmap(p1_card_pct, ax=axes[1], **heatmap_kws)
    axes[1].set_title("Player Card Win Probability (%)")
    axes[1].set_xlabel("Player 2 Combination")
    axes[1].set_ylabel("Player 1 Combination")
    plt.tight_layout()
    plt.show()
