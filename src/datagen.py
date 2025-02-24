import numpy as np
import os
import glob
from pathlib import Path
# from src.datagen import PATH_INFO

HALF_DECK_SIZE = 5
RED = 0
BLACK = 1


def get_decks(
    n_decks: int, seed: int, half_deck_size: int = HALF_DECK_SIZE
) -> tuple[np.ndarray, np.ndarray]:
    """
    Efficiently generate `n_decks` shuffled decks using NumPy.
    Returns: decks (np.ndarray): 2D array of shape (n_decks, num_cards), each row is a shuffled deck.
    """
    init_deck = [0] * half_deck_size + [1] * half_deck_size
    decks = np.tile(init_deck, (n_decks, 1))
    rng = np.random.default_rng(seed)
    seeds = np.arange(seed, seed + n_decks, 1)
    rng.permuted(decks, axis=1, out=decks)
    return decks, seeds


# The results are replicable and additional decks may be generated in addition to the other decks
def store_decks(
    decks: np.ndarray,
    seeds: np.ndarray,
    filepath: str = Path("./data"),
    append_file: bool = True,
) -> None:
    """
    Stores the shuffled decks and 'random' seeds used in np.arrays via time and date it was stored,
    saving it as the timestamp as the name. If the file exists, it appends the new shuffled decks and
    seeds to the existing file.
    """
    # Checking if file directory exists
    os.makedirs(filepath, exist_ok=True)
    # Finding and pulling the most recent file based on the timestamp
    files = glob.glob(os.path.join(filepath, "shuffled_decks_*.npz"))
    if append_file and files:
        files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))
        latest_file = files[-1]
        # Loading the existing data
        loaded = np.load(latest_file)
        stored_decks = loaded["decks"]
        stored_seeds = loaded["seeds"]
        # Appending new data
        decks = np.vstack((stored_decks, decks))
        seeds = np.concatenate((stored_seeds, seeds))
    else:
        # Create the new file with the incremented number per file
        new_index = 1 if not files else len(files) + 1
        latest_file = os.path.join(filepath, f"shuffled_decks_{new_index}.npz")
    # Save to the determined file
    np.savez_compressed(latest_file, decks=decks, seeds=seeds)
    print(f"Shuffled decks stored to {latest_file}")


def latest_seed(filepath: str) -> int:
    """
    Loads the latest seed that was last used based on the most recently saved file's datetime.
    If the file path isn't found, this is defaulted to random_state 42.
    """
    files = glob.glob(os.path.join(filepath, "shuffled_decks_*.npz"))
    if not files:
        return 42
    # Sort files numerically
    files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))
    latest_file = files[-1]
    loaded = np.load(latest_file)
    return loaded["seeds"][-1] + 1


# Note: there are only max 8 possible combinations that player 1 can generate
def player1(length=3, start: int = RED, end: int = BLACK, n_simulations=1):
    """Note: length=3 is default for the 3-bit game
    player1 function generates a random combination of Red and Black (represented as 0s and 1s) values of length=3
    """
    player1_combos = np.random.randint(start, end + 1, (n_simulations, length))
    return player1_combos


# Note: thinking is that .copy() logic is fine because of the limited number of unique potential combos from P1
def player2(player1_combos):
    """Takes the return from player1 to modify player2's output
    Function inverts the second value of P1's combo and shifts P1's first and second values to P2's 2nd and 3rd place
    """
    player2_combos = player1_combos.copy()
    player2_combos[:, 0] = 1 - player1_combos[:, 1]
    player2_combos[:, 1] = player1_combos[:, 0]
    player2_combos[:, 2] = player1_combos[:, 1]
    return player2_combos


def monte_carlo(
    n_simulations=1000, half_deck_size: int = HALF_DECK_SIZE, seed: int = 42
):
    """A vectorized approach to the Monte Carlo simulation, tracks the tricks and cards won, hopefully"""
    decks, _ = get_decks(n_simulations, seed=seed)

    # Calling the player sequence functions
    player1_combos = player1(n_simulations=n_simulations)
    player2_combos = player2(player1_combos)

    def rolling_window(arr, window_size):
        """Creates a rolling window view of the array (without copying data)."""
        shape = (arr.shape[0], arr.shape[1] - window_size + 1, window_size)
        strides = (arr.strides[0], arr.strides[1], arr.strides[1])
        return np.lib.stride_tricks.as_strided(arr, shape=shape, strides=strides)

    # Apply rolling window to decks (creates overlapping sequences)
    windowed_decks = rolling_window(
        decks, player1_combos.shape[1]
    )  # Shape: (n_simulations, deck_length-2, 3)
    # Vectorized sequence matching for both players
    p1_matches = np.all(
        windowed_decks == player1_combos[:, None, :], axis=2
    )  # Shape: (n_simulations, deck_length-2)
    p2_matches = np.all(
        windowed_decks == player2_combos[:, None, :], axis=2
    )  # Shape: (n_simulations, deck_length-2)

    def find_first_occurrence(matches):
        """Finds the first index where a sequence appears in each deck (or np.inf if not found)."""
        first_occurrence = np.where(matches, np.arange(matches.shape[1]), np.inf)
        min_indices = np.min(first_occurrence, axis=1)  # Earliest match per deck
        return min_indices, np.where(
            np.isinf(min_indices), 0, min_indices + 3
        )  # Add 3 cards per trick

    # commented out p1_card_counts, p2_card_counts
    p1_first_occurrence = find_first_occurrence(p1_matches)
    p2_first_occurrence = find_first_occurrence(p2_matches)
    # Counting Tricks
    player1_wins = np.sum(p1_first_occurrence < p2_first_occurrence)
    player2_wins = np.sum(p2_first_occurrence < p1_first_occurrence)
    # Computing probabilities
    player1_win_probability = player1_wins / n_simulations
    player2_win_probability = player2_wins / n_simulations
    # Compute average number of cards won per player
    # player1_avg_cards = np.sum(p1_card_counts) / n_simulations
    # player2_avg_cards = np.sum(p2_card_counts) / n_simulations

    return (
        player1_win_probability,
        player2_win_probability,
        # player1_avg_cards,
        # player2_avg_cards,
    )
