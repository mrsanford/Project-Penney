import numpy as np
import os
from pathlib import Path
from src.helpers import R, B, HALF_DECK_SIZE, TO_LOAD_DIR


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


def latest_deck_file(directory: str) -> Path | None:
    """
    Finds the most recent shuffled deck file based on the filename pattern in a given directory
    ---
    Arguments: directory (str): path to folder where the deck files are located
    Returns: the most recent deck file or None if no files are found
    """
    files = sorted(Path(directory).glob("raw_shuffled_decks_*.npz"))
    return files[-1] if files else None


def store_decks(
    decks: np.ndarray,
    seeds: np.ndarray,
    directory: str = TO_LOAD_DIR,
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
    # ensures the target directory exists; creates directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    if append_file:
        # finds the most recent shuffled deck file in the directory
        latest_file = latest_deck_file(directory)

        # if no file exists, creates the first one
        if latest_file is None:
            new_file = os.path.join(directory, "raw_shuffled_decks_1.npz")
            np.savez_compressed(new_file, decks=decks, seeds=seeds)
            print(f"Stored first deck file: {new_file}")
            return
        # loads the data from the most recent file
        data = np.load(latest_file)
        if "decks" in data.files and "seeds" in data.files:
            stored_decks = data["decks"].copy()
            stored_seeds = data["seeds"].copy()
            # generates the new seeds based on the last used seed
            latest_used_seed = stored_seeds[-1]
            new_seeds = np.arange(
                latest_used_seed + 1, latest_used_seed + 1 + len(decks)
            )
            # appends the new decks and seeds
            decks = np.vstack((stored_decks, decks))
            seeds = np.concatenate((stored_seeds, new_seeds))
        # saves the updated shuffled data and seeds to the latest file
        np.savez_compressed(latest_file, decks=decks, seeds=seeds)
    else:
        existing_files = sorted(Path(directory).glob("raw_shuffled_decks_*.npz"))

        if existing_files:
            try:
                latest_number = max(
                    int(file.stem.split("_")[-1]) for file in existing_files
                )
            except ValueError:
                # if the file naming convention is not followed, beginning at file number 1
                latest_number = 1
        else:
            latest_number = 0  # if no files exist, beginning at file number 1

        # creates a new file with the incremented index naming convention
        new_file = os.path.join(
            directory, f"raw_shuffled_decks_{latest_number + 1}.npz"
        )
        np.savez_compressed(new_file, decks=decks, seeds=seeds)
        print(f"Stored new deck file: {new_file}")
