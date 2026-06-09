# Learning Record 0004: Backpropagation and the Full Loop

**Date:** 2025-04-05

## What Was Learned
- Backpropagation walks from leaf to root, incrementing $n$ and adding $w$ at each node.
- Reward sign alternates at each tree level for two-player zero-sum games ($+1 \rightarrow -1$).
- Fixed-perspective reward (no sign flip) is simpler but requires the reward to always be from the same player's viewpoint.
- The complete `mcts_search` function: build root, loop iterations, return best action.
- The state object must implement exactly six methods: `legal_moves`, `is_terminal`, `apply`, `clone`, `reward`, `last_action`.
- MCTS is game-agnostic — swap the state object to change the game.

## Key Insights
- The draw ($+0.5$) case needs special handling with alternating-sign backpropagation.
- The clean interface between generic MCTS and game-specific state is the key architectural insight.

## Next Suggested Topic
Lesson 0005: Stochastic Games (handling randomness/dice).