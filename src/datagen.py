import numpy as np
import os
import glob
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
# from src.datagen import PATH_INFO

HALF_DECK_SIZE = 5
RED = 0
BLACK = 1

# 8 possible combos
ALL_COMBOS = np.array(
    [
        [0, 0, 0],
        [0, 0, 1],
        [0, 1, 0],
        [0, 1, 1],
        [1, 0, 0],
        [1, 0, 1],
        [1, 1, 0],
        [1, 1, 1],
    ]
)


def get_decks(
    n_decks: int, seed: int, half_deck_size: int = HALF_DECK_SIZE
) -> tuple[np.ndarray, np.ndarray]:
    """
    Efficiently generate `n_decks` shuffled decks using NumPy.
    Returns: decks (np.ndarray): 2D array of shape (n_decks, num_cards), each row is a shuffled deck.
    """
    print(
        f"Inside get_decks: n_decks type: {type(n_decks)}, value: {n_decks}"
    )  # Debug print

    if not isinstance(n_decks, int):  # Ensure it's an integer
        raise TypeError(f"Expected n_decks to be an integer, but got {type(n_decks)}")
    init_deck = [0] * half_deck_size + [1] * half_deck_size
    decks = np.tile(init_deck, (int(n_decks), 1))
    rng = np.random.default_rng(seed)
    rng.permuted(decks, axis=1, out=decks)
    seeds = np.arange(seed, seed + n_decks, 1)
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
    os.makedirs(filepath, exist_ok=True)
    files = glob.glob(os.path.join(filepath, "shuffled_decks_*.npz"))
    if append_file and files:
        files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))
        latest_file = files[-1]
        loaded = np.load(latest_file)
        stored_decks = loaded["decks"]
        stored_seeds = loaded["seeds"]
        decks = np.vstack((stored_decks, decks))
        seeds = np.concatenate((stored_seeds, seeds))
    else:
        new_index = 1 if not files else len(files) + 1
        latest_file = os.path.join(filepath, f"shuffled_decks_{new_index}.npz")

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
    files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))
    latest_file = files[-1]
    loaded = np.load(latest_file)
    return loaded["seeds"][-1] + 1


# Note: there are only max 8 possible combinations that player 1 can generate
def player1(n_simulations: int):
    """Generates P1's combos by randomly selecting from the 8 possible combos
    Just samples from the indices 0 to 7
    """
    indices = np.random.randint(0, len(ALL_COMBOS), n_simulations)
    player1_combos = ALL_COMBOS[indices]
    return player1_combos


# Note: thinking is that .copy() logic is fine because of the limited number of unique potential combos from P1
def player2(player1_combos: np.ndarray):
    """Takes the return from player1 to modify player2's output
    Function inverts the second value of P1's combo and shifts P1's first and second values to P2's 2nd and 3rd place
    """
    player2_combos = player1_combos.copy()
    player2_combos[:, 0] = 1 - player1_combos[:, 1]
    player2_combos[:, 1] = player1_combos[:, 0]
    player2_combos[:, 2] = player1_combos[:, 1]
    return player2_combos


def rolling_window(arr, window_size):
    shape = (arr.shape[0], arr.shape[1] - window_size + 1, window_size)
    strides = (arr.strides[0], arr.strides[1], arr.strides[1])
    return np.lib.stride_tricks.as_strided(arr, shape=shape, strides=strides)


def add_trick(matches):
    trick_count = np.sum(matches, axis=1)
    return trick_count


def add_cards(matches, decks):
    won_cards = np.zeros(matches.shape[0], dtype=int)
    for i in range(matches.shape[0]):
        last_win_idx = -1
        for j in range(matches.shape[1]):
            if matches[i, j]:
                won_cards[i] += j - last_win_idx
                last_win_idx = j
    return won_cards


def monte_carlo(
    n_decks: int = 5,
    n_simulations: int = 10,
    half_deck_size: int = HALF_DECK_SIZE,
    seed: int = 42,
):
    """A vectorized approach to the Monte Carlo simulation, tracks the tricks and cards won, hopefully"""
    decks, _ = get_decks(n_decks, seed=seed)
    player1_combos = player1(n_simulations)
    player2_combos = player2(player1_combos)

    windowed_decks = rolling_window(decks, player1_combos.shape[1])
    p1_matches = np.all(windowed_decks == player1_combos[:, None, :], axis=2)
    p2_matches = np.all(windowed_decks == player2_combos[:, None, :], axis=2)

    p1_tricks = add_trick(p1_matches)
    p2_tricks = add_trick(p2_matches)

    p1_cards = add_cards(p1_matches, decks)
    p2_cards = add_cards(p2_matches, decks)

    total_cards = half_deck_size * 2
    p1_unwon = total_cards - (p1_cards + p2_cards)

    player1_win_probability = np.sum(p1_tricks > p2_tricks) / n_simulations
    player2_win_probability = np.sum(p2_tricks > p1_tricks) / n_simulations

    return player1_win_probability, player2_win_probability


# Heatmap
prob_matrix = np.empty((8, 8))
for i, p1_combo in enumerate(ALL_COMBOS):
    p2_combo = player2(p1_combo.reshape(1, -1))
    p1_win_prob, _ = monte_carlo(n_simulations=1)
    prob_matrix[i] = p1_win_prob

plt.figure(figsize=(8, 6))
sns.heatmap(
    prob_matrix,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    xticklabels=ALL_COMBOS,
    yticklabels=ALL_COMBOS,
)
plt.xlabel("Player 2 Combination")
plt.ylabel("Player 1 Combination")
plt.title("Heatmap of Player 1 Win Probabilities")
plt.show()
