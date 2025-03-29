import os
import json
import datetime
from datetime import datetime
import numpy as np
from src.helpers import (HALF_DECK_SIZE,
                         PATH_DATA_DECKS,
                         PATH_DATA_SEEDS)


def gen_decks(n_decks: int = 1000, seed: int = 50) -> tuple[np.ndarray, np.ndarray]:
    """
    Generates shuffled decks of cards and used seeds
    ---
    Args:
        n_decks (int) number of decks to generate
        seed (int) starting seed for deck shuffling
    Returns:
        tuple[np.ndarray,np.ndarray] of shuffled decks and seeds
    """
    init_deck = [0] * HALF_DECK_SIZE + [1] * HALF_DECK_SIZE
    decks = np.tile(init_deck, (n_decks, 1))
    rng = np.random.default_rng(seed)
    rng.permuted(decks, axis=1, out=decks)
    seeds = np.arange(seed, seed + n_decks)
    return decks, seeds


def store_decks(n_decks: int = 1000, seed: int = 50) -> None:
    """
    Stores generated decks with timestamped filenames
    ---
    Args: same as generate_decks()
    Returns: None
    """
    os.makedirs(PATH_DATA_DECKS, exist_ok=True)
    os.makedirs(PATH_DATA_SEEDS, exist_ok=True)
    MAX_DECKS_PER_FILE = 10000
    decks, seeds = gen_decks(n_decks, seed)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # calculate number of files needed
    num_files = (n_decks + MAX_DECKS_PER_FILE - 1) // MAX_DECKS_PER_FILE
    for file_num in range(num_files):
        start_idx = file_num * MAX_DECKS_PER_FILE
        end_idx = min((file_num + 1) * MAX_DECKS_PER_FILE, n_decks)
        # saving deck chunk
        deck_filename = f"{n_decks}_decks_{timestamp}_part{file_num+1}.npz"
        np.savez_compressed(
            os.path.join(PATH_DATA_DECKS, deck_filename),
            decks=decks[start_idx:end_idx]
        )
        # saving seed chunk
        seed_filename = f"seeds_{timestamp}_part{file_num+1}.json"
        with open(os.path.join(PATH_DATA_SEEDS, seed_filename), 'w') as f:
            json.dump(seeds[start_idx:end_idx].tolist(), f)
        print(f"Stored {end_idx-start_idx} decks in {deck_filename}")
    print(f"Finished storing all {n_decks} decks across {num_files} files")
    return None