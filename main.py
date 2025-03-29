from src.datagen import gen_decks, store_decks
from src.visualization import plot_results
from src.processing import load_decks
import numpy as np

def project_penney(n_decks: int = 10000, seed: int = 15):
    """
    Complete workflow: generates decks, stores them, loads existing ones,
    runs simulations, and visualizes the result as annotated heatmaps.
    """
    prev_decks = load_decks() # loading any previous decks stored
    new_decks, _ = gen_decks(n_decks=n_decks, seed=seed) # generating new decks
    # combining new and existing decks for full analysis
    if prev_decks.shape[0] == 0:
        all_decks = new_decks
    else:
        all_decks = np.vstack([prev_decks, new_decks])
    store_decks(n_decks=n_decks, seed=seed) # storing new decks 
    plot_results(all_decks) # run simulations and visualize win probabilities

if __name__ == '__main__':
    project_penney(n_decks=1000000, seed=1)
