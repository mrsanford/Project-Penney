import numpy as np
from datetime import datetime
from pathlib import Path
import json
from src.helpers import HALF_DECK_SIZE, TO_LOAD_DIR, USED_SEEDS


def get_decks(
    n_decks: int = 1000, seed: int = 50, half_deck_size: int = HALF_DECK_SIZE
) -> tuple[np.ndarray, np.ndarray, int]:
    """
    Generates `n_decks` shuffled decks using NumPy.
    Returns:
        decks, seeds (np.ndarray): 2D array of shape (n_decks, num_cards)
        each row is a shuffled deck; array of seeds used to shuffle decks
    """
    init_deck = [0] * half_deck_size + [1] * half_deck_size
    decks = np.tile(init_deck, (int(n_decks), 1))
    rng = np.random.default_rng(seed)
    rng.permuted(decks, axis=1, out=decks)
    seeds = np.arange(seed, seed + n_decks, 1)
    return decks, seeds, n_decks


def store_decks(
    decks: np.ndarray,
    seeds: np.ndarray,
    n_decks: int,
    deck_dir: Path = TO_LOAD_DIR,
    seed_dir: Path = USED_SEEDS,
) -> None:
    """
    Stores shuffled decks with a datetime-based naming convention
    ---
    Args:
        decks, seeds (np.ndarray): 2D array of shuffled decks to store and
        array of seeds associated with the decks
        directory (Path): Target directory to store the files
    """
    MAX_DPF = 10000  # DPF = Decks Per File
    # checking file paths
    deck_dir.mkdir(parents=True, exist_ok=True)
    seed_dir.mkdir(parents=True, exist_ok=True)
    # preventing deck size from exceeding storage limit via splitting into multiple files
    if len(decks) > MAX_DPF:
        num_splits = (len(decks) // MAX_DPF) + (1 if len(decks) % MAX_DPF > 0 else 0)
        for i in range(num_splits):
            start_idx = i * MAX_DPF
            end_idx = min((i + 1) * MAX_DPF, len(decks))
            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )  # creating new timestamped file
            new_file = deck_dir / f"raw_{n_decks}_decks_{timestamp}_part{i + 1}.npz"
            np.savez_compressed(
                new_file, decks=decks[start_idx:end_idx], seeds=seeds[start_idx:end_idx]
            )
            # saving seeds to JSON file
            seed_file = seed_dir / f"seeds_{timestamp}_part{i + 1}.json"
            with open(seed_file, "w") as f:
                json.dump(seeds[start_idx:end_idx].tolist(), f)
            # print checks
            print(f"Stored new deck file: {new_file}")
            print(f"Stored seed file: {seed_file}")
    else:
        # creating single file if decks are within the limit
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_file = deck_dir / f"raw_{n_decks}_decks_{timestamp}.npz"
        np.savez_compressed(new_file, decks=decks, seeds=seeds)
        # saving seeds to a JSON file in seed directory
        seed_file = seed_dir / f"seeds_{timestamp}.json"
        with open(seed_file, "w") as f:
            json.dump(seeds.tolist(), f)
        print(f"Stored new deck file: {new_file}")
        print(f"Stored seed file: {seed_file}")
