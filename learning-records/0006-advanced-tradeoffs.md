# Learning Record 0006: Memory, Parallelism, and Advanced Tradeoffs

**Date:** 2025-04-05

## What Was Learned
- Tree reuse via `advance_root()` preserves the subtree after an opponent's move — the single biggest performance win.
- Transposition tables hash game states to merge equivalent positions reached via different move sequences.
- Root parallelism is the simplest parallel approach: independent searches, average results.
- Tree parallelism with virtual loss shares one tree across threads for better memory efficiency.
- Heuristic rollouts (preferring captures, forward moves, etc.) improve per-iteration quality.
- The complete engine architecture separates the generic MCTS core from the game-specific state.

## Key Insights
- Never rebuild the tree from scratch after a move — always reuse the opponent's subtree.
- Virtual loss acts as a temporary lock by artificially inflating visit counts.
- The six-method state interface is the only coupling between MCTS and the game.

## Course Complete
All six lessons covering the full MCTS engine design spectrum.