# **Project Penney Overview**

This version of Project Penney is a 3-bit implementation. The game works where Player 1 (P1) selects a three card length combination of red and black cards, represented as RED = 0 or BLACK = 1.
This is not actually a Penney game, rather it is a simulation which visualizes all combination outcomes on a set of 'randomly' shuffled decks so we can determine a play strategy for Player 2 (P2) since they are at the advantage from picking second. We want to see which combinations would maximize our wins/mimizes our losses. For P1, it is also seeing which combinations would be more likely to force a draw.

The script generates a set of 'randomly shuffled' decks, which have been designed so testing is replicable and easily accessible (the seeds used for each shuffled deck has been stored). The shuffled decks are saved to .npz files in the ./data folder in this repository. The store_decks() function has been designed to provide the option to append newly generated decks to either the most recent file (indexed by number) or to create a new file of generated decks. It is an attempt at handling the generation of large quantities of shuffled decks more gracefully and avoids shuffled decks on replicated seeds.

The script simulates most combinations of P1 and P2 (of 64 total combinations - 8 possible combos if P1 and P2 picked the same combination = 56 combinations simulated) on every shuffled deck. It loads the data from the most recent file in [/data](url). It counts cards and tricks for P1 and P2 in order to calculate wins; moreover, it will (hopefully) gracefully track unwon cards and handle ties. There are two 'outputs' which include a master dataframe, which holds the running counts of all out simulations and a heatmap derived from this data, which visualizes all the combinations.

--- 

## **Quick Start Guide**
In addition to the necessary versions and dependencies, the project is maintained using uv. Please check their website for more information regarding setup. To simply view the project, clone the repository and:
'''
print('testing')
'''
Then check the outputs in /reports.
