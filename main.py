from src.datagen import gen_decks, store_decks
from src.visualization import plot_results
from src.processing import load_decks, score_game
import numpy as np

def project_penney(n_decks: int = 10000, seed: int = 15):
    """
    Complete workflow: generates decks, stores them, loads existing ones,
    runs simulations, and visualizes the result as annotated heatmaps.
    """
    # loading previously stored decks (can be empty)
    prev_decks = load_decks()
    # generating new decks
    new_decks, _ = gen_decks(n_decks=n_decks, seed=seed)
    # combining all decks
    if prev_decks.shape[0] == 0:
        all_decks = new_decks
    else:
        all_decks = np.vstack([prev_decks, new_decks])
    # optional: saving new ones
    store_decks(n_decks=n_decks, seed=seed)
    
    # plotting results using all decks, showing total deck count in title
    plot_results(all_decks)

if __name__ == '__main__':
    project_penney(n_decks=1000000, seed=1)
