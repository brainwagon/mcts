# Learning Record 0001: MCTS Overview & Four Pillars

**Date:** 2025-04-05

## What Was Learned
- MCTS is a best-first, anytime search algorithm that uses random sampling instead of exhaustive search.
- The four-phase cycle: Selection → Expansion → Simulation → Backpropagation.
- How MCTS naturally handles high branching factors ("combinatorial explosion") by focusing compute on promising branches.

## Key Insights
- MCTS does not need a heuristic evaluation function for non-terminal states (unlike Minimax/Alpha-Beta), which makes it powerful for games where good heuristics are hard to define.
- The tradeoff between exploration and exploitation is controlled by the UCT formula, not hard-coded.
- "Anytime" property means you can run as many iterations as time allows and get the best answer available.

## Questions to Revisit
- How exactly does UCT balance exploration vs. exploitation quantitatively?
- How are chance nodes (dice rolls) inserted into the tree structure?

## Next Suggested Topic
Lesson 0001: The UCT Selection Formula — deriving, tuning, and implementing the core of the search.