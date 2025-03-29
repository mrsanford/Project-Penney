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
        np.ndarray of all combined decks
    """
    decks = []
    # finding all .npz files in the specified directory
    for file in glob.glob(os.path.join(data_dir, '*.npz')):
        # loading deck array from each .npz file
        with np.load(file) as data:
            decks.append(data['decks'])
     # returning empty array if no decks are found
    if not decks:
        print(f"[load_decks] No deck files found in {data_dir}. Returning empty array.")
        return np.empty((0, HALF_DECK_SIZE*2), dtype=int)
    # vertically stacking all loaded decks
    return np.vstack(decks)


def score_game(deck: np.ndarray, p1_combo: list, p2_combo: list) -> tuple:
    """
    Scores a single game between two players' combos in a deck
    ---
    Args:
        deck_str (np.ndarray) is the representation of the deck
        p1_combo, p2_combo (list) is P1, P2's combo pattern
    Returns:
        tuple with trick, card, and tie counts for both players
    """
    # instantiating counters and lengths
    p1_tricks_score = p2_tricks_score = 0
    p1_cards_score = p2_cards_score = 0
    pos = 0
    last_trick_end = 0
    combo_len = len(p1_combo)
    deck_len = len(deck)

    while pos <= deck_len - combo_len:
        # iterating through the deck using a sliding window
        window = deck[pos:pos + combo_len]
        # checking for player 1's combo match
        if np.array_equal(window, p1_combo):
            p1_tricks_score += 1
            trick_end = pos + combo_len - 1
            cards_won = trick_end - last_trick_end + 1
            p1_cards_score += cards_won
            last_trick_end = trick_end + 1 
            pos = trick_end + 1 # jumping past the matched combo
        # checking for player 2's combo match
        elif np.array_equal(window, p2_combo):
            p2_tricks_score += 1
            trick_end = pos + combo_len - 1
            cards_won = trick_end - last_trick_end + 1
            p2_cards_score += cards_won
            last_trick_end = trick_end + 1
            pos = trick_end + 1
        else:
            pos += 1 # moving window forward if no match found
    # checking for ties       
    trick_tie = int(p1_tricks_score == p2_tricks_score)
    card_tie = int(p1_cards_score == p2_cards_score)
    # returning final scores and any tie flags
    return (
        p1_tricks_score, p1_cards_score,
        p2_tricks_score, p2_cards_score,
        trick_tie, card_tie
    )
            

def simulate_games(decks: np.ndarray, p1_combo: list, p2_combo: list) -> tuple:
    """
    "Simulates the game on every deck in decks
    ---
    Args: same args as score_game()
    Returns: tuple containing lists of trick and card records
    """
    tricks_record = []
    cards_record = []

    # running score_game for each deck
    for deck in decks:
        (p1_tricks_score, p1_cards_score,
         p2_tricks_score, p2_cards_score, trick_tie, card_tie) = score_game(deck, p1_combo, p2_combo)
        # storing results for each game
        tricks_record.append((p1_tricks_score, p2_tricks_score, trick_tie))
        cards_record.append((p1_cards_score,p2_cards_score,card_tie))
    return tricks_record, cards_record


def calc_probability(decks:np.ndarray, p1_combo:list, p2_combo:list) -> list:
    """
    Calculates the win and draw percentages for both players, even though
    only P2 will ultimately be calculated
    ---
    Args: same parameters as simulate_games() and score_game()
    Returns: list of win and draw percentages
    """
    tricks, cards = simulate_games(decks, p1_combo, p2_combo)
    tricks_scores = np.array(tricks)
    cards_scores = np.array(cards)
    total_games = len(decks)

    # calculating win/tie percentages for trick scores
    p1_tricks_wins = np.sum(tricks_scores[:, 0] > tricks_scores[:, 1])
    p2_tricks_wins = np.sum(tricks_scores[:, 1] > tricks_scores[:, 0])
    trick_ties = np.sum(tricks_scores[:, 2] == 1)
    # calculating win/tie percentages for card scores
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
    # iterates through all possible combo matchups
    for p1_combo in ALL_COMBOS:
        for p2_combo in ALL_COMBOS:  
            if p1_combo == p2_combo:
                continue # skips invalid self-match
            # converting string combos to arrays of ints
            p1_combo_array = np.array(list(p1_combo), dtype=int)
            p2_combo_array = np.array(list(p2_combo), dtype=int)
            # calculating win probabilities
            (
                p1_trick_pct, p2_trick_pct, trick_tie_pct,
                p1_card_pct, p2_card_pct, card_tie_pct
            ) = calc_probability(decks, p1_combo_array, p2_combo_array)
            # storing results
            tricks_results.append((p1_combo, p2_combo, p1_trick_pct, p2_trick_pct, trick_tie_pct))
            cards_results.append((p1_combo, p2_combo, p1_card_pct, p2_card_pct, card_tie_pct))
    return tricks_results, cards_results