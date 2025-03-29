# **Project Penney Overview**

This version of Project Penney is a 3-bit simulation where two players compete by selecting sequences of three binary playing card values:
- RED = 0
- BLACK = 1

The goal of the project is to simulate *n* Penney games and to visualize player combination probabilities. Each simulation shuffles a deck of 52 cards (26 red, 26 black), and the game is played by searching for each player's sequence within this shuffled deck. **The player whose sequence appears first in the deck will will a trick.**

Points are awarded in **two ways:**
- **Tricks**: When a player's sequence appears in the deck, a trick is earned. Each trick is always work +1 point each.
- **Cards**: The number of cards between the last match and the current match (inclusive) is added to the player's card score. Cards will always be awarded when a trick is won, and the minimum number of won cards will always be three (equivalent to the length of the combination).

#### Game Mechanics:

Since Player 1 (P1) selectes their sequence, Player 2 (P2) has a strategic advantage in selecting a counter-sequence to maximize their probability of winning or at least forcing a draw. This advantage is represented in the selection formula:
- If P1 chooses ```[1, 2, 1]```, the optimal response for P2 is ```[-2, 1, 2]```

    
## **Features**

### Deck Generation and Storage
Efficient generation of large numbers of shuffled decks and reproducible seeds. Decks are saved in compressed ```.npz``` files and stored in the decks subfolder within its parent ```/data``` folder. Per-file prefixes indicating the actual number of contained decks. Decks with lengths exceeding >10000 decks are automatically split across multiple files to accomodate GitHub's storage limits.

### Game Simulation
All 56 valid combinations of P1 vs. P2 (omitting self-matches) are simulated across every shuffled deck. More information regarding statistics of combination win probabilties can be found [here](https://en.wikipedia.org/wiki/Penney%27s_game#/media/File:Penney_game_graphs.svg). Win/draw probabilities for both tricks and cards are computed and stored. 

### Result Aggregation and Heatmap Visualization
Result matrices are generated and visualized as heatmaps showing win/draw probabilities of P2 across every valid matchup.

### Modular Pipeline
Each module (deck generation, processing, visualization) has been compartmentalized and is independently testable. 

#### Disclaimer: this project is not a game rather it is a simulation and visualization tool to aid in optimizing 3-bit Penney's games. 


## **File Organization**

```
project-root/
│
├── /src/
│   ├── datagen.py        # generates and stores shuffled decks
│   ├── helpers.py        # constants, utility decorators, paths
│   ├── processing.py     # game simulation logic
│   └── visualization.py  # matrix formatting and heatmap generation
│
├── /data/
│   ├── decks/            # stored shuffled decks (.npz) by chunk
│   └── seeds/            # JSON files of RNG seeds used per deck set
│
├── /plots/               # Win/Draw trick and card percentage heatmaps
└── README.md
```


## **Quick Start Guide**

Beginning with this repository will require you cloning  and installing the dependencies. Note: this project has been managed with uv, and more information regarding uv setup and management can be found [here](https://docs.astral.sh/uv/getting-started/installation/). To simply view the project, clone the repository and run the script out of main.py. An alternative set up is below:

### Generate and Store Shuffled Decks
```
from src.datagen import store_decks

# Generates and stores 50000 decks across 5 files of 10k decks each
store_decks(n_decks=50000, seed=15)
```

### Load and Simulate All Matchups
```
from src.processing import load_decks, aggregate_results

decks = load_decks()
trick_results, card_results = aggregate_results(decks)
```

### Visualize Results
```
from src.visualization import plot_results, get_n_decks()

# automatically reads decks and generates heatmaps
plot_results(decks)
```

## **Output**
Heatmaps will be saved to ```/plots``` as:
* ```Card_Heatmap.png```
* ```Trick_Heatmap.png```

Each cell will show P2's Win(Draw) percentages, rounded to the nearest whole number:
* e.g. ```85(5)``` corresponds to **85% win, 5% draw**
