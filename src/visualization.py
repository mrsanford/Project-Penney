import numpy as np
import os
import glob
import re
import matplotlib.pyplot as plt
from src.helpers import ALL_COMBOS, PATH_DATA_DECKS
from src.processing import aggregate_results


def get_n_decks(path: str = PATH_DATA_DECKS) -> int:
    """
    Scans all stored deck files and adds up the prefix deck counts
    ---
    Args: path (str)
    Returns: int of the total decks
    """
    total_num_decks = 0
    pattern = os.path.join(path, '*_decks_*_part*.npz')
    for file in glob.glob(pattern):
        filename = os.path.basename(file)
        match = re.match(r'^(\d+)_decks_', filename)
        if match:
            total_num_decks += int(match.group(1))
    return total_num_decks


def prep_heatmaps(decks: np.ndarray) -> dict[str, np.ndarray]:
    """
    Preps the heatmap matrices of win/draw percentages for both
    tricks and cards
    Note: created framework for P1 if you want to find P1
    ---
    Args:
        decks (np.ndarray) is the array of decks to evaluate
    Results:
        dict[str, np.ndarray]: dictionary of six 8x8 matrices 
    """
    # running full scoring simulation
    tricks_results, cards_results = aggregate_results(decks)

    # creating empty 8x8 matrices for all results
    shape = (len(ALL_COMBOS), len(ALL_COMBOS))
    tricks_matrix_p1 = np.full(shape, np.nan)
    tricks_matrix_p2 = np.full(shape, np.nan)
    tricks_matrix_tie = np.full(shape, np.nan)
    cards_matrix_p1 = np.full(shape, np.nan)
    cards_matrix_p2 = np.full(shape, np.nan)
    cards_matrix_tie = np.full(shape, np.nan)

    # indexing for combo placement in matrix
    combo_to_index = {combo: i for i, combo in enumerate(ALL_COMBOS)}
    
    # putting trick results into the matrices
    for p1_combo, p2_combo, p1_trick_pct, p2_trick_pct, trick_tie_pct in tricks_results:
        row = combo_to_index[p1_combo]
        col = combo_to_index[p2_combo]
        tricks_matrix_p1[row, col] = p1_trick_pct
        tricks_matrix_p2[row, col] = p2_trick_pct
        tricks_matrix_tie[row, col] = trick_tie_pct
    # putting card results into the matrices
    for p1_combo, p2_combo, p1_card_pct, p2_card_pct, card_tie_pct in cards_results:
        row = combo_to_index[p1_combo]
        col = combo_to_index[p2_combo]
        cards_matrix_p1[row, col] = p1_card_pct
        cards_matrix_p2[row, col] = p2_card_pct
        cards_matrix_tie[row, col] = card_tie_pct
    return {
        'tricks_p1': tricks_matrix_p1,
        'tricks_p2': tricks_matrix_p2,
        'tricks_tie': tricks_matrix_tie,
        'cards_p1': cards_matrix_p1,
        'cards_p2': cards_matrix_p2,
        'cards_tie': cards_matrix_tie
    }


def plot_results(decks: np.ndarray) -> None:
    """
    Plots annotated heatmaps for P2 Win(Draw)
    probabilities on tricks and cards
    ---
    Args:
        decks (np.ndarray) are the  decks to analyze.
    Returns: None
    """
    ALL_COMBOS_COLOR = ['RRR', 'RRB', 'RBR', 'RBB', 'BRR', 'BRB', 'BBR', 'BBB']
    num_combos = len(ALL_COMBOS_COLOR)
    results = prep_heatmaps(decks)

    # greying out diagonal (where P1 == P2)
    for i in range(num_combos):
        results['tricks_p2'][i, i] = np.nan
        results['tricks_tie'][i, i] = np.nan
        results['cards_p2'][i, i] = np.nan
        results['cards_tie'][i, i] = np.nan

    def format_matrix(win_matrix:  np.ndarray, tie_matrix:  np.ndarray) -> np.ndarray:
        """
        Formatting the matrix to put wins and ties on together
        ---
        Args:
            win_matrix (np.ndarray) is win percentage matrix
            tie_matrix (np.ndarray) is tie percentage matrix
        Return:
            np.ndarray matrix of formatted strings
        """
        formatted = np.empty(win_matrix.shape, dtype=object)
        for i in range(win_matrix.shape[0]):
            for j in range(win_matrix.shape[1]):
                if np.isnan(win_matrix[i, j]):
                    formatted[i, j] = ""
                else:
                    win_pct = f"{100 * win_matrix[i, j]:.0f}"
                    tie_pct = f"{100 * tie_matrix[i, j]:.0f}"
                    formatted[i, j] = f"{win_pct}({tie_pct})"
        return formatted

    def plot_heatmap(data_matrix: np.ndarray, annotations: np.ndarray, title: str) -> plt.Figure:
        """
        Plots single annotated heatmap
        --
        Args:
            data_matrix (np.ndarray): win percentage matrix
            annotations (np.ndarray): matrix of formatted strings
            title (str): title of plot
        Returns: the figure
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        cmap = plt.cm.Greens
        cmap = cmap.copy()
        cmap.set_bad(color='lightgrey')
        masked_matrix = np.ma.masked_invalid(data_matrix)
        cax = ax.imshow(masked_matrix, cmap=cmap, vmin=0, vmax=1)

        ax.set_xticks(np.arange(num_combos))
        ax.set_yticks(np.arange(num_combos))
        ax.set_xticklabels(ALL_COMBOS_COLOR)
        ax.set_yticklabels(ALL_COMBOS_COLOR)
        ax.set_xlabel("P2 Choice")
        ax.set_ylabel("P1 Choice")

        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        for i in range(num_combos):
            for j in range(num_combos):
                if annotations[i, j] != "":
                    ax.text(j, i, annotations[i, j], ha="center", va="center", color="black", fontsize=8)
        ax.set_title(title)
        plt.tight_layout()
        return fig
    # getting the number of decks for the titles
    num_decks = get_n_decks()
    # creating formatted text for annotations
    cards_formatted = format_matrix(results['cards_p2'], results['cards_tie'])
    tricks_formatted = format_matrix(results['tricks_p2'], results['tricks_tie'])
    # plotting and showing both heatmaps
    fig1 = plot_heatmap(
        results['cards_p2'], cards_formatted,
        f"Player 2's Win(Draw) Probabilities \n on Cards \n on {num_decks:,} Decks")
    fig2 = plot_heatmap(
        results['tricks_p2'], tricks_formatted,
        f"Player 2's Win(Draw) Probabilities \n on Tricks \n on {num_decks:,} Decks"
    )
    fig1.savefig(f"plots/Card_Heatmap.png", dpi=300)
    fig2.savefig(f"plots/Trick_Heatmap.png", dpi=300)
