import seaborn as sns
import pandas as pd
from src.helpers import ALL_COMBOS, PLOTS_DIR


def plot_heatmaps(trick_matrix: pd.DataFrame, card_matrix: pd.DataFrame, n_decks: int):
    """
    Creates heatmaps for visualizing the probability results for tricks and cards
    ---
    Args:
        trick_array (np.ndarray): 8x8 array with probabilities of P2 winning tricks.
        card_array (np.ndarray): 8x8 array with probabilities of P2 winning cards.
        n_decks (int): Number of decks used for generating probabilities.
    Returns: None
    """
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)  # checking output directory exists

    # plotting trick heatmap
    trick_title = f"Probability of Player Winning \n on Tricks \nN = {n_decks}"
    trick_plt = sns.heatmap(
        trick_matrix,
        cmap="coolwarm",
        cbar=False,
        annot=True,
        linewidths=0.5,
        xticklabels=ALL_COMBOS,
        yticklabels=ALL_COMBOS,
    )
    trick_plt.set_title(trick_title)
    plot_title = f"Heatmap for the {trick_title}"
    # plotting card heatmap
    card_title = f"Probability of Player Winning \n on Cards \nN = {n_decks}"
    card_plt = sns.heatmap(
        card_matrix,
        cmap="coolwarm",
        cbar=False,
        annot=True,
        linewidths=0.5,
        xticklabels=ALL_COMBOS,
        yticklabels=ALL_COMBOS,
    )
    card_plt.set_title(card_title)
    plot_title2 = f"Heatmap for the {card_title}"

    # making file paths and saving the plots
    trick_figure_path = PLOTS_DIR / plot_title
    card_figure_path = PLOTS_DIR / plot_title2
    trick_fig = trick_plt.get_figure()
    card_fig = card_plt.get_figure()
    trick_fig.savefig(trick_figure_path, bbox_inches="tight", facecolor="white")
    card_fig.savefig(card_figure_path, bbox_inches="tight", facecolor="white")

    return trick_plt, card_plt
