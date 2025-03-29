import numpy as np
import os
import glob
from src.helpers import ALL_COMBOS, PATH_DATA, HALF_DECK_SIZE


def load_decks(data_dir: str= PATH_DATA) -> np.ndarray:
    """
    Loads decks as binary arrays
    ---
    Args:
        data_dir (str) is the target path to the data folder
    Returns:
        list of strings representing decks
    """
    decks = []
    for file in glob.glob(os.path.join(data_dir, '*.npz')):
        with np.load(file) as data:
            decks.append(data['decks'])
    if not decks:
        print(f"[load_decks] No deck files found in {data_dir}. Returning empty array.")
        return np.empty((0, HALF_DECK_SIZE*2), dtype=int)
    return np.vstack(decks)


def score_game(deck: np.ndarray, p1_combo: list, p2_combo: list) -> tuple:
    """
    Scores a single game between two players' combos in a deck
    ---
    Args:
        deck_str (np.ndarray) is the representation of the deck
        p1_combo, p2_combo (list) is P1, P2's combo pattern
    Returns:
        tuple with trick and card counts for both players
    """
    p1_tricks_score = p2_tricks_score = p1_cards_score = p2_cards_score = 0 
    pos = 0
    combo_len = len(p1_combo)
    deck_len = len(deck)
    last_p1_match = -1
    last_p2_match = -1

    while pos <= deck_len - combo_len:
        current_window = deck[pos:pos+combo_len]
        p1_match = np.array_equal(current_window, p1_combo)
        p2_match = np.array_equal(current_window, p2_combo)
        if p1_match:
            p1_tricks_score += 1
            # counts cards since last match + combo length
            if last_p1_match == -1:
                p1_cards_score += pos + combo_len
            else:
                p1_cards_score += (pos - last_p1_match) + combo_len
            last_p1_match = pos
            pos += 1  # allowing overlaps and not just incremental, every 3 cards
        elif p2_match:
            p2_tricks_score += 1
            if last_p2_match == -1:
                p2_cards_score += pos + combo_len
            else:
                p2_cards_score += (pos - last_p2_match) + combo_len
            last_p2_match = pos
            pos += 1
        else:
            pos += 1
    trick_tie = 1 if p1_tricks_score == p2_tricks_score else 0
    card_tie = 1 if p1_cards_score == p2_cards_score else 0
    return p1_tricks_score, p1_cards_score, p2_tricks_score, p2_cards_score, trick_tie, card_tie
            

def simulate_games(decks: np.ndarray, p1_combo: list, p2_combo: list) -> tuple:
    """
    "Simulates the game on every deck in decks
    ---
    Args: same args as score_game()
    Returns: tuple containing lists of trick and card records
    """
    tricks_record = []
    cards_record = []
    for deck in decks:
        (p1_tricks_score, p1_cards_score,
         p2_tricks_score, p2_cards_score, trick_tie, card_tie) = score_game(deck, p1_combo, p2_combo)
        tricks_record.append((p1_tricks_score, p2_tricks_score, trick_tie))
        cards_record.append((p1_cards_score,p2_cards_score,card_tie))
    return tricks_record, cards_record


def calc_probability(decks:np.ndarray, p1_combo:list, p2_combo:list) -> list:
    """
    Calculates the win and draw percentages for both players, even though
    only P2 will ultimately be calculated
    ---
    Args: same parameters as simulate_games()
    Returns: list of win and draw percentages
    """
    tricks, cards = simulate_games(decks, p1_combo, p2_combo)
    tricks_scores = np.array(tricks)
    cards_scores = np.array(cards)
    total_games = len(decks)

    # trick scores
    p1_tricks_wins = np.sum(tricks_scores[:, 0] > tricks_scores[:, 1])
    p2_tricks_wins = np.sum(tricks_scores[:, 1] > tricks_scores[:, 0])
    trick_ties = np.sum(tricks_scores[:, 2] == 1)
    # card scores
    p1_cards_wins = np.sum(cards_scores[:, 0] > cards_scores[:, 1])
    p2_cards_wins = np.sum(cards_scores[:, 1] > cards_scores[:, 0])
    card_ties = np.sum(cards_scores[:, 2] == 1)

    return [
        p1_tricks_wins / total_games,
        p2_tricks_wins / total_games,
        trick_ties / total_games,
        p1_cards_wins / total_games,
        p2_cards_wins / total_games,
        card_ties / total_games,
    ]


def aggregate_results(decks: np.ndarray) -> tuple[list, list]:
    """
    Runs simulations for all valid P1 vs P2 combo matchups excluding
    invalid matchups
    ---
    Args:
        decks (np.ndarray): all decks
    Returns
        tuple of two lists: (trick_results, cards_results)
    """
    tricks_results = []
    cards_results = []
    for p1_combo in ALL_COMBOS:
        for p2_combo in ALL_COMBOS:  
            if p1_combo == p2_combo:
                continue
            p1_combo_array = np.array(list(p1_combo), dtype=int)
            p2_combo_array = np.array(list(p2_combo), dtype=int)
            (
                p1_trick_pct, p2_trick_pct, trick_tie_pct,
                p1_card_pct, p2_card_pct, card_tie_pct
            ) = calc_probability(decks, p1_combo_array, p2_combo_array)
            tricks_results.append((p1_combo, p2_combo, p1_trick_pct, p2_trick_pct, trick_tie_pct))
            cards_results.append((p1_combo, p2_combo, p1_card_pct, p2_card_pct, card_tie_pct))
    return tricks_results, cards_results