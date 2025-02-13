import numpy as np
# from src.datagen import PATH_DATA

HALF_DECK_SIZE = 5


def get_decks(
    seed: int, n_decks: int, half_deck_size: int = HALF_DECK_SIZE
) -> tuple[np.ndarray, np.ndarray]:
    """Efficiently generate `n_decks` shuffled decks using NumPy.
    Returns: decks (np.ndarray): 2D array of shape (n_decks, num_cards), each row is a shuffled deck.
    """
    init_deck = [0] * half_deck_size + [1] * half_deck_size
    decks = np.tile(init_deck, (n_decks, 1))
    rng = np.random.default_rng(seed)
    rng.permuted(decks, axis=1, out=decks)
    return decks


def store_decks(decks: np.ndarray, seeds: np.ndarray, filename: str) -> None:
    np.savez_compressed(filename, decks=decks, seeds=seeds)


# Write a function that stores the data generated by get_added()
# Make sure you can generate some decks, and then generate some additional decks
## without losing track of the random seeds used
# Make sure you can duplicate your results
# ^^ Due by next class
