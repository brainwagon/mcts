#!/usr/bin/env python3
"""MCTS-powered Yahtzee: a complete implementation for Lesson 0007.

Usage:
    python yahtzee_mcts.py              # interactive play (human vs AI hint)
    python yahtzee_mcts.py --simulate N  # AI plays N games automatically
"""
from __future__ import annotations

import argparse
import math
import random
import sys
from typing import Any, Callable, List, Optional, Tuple

# ── Yahtzee Domain ──────────────────────────────────────────────────────

CATEGORY_NAMES = [
    "Ones", "Twos", "Threes", "Fours", "Fives", "Sixes",
    "Three of a Kind", "Four of a Kind", "Full House",
    "Small Straight", "Large Straight", "Yahtzee", "Chance",
]


def score_dice(dice: Tuple[int, ...], category: int) -> int:
    """Return the raw points for `dice` in `category` (0 if invalid)."""
    counts = [dice.count(v) for v in range(1, 7)]
    if category < 6:                    # Upper section
        return (category + 1) * counts[category]
    if category == 6:                   # Three of a Kind
        return sum(dice) if max(counts) >= 3 else 0
    if category == 7:                   # Four of a Kind
        return sum(dice) if max(counts) >= 4 else 0
    if category == 8:                   # Full House
        return 25 if sorted(counts) == [0, 0, 0, 0, 2, 3] else 0
    if category == 9:                   # Small Straight
        dice_set = set(dice)
        straights = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
        return 30 if any(s.issubset(dice_set) for s in straights) else 0
    if category == 10:                  # Large Straight
        return 40 if sorted(dice) in [[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]] else 0
    if category == 11:                  # Yahtzee
        return 50 if max(counts) == 5 else 0
    if category == 12:                  # Chance
        return sum(dice)
    return 0


class YahtzeeState:
    """Immutable game state."""

    def __init__(self,
                 dice: Tuple[int, ...],
                 rolls_left: int,
                 scores: List[int]):
        self.dice = tuple(sorted(dice))
        self.rolls_left = rolls_left
        self.scores = list(scores)          # -1 = unfilled, else points

    def clone(self) -> YahtzeeState:
        return YahtzeeState(self.dice, self.rolls_left, list(self.scores))

    def __key(self):
        return (self.dice, self.rolls_left, tuple(self.scores))

    def __eq__(self, other):
        if not isinstance(other, YahtzeeState): return False
        return self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())

    def is_terminal(self) -> bool:
        return all(s >= 0 for s in self.scores)

    def current_total(self) -> int:
        total = sum(s for s in self.scores if s >= 0)
        # Upper-section bonus
        upper = sum(self.scores[i] for i in range(6) if self.scores[i] >= 0)
        if upper >= 63:
            total += 35
        return total

    def legal_moves(self) -> List[Tuple[str, Any]]:
        moves = []
        for cat in range(13):
            if self.scores[cat] < 0:
                moves.append(('SCORE', cat))
        if self.rolls_left > 0 and not self.is_terminal():
            import itertools
            keep_sets = set()
            for r in range(6):
                for combo in itertools.combinations(self.dice, r):
                    keep_sets.add(combo)
            for combo in keep_sets:
                moves.append(('KEEP', combo))
        return moves

    def apply(self, move: Tuple[str, Any]) -> YahtzeeState:
        kind, arg = move
        if kind == 'KEEP':
            pool = list(self.dice)
            new_dice = []
            for val in arg:
                if val in pool:
                    new_dice.append(val)
                    pool.remove(val)
            while len(new_dice) < 5:
                new_dice.append(random.randint(1, 6))
            return YahtzeeState(tuple(sorted(new_dice)), self.rolls_left - 1,
                                list(self.scores))
        else:   # SCORE
            cat = arg
            raw = score_dice(self.dice, cat)
            # Yahtzee bonus: +100 for extra Yahtzees after scoring cat 11
            bonus = 0
            if len(set(self.dice)) == 1 and self.scores[11] > 0 and cat != 11:
                bonus = 100
            new_scores = list(self.scores)
            new_scores[cat] = raw + bonus
            if self.is_terminal():
                return YahtzeeState(self.dice, 0, new_scores)
            fresh = tuple(sorted(random.randint(1, 6) for _ in range(5)))
            return YahtzeeState(fresh, 2, new_scores)


# ── ExpectiMax MCTS Engine ──────────────────────────────────────────────

from typing import Dict, Any

class ChanceNode:
    """Node representing a stochastic environment response."""
    def __init__(self, action: Tuple[str, Any], parent: 'DecisionNode'):
        self.action = action
        self.parent = parent
        self.visits = 0
        self.total_reward = 0.0
        # children keyed by the resulting state outcome
        self.children: Dict[YahtzeeState, 'DecisionNode'] = {}

class DecisionNode:
    """Node representing the player's turn (Closed Loop)."""
    def __init__(self, state: YahtzeeState, parent: Optional[ChanceNode] = None):
        self.state = state
        self.parent = parent
        self.visits = 0
        self.total_reward = 0.0
        self.untried_moves = state.legal_moves()
        # children keyed by action
        self.children: Dict[Tuple[str, Any], ChanceNode] = {}


def simulate(state: YahtzeeState) -> float:
    """Heuristic rollout from this state to a terminal."""
    state = state.clone()
    while not state.is_terminal():
        moves = state.legal_moves()
        keep_moves = [m for m in moves if m[0] == 'KEEP']

        scores = [(score_dice(state.dice, cat), cat) for cat in range(13) if state.scores[cat] < 0]
        if not scores: break
        
        best_score_val, best_cat = max(scores, key=lambda x: x[0])
        should_score = False
        score_cat = best_cat
        
        if keep_moves:
            counts = [state.dice.count(v) for v in range(1, 7)]
            max_count = max(counts)
            
            if max_count == 5 and state.scores[11] < 0:
                should_score = True
                score_cat = 11
            elif best_score_val == 40 and state.scores[10] < 0:
                should_score = True
                score_cat = 10
            elif best_score_val == 30 and state.scores[9] < 0:
                should_score = True
                score_cat = 9
            elif best_score_val == 25 and state.scores[8] < 0:
                should_score = True
                score_cat = 8
            else:
                for val, count in enumerate(counts, 1):
                    if count >= 3 and state.scores[val-1] < 0:
                        should_score = True
                        score_cat = val - 1
                        break
        else:
            should_score = True
            if best_score_val == 0:
                sacrifice_order = [11, 0, 1, 2, 3, 12, 6, 7, 8, 9, 10, 4, 5]
                for cat in sacrifice_order:
                    if state.scores[cat] < 0:
                        score_cat = cat
                        break
                        
        if should_score:
            state = state.apply(('SCORE', score_cat))
            continue
            
        counts = {v: state.dice.count(v) for v in range(1, 7)}
        max_count = max(counts.values())
        dice_set = set(state.dice)
        needs_straight = (state.scores[9] < 0 or state.scores[10] < 0)
        best_keep = ()
        
        if needs_straight and max_count < 3:
            for s in [{1,2,3,4,5}, {2,3,4,5,6}, {1,2,3,4}, {2,3,4,5}, {3,4,5,6}]:
                intersection = s.intersection(dice_set)
                if len(intersection) >= 4:
                    best_keep = tuple(sorted(intersection))
                    break
            if not best_keep and len(dice_set) >= 3 and max_count < 2:
                for s in [{1,2,3}, {2,3,4}, {3,4,5}, {4,5,6}]:
                    intersection = s.intersection(dice_set)
                    if len(intersection) == 3:
                        best_keep = tuple(sorted(intersection))
                        break
                        
        if not best_keep:
            best_val = max(range(1, 7), key=lambda v: (counts[v], v))
            best_keep = tuple(best_val for _ in range(counts[best_val]))
            
        state = state.apply(('KEEP', best_keep))

    return float(state.current_total())


def mcts_search(root_state: YahtzeeState,
                iterations: int = 500,
                Cp: float = 10.0) -> Optional[Tuple[str, Any]]:
    """Return the best action from root_state using ExpectiMax MCTS."""
    root = DecisionNode(root_state)
    for _ in range(iterations):
        node = root
        
        # 1. Tree Policy & Expand
        while not node.state.is_terminal():
            if node.untried_moves:
                # Expand a new action
                idx = random.randrange(len(node.untried_moves))
                action = node.untried_moves.pop(idx)
                chance_node = ChanceNode(action, parent=node)
                node.children[action] = chance_node
                
                # Sample an outcome from the environment
                next_state = node.state.apply(action)
                child_decision = DecisionNode(next_state, parent=chance_node)
                chance_node.children[next_state] = child_decision
                
                node = child_decision
                break
            else:
                # Select best action via UCB
                best_score = -float('inf')
                best_action = None
                best_chance_node = None
                for action, chance_child in node.children.items():
                    if chance_child.visits == 0:
                        score = float('inf')
                    else:
                        exploitation = chance_child.total_reward / chance_child.visits
                        exploration = Cp * math.sqrt(math.log(node.visits) / chance_child.visits)
                        score = exploitation + exploration
                    if score > best_score:
                        best_score = score
                        best_action = action
                        best_chance_node = chance_child
                
                if best_chance_node is None:
                    break
                    
                # Sample the environment using the chosen action
                next_state = node.state.apply(best_action)
                
                # If we've never seen this exact dice outcome from this action, expand it!
                if next_state not in best_chance_node.children:
                    child_decision = DecisionNode(next_state, parent=best_chance_node)
                    best_chance_node.children[next_state] = child_decision
                    node = child_decision
                    break
                else:
                    node = best_chance_node.children[next_state]
            
        # 2. Simulate
        reward = simulate(node.state)
        
        # 3. Backpropagate
        curr = node
        while curr is not None:
            curr.visits += 1
            curr.total_reward += reward
            # Move up to ChanceNode
            curr = curr.parent
            if curr is not None:
                curr.visits += 1
                curr.total_reward += reward
                curr = curr.parent

    if not root.children:
        return None
    best_action = max(root.children.keys(), key=lambda a: root.children[a].visits)
    return best_action


# ── CLI ─────────────────────────────────────────────────────────────────

def simulate_games(count: int, iterations: int = 500) -> None:
    """Run `count` games with MCTS making all decisions."""
    scores = []
    for game in range(1, count + 1):
        # Fresh game state: no dice, 2 rolls, all scores unfilled
        dice = tuple(sorted(random.randint(1, 6) for _ in range(5)))
        state = YahtzeeState(dice, 2, [-1] * 13)
        while not state.is_terminal():
            action = mcts_search(state, iterations=iterations)
            if action is None:
                break
            state = state.apply(action)
        total = state.current_total()
        scores.append(total)
        print(f"Game {game}: {total} pts")
    avg = sum(scores) / len(scores)
    print(f"\nAverage over {count} games: {avg:.1f} pts  "
          f"(max={max(scores)}, min={min(scores)})")
    return avg


def interactive_play(iterations: int = 500) -> None:
    """Human plays, but can ask for MCTS hint at each move."""
    dice = tuple(sorted(random.randint(1, 6) for _ in range(5)))
    state = YahtzeeState(dice, 2, [-1] * 13)

    while not state.is_terminal():
        print(f"\nDice: {state.dice}  |  Rolls left: {state.rolls_left}")
        for i, s in enumerate(state.scores):
            if s >= 0:
                print(f"  [{i:>2}] {CATEGORY_NAMES[i]:20s} {s}")
            else:
                cat_score = score_dice(state.dice, i)
                print(f"  [{i:>2}] {CATEGORY_NAMES[i]:20s} {cat_score:2d}  (unfilled)")

        hint = mcts_search(state, iterations=iterations)
        if hint:
            print(f"\nMCTS hint: {hint[0]} {hint[1]}")

        raw = input("\nYour move (e.g., 'SCORE 5' or 'KEEP 2,2,3' or 'KEEP NONE'): ").strip()
        if not raw:
            break
        parts = raw.split()
        if len(parts) != 2:
            print("Bad format; try 'SCORE 5' or 'KEEP 2,2,3'")
            continue
        kind = parts[0].upper()
        if kind == 'KEEP':
            if parts[1].upper() in ('0', 'NONE'):
                arg = ()
            else:
                try:
                    arg = tuple(int(x) for x in parts[1].split(','))
                except ValueError:
                    print("Bad format for KEEP; use comma-separated values like '2,2,3'")
                    continue
        else:
            arg = int(parts[1])
        state = state.apply((kind, arg))

    print(f"\nFinal score: {state.current_total()}")


def main():
    parser = argparse.ArgumentParser(description="MCTS Yahtzee")
    parser.add_argument('--simulate', type=int, default=0,
                        help='Run N games automatically with MCTS')
    parser.add_argument('--iterations', type=int, default=500,
                        help='MCTS iterations per decision (default 500)')
    args = parser.parse_args()

    random.seed()
    if args.simulate > 0:
        simulate_games(args.simulate, args.iterations)
    else:
        interactive_play(args.iterations)


if __name__ == '__main__':
    main()