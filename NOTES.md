# Teaching Notes: MCTS Game Engine

## User Preferences
- Wants to understand MCTS deeply enough to *design a complete implementation* — not just use a library.
- Primary interest: games with high branching factor and randomness.
- Explicitly postponing neural networks / deep RL.
- Prefers concrete tradeoffs analysis over abstract theory.
- Responds well to architectural/design-oriented framings.
- Wants MathJax-rendered mathematics in lessons.

## Key Terms Defined So Far
- **MCTS** — Monte Carlo Tree Search
- **UCT** — Upper Confidence Bound applied to Trees
- **Selection/Expansion/Simulation/Backpropagation** — the four pillars
- **$C_p$** — Exploration constant in UCT (default ~1.414)
- **Tree policy** — the loop that descends from root to a frontier node using UCT
- **Robust child** — the most-visited child, used as final move selection
- **Chance node** — tree node representing a random event
- **Transposition table** — hash-based node merging for equivalent states
- **Virtual loss** — artificial visit increment to coordinate parallel threads
- **Root parallelism / Tree parallelism** — two approaches to multi-threaded MCTS

## Zone of Proximal Development (Complete)
- Lesson 0001 ✅: UCT formula with interactive $C_p$ tuning
- Lesson 0002 ✅: Implementing Selection in code — `MCTSNode`, `uct_select_child`, `tree_policy`, `best_move`
- Lesson 0003 ✅: Expansion and Simulation — adding nodes, running rollouts
- Lesson 0004 ✅: Backpropagation and the full four-phase loop
- Lesson 0005 ✅: Stochastic games — chance nodes, determinize approach
- Lesson 0006 ✅: Memory, parallelism, and advanced tradeoffs