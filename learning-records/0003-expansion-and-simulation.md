# Learning Record 0003: Expansion and Simulation

**Date:** 2025-04-05

## What Was Learned
- `expand()` pops one untried move, applies it via `state.apply(move)`, creates an `MCTSNode`, links as child.
- `simulate()` clones the state and runs random moves to a terminal, returning a reward.
- Random rollouts work because the aggregate of many noisy samples converges to a useful signal.
- The reward is from the perspective of the player who made the move to the current node.
- State cloning (or undo pattern) is essential to avoid corrupting tree state during rollouts.

## Key Insights
- Expanding one child per iteration is standard — UCT controls which branches deepen.
- Uniform random is often "good enough" — a key result from the literature that made MCTS practical.
- The rollout policy quality vs. speed tradeoff is a core design decision for engine builders.

## Questions to Revisit
- How exactly does reward sign alternation work during backpropagation?
- What does `state.reward()` return and from whose perspective?

## Next Suggested Topic
Lesson 0004: Backpropagation and the Full Loop — completing the four-phase cycle.