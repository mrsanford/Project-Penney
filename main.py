from src.helpers import ALL_COMBOS, TO_LOAD_DIR
from src.datagen import get_decks, store_decks
from src.processing import load_decks, find_sequences, simulate_games
from src.scoring import score_summarize
from src.visualization import plot_heatmaps


def main():
    # deck shuffling, seed generation, and storage
    decks, seeds = get_decks(n_decks=100, seed=42)
    store_decks(decks, seeds, directory=TO_LOAD_DIR, append_file=True)
    # loading data and simulating
    loaded_decks, latest_file = load_decks()
    # running trick and card simulations
    sample_deck = loaded_decks[0]
    P1_combo = ALL_COMBOS[0]
    P2_combo = ALL_COMBOS[1]
    P1_cards, P2_cards, P1_tricks, P2_tricks = find_sequences(
        sample_deck, P1_combo, P2_combo
    )
    results = simulate_games(
        decks=loaded_decks, P1_combos=ALL_COMBOS, P2_combos=ALL_COMBOS
    )
    # scoring the results
    trick_win_prob, card_win_prob = score_summarize()
    # visualization
    plot_heatmaps(trick_win_prob, card_win_prob)


if __name__ == "__main__":
    main()
