import numpy as np
import os
from pathlib import Path
from src.helpers import R, B

HALF_DECK_SIZE = 5


def get_decks(
    n_decks: int = 1000, seed: int = 42, half_deck_size: int = HALF_DECK_SIZE
) -> tuple[np.ndarray, np.ndarray]:
    """Efficiently generates `n_decks` shuffled decks using NumPy.
    ---
    Arguments:
    n_decks (int): number of shuffled decks to generate, default is 1000
    seed (int): seed for random number generator, default is 42
    half_deck_size (int): as mentioned, default is 5
    Returns:
    tuple containing
     - decks (np.ndarray): 2D array of shape (n_decks, num_cards), each row is a shuffled deck.
     - seeds (np.ndarray): Array of seeds used to shuffle the decks."""
    init_deck = [R] * half_deck_size + [B] * half_deck_size
    decks = np.tile(init_deck, (int(n_decks), 1))
    rng = np.random.default_rng(seed)
    rng.permuted(decks, axis=1, out=decks)
    seeds = np.arange(seed, seed + n_decks, 1)
    return decks, seeds


def latest_deck_file(directory: str) -> Path:
    """
    Finds the most recent shuffled deck file based on the filename pattern in a given directory
    ---
    Arguments: directory (str): path to folder where the deck files are located
    Returns: either the most recent deck file or not returning anything if the files aren't found
    """
    files = sorted(Path(directory).glob("shuffled_decks_*.npz"))
    if not files:
        return None
    return files[-1]


def store_decks(
    decks: np.ndarray,
    seeds: np.ndarray,
    directory: str = "./data",
    append_file: bool = True,
) -> None:
    """Stores shuffled decks and respective seeds in the .npz file
    ---
    Arguments:
    decks (np.ndarray): 2D array of shuffled decks to store
    seeds (np.ndarray): array of seeds associated with the decks
    directory (str)
    append_file (bool): option to append to the most recent file or store a new one (default is `True`)
    """
    os.makedirs(directory, exist_ok=True)
    latest_file = latest_deck_file(directory)
    if latest_file is None:
        new_file = os.path.join(directory, "shuffled_decks_1.npz")
        np.savez_compressed(new_file, decks=decks, seeds=seeds)
        print(f"Stored first deck file: {new_file}")
        return
    if append_file:
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
    else:
        latest_number = int(latest_file.stem.split("_")[-1])
        new_file = os.path.join(directory, f"shuffled_decks_{latest_number + 1}.npz")
        np.savez_compressed(new_file, decks=decks, seeds=seeds)
