import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
from src.helpers import P1_COMBOS, R
from src.helpers import PLOTS_DIR


def plot_heatmaps(p2_trick_pct, p2_card_pct, save: bool = True, show: bool = False):
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    mask = np.eye(len(P1_COMBOS), dtype=bool)
    cmap = sns.color_palette("coolwarm", as_cmap=True)
    cmap = cmap.with_extremes(bad="lightgrey")
    labels = ["".join(["R" if x == R else "B" for x in combo]) for combo in P1_COMBOS]

    fig, axes = plt.subplots(1, 2, figsize=(18, 8), dpi=100)

    heatmap_kws = {
        "annot": True,
        "fmt": ".1f",
        "xticklabels": labels,
        "yticklabels": labels,
        "vmin": 0,
        "vmax": 100,
        "cbar_kws": {"shrink": 0.8},
        "cmap": cmap,
        "mask": mask,
    }
    sns.heatmap(p2_trick_pct, ax=axes[0], **heatmap_kws)
    axes[0].set_title("P2 Trick Win Probability (%)")
    axes[0].set_xlabel("Player 1 Combination")
    axes[0].set_ylabel("Player 2 Combination")

    sns.heatmap(p2_card_pct, ax=axes[1], **heatmap_kws)
    axes[1].set_title("P2 Card Win Probability (%)")
    axes[1].set_xlabel("Player 1 Combination")
    axes[1].set_ylabel("Player 2 Combination")
    plt.tight_layout()
    if save:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        plot_path = PLOTS_DIR / f"heatmap_{timestamp}.png"
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        print(f"Saved heatmap to: {plot_path}")
    if show:
        plt.show()
    else:
        plt.close()
