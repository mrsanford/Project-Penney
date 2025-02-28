import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.datagen import (
    P1_COMBOS,
    get_decks,
    latest_seed,
    latest_deck,
    store_decks,
    load_decks,
    count_tricks,
    count_cards,
    simulate_combos,
    score_game,
    plot_heatmaps,
)
# from src.helpers import PATH_INFO


def main():
    # Generating shuffled decks and getting the seeds
    decks, seeds = get_decks(n_decks=1000, seed=42)
    # Storing the shuffled decks to a file
    store_decks(decks, seeds, filepath="./data", append_file=True)
    # Loading the latest deck from the stored files
    loaded_decks = load_decks("./data")
    # Running the trick count simulation
    sample_deck = loaded_decks[0]
    P1_combo = P1_COMBOS[0]  # First combo for Player 1
    P2_combo = P1_COMBOS[1]
    P1_tricks, P2_tricks = count_tricks(sample_deck, P1_combo, P2_combo)
    # print(f"Player 1 tricks: {P1_tricks}, Player 2 tricks: {P2_tricks}")
    # Running the card count simulation
    P1_cards, P2_cards = count_cards(sample_deck, P1_combo, P2_combo)
    # print(f"Player 1 cards: {P1_cards}, Player 2 cards: {P2_cards}")
    # Simulating combos across multiple decks
    results = simulate_combos(
        deck_file="./data", P1_combos=P1_COMBOS, P2_combos=P1_COMBOS
    )
    # Scoring the results of the game
    score = score_game(results)
    print(f"Game Score: {score}")
    # Visualizing the results for trick and card win percentages
    p1_trick_pct = np.random.rand(len(P1_COMBOS), len(P1_COMBOS)) * 100
    p1_card_pct = np.random.rand(len(P1_COMBOS), len(P1_COMBOS)) * 100
    plot_heatmaps(p1_trick_pct, p1_card_pct)


if __name__ == "__main__":
    main()
