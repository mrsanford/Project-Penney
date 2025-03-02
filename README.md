# **Project Penney Overview**

This version of Project Penney is a 3-bit implementation. The game works where Player 1 (P1) selects a three card length combination of red and black cards, represented as RED = 0 or BLACK = 1. The project is a simulation designed to visualize and analyze combination outcomes in order to (1) help Player 2 (P2) to exploit the advantage of picking second through minimizing loss, maximizing wins, or increasing the chances of a draw. 

### Features
- Deck shuffling and storing: the simulation has generated a set of easily reproducible and accessible seeds, which are used to shuffle the decks. The shuffled decks have been stored in .npz files in the [/data](https://github.com/mrsanford/Project-Penney/tree/main/data) folder. Considerations have been taking to allow for new decks to be either appended to existing ones, or for newly shuffled decks to be inputted into brand new files.
- Simulation techniques: all combinations (56 of 64 total combinations) of P1 and P2's choices are simulated on every shuffled deck. *The missing 8 are derived from P2 choosing the same combination as P1, and the statistics of all the combination win probabilities can be found [here](https://en.wikipedia.org/wiki/Penney%27s_game#/media/File:Penney_game_graphs.svg).
- Result tracking: tricks and cards are counted for both players; additionally, wins, ties, and unwon cards are counted.
- Visualizing: a master dataframe is outputted of all simulation results and heatmaps are generated of players' trick and card win percentages.

#### Disclaimer: this project is not a game rather it is a simulation and visualization tool to aid in optimizing 3-bit Penney's games. 

--- 

## **Quick Start Guide**
Beginning with this repository will require you cloning  and installing the dependencies. Note: this project has been managed with uv, and more information regarding uv setup and management can be found [here](https://docs.astral.sh/uv/getting-started/installation/). To simply view the project, clone the repository and run the script out of main.py. An alternative set up is below:

### Access the Directories and Constants
```
from src.helpers import P1_COMBOS, R, C, DATA_DIR, LATEST_RESULTS_FILE
```
### Generate the Shuffled Decks
```
from src.datagen import get_decks, store_decks
decks, seeds = get_decks(n_decks=1000,seed=42)
store_decks(decks, seeds, directory=DATA_DIR, append_file=False)
```
### Run the Simulation and Score
```
from src.processing import load_decks, simulate_combos,score_summarize
results = simulate_combos(decks,P1_COMBOS,P1_COMBOS)
score = score_summarize(results_file=LATEST_RESULTS_FILE)
```
### Visualize Outputs
```
from src.visualization import plot_heatmaps
plot_heatmaps(p2_trick_pct, p2_card_pct, save=True, show=True)
```
