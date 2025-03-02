import numpy as np
from src.helpers import P1_COMBOS
from src.helpers import DATA_DIR
from src.datagen import get_decks, store_decks
from src.processing import (
    load_decks,
    count_cards,
    find_tricks,
    simulate_combos,
    score_summarize,
)
from src.visualization import plot_heatmaps


# default testing
def main():
    # deck shuffling, seed generation, and storage
    decks, seeds = get_decks(n_decks=1000, seed=42)
    store_decks(decks, seeds, directory=DATA_DIR, append_file=True)
    # loading data and simulating
    loaded_decks = load_decks(DATA_DIR)
    # running trick and card simulations
    sample_deck = loaded_decks[0]
    P1_combo = P1_COMBOS[0]
    P2_combo = P1_COMBOS[1]
    P1_tricks, P2_tricks = find_tricks(sample_deck, P1_combo, P2_combo)
    P1_cards, P2_cards = count_cards(sample_deck, P1_combo, P2_combo)
    results = simulate_combos(
        decks=sample_deck, P1_combos=P1_COMBOS, P2_combos=P1_COMBOS
    )
    # scoring the results
    score = score_summarize(results)
    # visualization
    p2_trick_pct = np.random.rand(len(P1_COMBOS), len(P1_COMBOS)) * 100
    p2_card_pct = np.random.rand(len(P1_COMBOS), len(P1_COMBOS)) * 100
    plot_heatmaps(p2_card_pct, p2_trick_pct)


if __name__ == "__main__":
    main()
