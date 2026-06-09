# Learning Record 0002: Implementing Selection in Code

**Date:** 2025-04-05

## What Was Learned
- The `MCTSNode` data structure with `visits`, `wins`, `children`, `_untried_moves`.
- `uct_select_child()` implements the UCT formula with a short-circuit for unvisited children.
- `tree_policy()` is the loop that descends until finding a frontier (unexpanded move) or terminal node.
- `best_move()` picks the most-visited child ("robust child") after search completes, not the highest UCT score.
- The state object must expose `legal_moves()`, `is_terminal()`, and `last_action`.

## Key Insights
- The distinction between exploration during search (UCT) and exploitation at move time (max visits) is an important design pattern.
- Unvisited children need an explicit short-circuit because the UCT formula can't compute $n=0$.
- `tree_policy` serves as the bridge between Selection and Expansion — it stops at the right place for each.

## Questions to Revisit
- How does `expand()` choose which untried move to add?
- What does a rollout function look like for a stochastic game?

## Next Suggested Topic
Lesson 0003: Expansion and Simulation — adding nodes and running rollouts.