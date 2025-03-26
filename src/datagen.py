import numpy as np
from datetime import datetime
from pathlib import Path
from src.helpers import HALF_DECK_SIZE, TO_LOAD_DIR


def get_decks(
    n_decks: int = 1000, seed: int = 42, half_deck_size: int = HALF_DECK_SIZE
) -> tuple[np.ndarray, np.ndarray]:
    """Efficiently generates `n_decks` shuffled decks using NumPy.
    ---
    Args:
        n_decks (int): number of shuffled decks to generate, default is 1000
        seed (int): seed for random number generator, default is 42
        half_deck_size (int): default is 26
    Returns:
        tuple containing
        decks (np.ndarray): 2D array of shape (n_decks, num_cards), each row is a shuffled deck
        seeds (np.ndarray): Array of seeds used to shuffle the decks
    """
    init_deck = [0] * half_deck_size + [1] * half_deck_size
    decks = np.tile(init_deck, (int(n_decks), 1))
    rng = np.random.default_rng(seed)
    rng.permuted(decks, axis=1, out=decks)
    seeds = np.arange(seed, seed + n_decks, 1)
    return decks, seeds


def latest_deck_file(directory: Path = TO_LOAD_DIR) -> str | None:
    """
    Finds the most recent shuffled deck file based on the filename pattern in a given directory
    ---
    Args: directory (str): path to folder where the deck files are located
    Returns: the most recent deck file or None if no files are found
    """
    files = sorted(Path(directory).glob("raw_decks_*.npz"))
    return str(files[-1] if files else None)


def store_decks(
    decks: np.ndarray,
    seeds: np.ndarray,
    directory: Path = TO_LOAD_DIR,
    append_decks: bool = True,
) -> None:
    """
    Stores shuffled decks with a datetime-based naming convention.
    ---
    Args:
        decks (np.ndarray): 2D array of shuffled decks to store.
        seeds (np.ndarray): Array of seeds associated with the decks.
        directory (str): Target directory to store the files.
        append_decks (bool): If True, appends to latest file; otherwise, creates a new file.
    """
    directory.mkdir(parents=True, exist_ok=True)
    decks_str = np.array(
        ["".join(map(str, deck)) for deck in decks]
    )  # converts decks to string format
    if append_decks:
        # Find the latest deck file in the directory
        latest_file = latest_deck_file(directory)
        if latest_file is None:  # If no previous files exist, create the first file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_file = directory / f"raw_decks_{timestamp}.npz"
            np.savez_compressed(new_file, decks=decks, decks_str=decks_str, seeds=seeds)
            print(f"Stored first deck file: {new_file}")
            return
        # If latest file exists, load it
        data = np.load(latest_file)
        # Check if decks and seeds exist in the loaded file
        if "decks" in data.files and "seeds" in data.files:
            stored_decks = data["decks"].copy()
            stored_seeds = data["seeds"].copy()
            stored_decks_str = data["decks_str"].copy()

            latest_used_seed = stored_seeds[-1]
            new_seeds = np.arange(
                latest_used_seed + 1, latest_used_seed + 1 + len(decks)
            )

            # Append new decks
            decks = np.vstack((stored_decks, decks))
            decks_str = np.concatenate((stored_decks_str, decks_str))
            seeds = np.concatenate((stored_seeds, new_seeds))

            # Save updated file
            np.savez_compressed(
                latest_file, decks=decks, decks_str=decks_str, seeds=seeds
            )
            print(f"Updated existing deck file: {latest_file}")
        else:
            # If no valid decks/seeds found in the file, create a new one
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_file = directory / f"raw_decks_{timestamp}.npz"
            np.savez_compressed(new_file, decks=decks, decks_str=decks_str, seeds=seeds)
            print(f"Stored new deck file: {new_file}")
    else:  # If not appending, create a new file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_file = directory / f"raw_decks_{timestamp}.npz"
        np.savez_compressed(new_file, decks=decks, decks_str=decks_str, seeds=seeds)
        print(f"Stored new deck file: {new_file}")
        return
