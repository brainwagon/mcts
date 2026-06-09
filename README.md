# MCTS & Yahtzee AI: An AI Teaching Experiment

This repository documents an experiment in using Monte Carlo Tree Search (MCTS) to build game solvers for stochastic games like Blackjack and Yahtzee.

The entire project—including the Python source code, the html-based lessons, and this documentation—was generated as an experiment using the `/teach` skill created by Matt Pocock ([Learn Anything with my /teach skill](https://www.aihero.dev/learn-anything-with-my-teach-skill)).

## The Experiment

The repository begins as an educational exploration of the MCTS mechanics: Selection, Expansion, Simulation, and Backpropagation. It then applies these mechanics to simple domains like Blackjack, where we compare MCTS performance against pure Dynamic Programming solvers.

The experiment truly takes off when we attempt to build an expert-level Yahtzee engine using MCTS. Despite the AI's confident theoretical setup, the engine's actual empirical performance fell vastly below expectations. We then debug the architecture, migrating from an **Open-Loop** MCTS to an **ExpectiMax (Closed-Loop)** MCTS, uncovering deep insights into the limitations of standard MCTS when dealing with environments that have massively wide chance nodes.

## Repository Contents

* **`lessons/`**: A series of HTML files documenting the learning journey, architecture decisions, and benchmarking results.
* **`index.html`**: A clean, GitHub Pages-ready index file that links to all lessons and source code.
* **`glossary.html`**: A glossary of terms covering MCTS mechanics, Markov Decision Processes, and Dynamic Programming.
* **`yahtzee_mcts.py`**: The initial (flawed) Open-Loop MCTS implementation for Yahtzee.
* **`yahtzee_expectimax_mcts.py`**: The corrected Closed-Loop ExpectiMax implementation.
* **`blackjack_mcts.py`**: An MCTS solver for Blackjack.
* **`blackjack_dp.py`**: A Dynamic Programming (Value Iteration) solver for Blackjack.

## Disclaimer

I have **not** reviewed the underlying generated information for mathematical or theoretical accuracy. Proceed with a healthy dose of skepticism! This repository serves primarily as an incredibly entertaining meta-study on the disconnect between an LLM's textbook theoretical knowledge and its practical empirical capabilities in complex, statistically noisy domains.

## License

This project is released into the public domain. See the [LICENSE](LICENSE) file for details.
