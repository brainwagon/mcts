# Learning Record 0005: Handling Stochastic Games

**Date:** 2025-04-05

## What Was Learned
- Chance nodes model random events (dice, cards) as explicit tree nodes.
- Explicit chance nodes multiply the branching factor by the number of outcomes.
- Implicit (determinize) chance resolves randomness inside `state.apply()` during rollouts.
- Higher $C_p$ values help average out noise in random-heavy games.
- Recommendation: start with implicit chance, upgrade to explicit only for high-impact randomness.

## Key Insights
- The tradeoff between explicit and implicit chance is a core design decision for stochastic game engines.
- Risk-style combat with dice is well-suited to explicit chance nodes because there are few outcomes with known probabilities.

## Next Suggested Topic
Lesson 0006: Memory, Parallelism, and Advanced Tradeoffs.