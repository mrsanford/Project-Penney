import numpy as np
import pandas as pd


def score_probability(results_df: pd.DataFrame) -> tuple[np.ndarray,np.ndarray]:
    """
    Computes probability matrices for tricks and cards based on P1_index and P2_index.
    ---
    Args: results_df (pd.DataFrame) contains game results.
    Returns:
        np.ndarray: 3D NumPy array with shape (8, 8, 2) where:
                    - `result[:,:,0]` = Trick win probabilities for P2
                    - `result[:,:,1]` = Card win probabilities for P2
    """
    # initializing probability matrices for tricks and cards (wins & draws)
    trick_probs = np.zeros((8, 8, 2))
    card_probs = np.zeros((8, 8, 2))

    # Extract relevant columns as NumPy arrays
    P1_indices = results_df["P1_index"].to_numpy()
    P2_indices = results_df["P2_index"].to_numpy()
    P1_tricks = results_df["P1_tricks"].to_numpy()
    P2_tricks = results_df["P2_tricks"].to_numpy()
    P1_cards = results_df["P1_cards"].to_numpy()
    P2_cards = results_df["P2_cards"].to_numpy()
    Trick_Ties = results_df["trick_tie"].to_numpy()
    Card_Ties = results_df["card_tie"].to_numpy()

    for P1 in range(8):
        for P2 in range(8):
            mask = (P1_indices == P1) & (P2_indices == P2)
            subset_size = mask.sum()
            if subset_size > 0:
                p2_trick_wins = np.sum(P2_tricks[mask] > P1_tricks[mask])
                p2_card_wins = np.sum(P2_cards[mask] > P1_cards[mask])
                trick_ties = np.sum(Trick_Ties[mask])
                card_ties = np.sum(Card_Ties[mask])
                
                # P2 trick win probability
                trick_probs[P1, P2, 0] = p2_trick_wins / subset_size
                # Trick tie probability
                trick_probs[P1, P2, 1] = trick_ties / subset_size
                # P2 Card win probability
                card_probs[P1, P2, 0] = p2_card_wins / subset_size
                # Card tie probability
                card_probs[P1, P2, 1] = card_ties / subset_size
    return trick_probs, card_probs
