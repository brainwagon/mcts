import random
import math
from typing import List

def draw():
    c = random.randint(1, 13)
    return 10 if c > 10 else c

def get_value(cards):
    v = sum(cards)
    if 1 in cards and v + 10 <= 21:
        return v + 10, True
    return v, False

class State:
    def __init__(self, hands: List[dict], dealer_cards: List[int], hand_idx: int):
        self.hands = [h.copy() for h in hands]
        for i, h in enumerate(hands):
            self.hands[i]['cards'] = h['cards'].copy()
        self.dealer_cards = dealer_cards.copy()
        self.hand_idx = hand_idx

    def clone(self):
        return State(self.hands, self.dealer_cards, self.hand_idx)

    def is_terminal(self):
        return self.hand_idx >= len(self.hands)

    def legal_moves(self):
        if self.is_terminal(): return []
        hand = self.hands[self.hand_idx]
        cards = hand['cards']
        val, _ = get_value(cards)
        if val >= 21:
            return ['STAND']
        
        moves = ['HIT', 'STAND']
        if len(cards) == 2:
            moves.append('DOUBLE')
            if cards[0] == cards[1] or (min(cards[0], 10) == 10 and min(cards[1], 10) == 10):
                moves.append('SPLIT')
        return moves

    def apply(self, action):
        s = self.clone()
        hand = s.hands[s.hand_idx]
        
        if action == 'STAND':
            hand['done'] = True
            s.hand_idx += 1
        elif action == 'HIT':
            hand['cards'].append(draw())
            if get_value(hand['cards'])[0] >= 21:
                hand['done'] = True
                s.hand_idx += 1
        elif action == 'DOUBLE':
            hand['bet'] *= 2
            hand['cards'].append(draw())
            hand['done'] = True
            s.hand_idx += 1
        elif action == 'SPLIT':
            c = hand['cards'].pop()
            hand['cards'].append(draw())
            new_hand = {'cards': [c, draw()], 'bet': hand['bet'], 'done': False}
            s.hands.insert(s.hand_idx + 1, new_hand)
            # Split Aces -> 1 card only
            if c == 1:
                hand['done'] = True
                new_hand['done'] = True
                s.hand_idx += 2
        return s

    def get_reward(self):
        dealer_cards = self.dealer_cards.copy()
        # Dealer hits soft 17
        while True:
            d_val, d_soft = get_value(dealer_cards)
            if d_val < 17 or (d_val == 17 and d_soft):
                dealer_cards.append(draw())
            else:
                break
                
        d_val, _ = get_value(dealer_cards)
        d_bust = d_val > 21
        
        reward = 0.0
        for hand in self.hands:
            p_val, _ = get_value(hand['cards'])
            if p_val > 21:
                reward -= hand['bet']
            elif d_bust:
                reward += hand['bet']
            elif p_val > d_val:
                reward += hand['bet']
            elif p_val < d_val:
                reward -= hand['bet']
        return reward

class MCTSNode:
    def __init__(self, parent=None, action=None):
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.total_reward = 0.0
        self.untried_moves = None

def simulate(state):
    s = state.clone()
    while not s.is_terminal():
        moves = s.legal_moves()
        if not moves: break
        hand = s.hands[s.hand_idx]
        val, soft = get_value(hand['cards'])
        # Basic rollout heuristic
        if val < 17 or (val == 17 and soft):
            action = 'HIT'
        else:
            action = 'STAND'
        if action not in moves:
            action = random.choice(moves)
        s = s.apply(action)
    return s.get_reward()

def mcts_search(root_state, iterations=50000, Cp=1.0):
    root = MCTSNode()
    for _ in range(iterations):
        node = root
        state = root_state.clone()
        
        while not state.is_terminal():
            if node.untried_moves is None:
                node.untried_moves = state.legal_moves()
                random.shuffle(node.untried_moves)
                
            if node.untried_moves:
                action = node.untried_moves.pop()
                child = MCTSNode(parent=node, action=action)
                node.children.append(child)
                state = state.apply(action)
                node = child
                break
                
            best_score = -float('inf')
            best_child = None
            for child in node.children:
                if child.visits == 0:
                    best_child = child
                    break
                exploitation = child.total_reward / child.visits
                exploration = Cp * math.sqrt(math.log(node.visits) / child.visits)
                if exploitation + exploration > best_score:
                    best_score = exploitation + exploration
                    best_child = child
            if best_child is None: break
            node = best_child
            state = state.apply(node.action)
            
        reward = simulate(state)
        
        while node is not None:
            node.visits += 1
            node.total_reward += reward
            node = node.parent
            
    best = max(root.children, key=lambda c: c.total_reward / c.visits if c.visits > 0 else -100)
    return best.action

def generate_strategy():
    dealer_upcards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 1]
    action_map = {'HIT': 'H', 'STAND': 'S', 'DOUBLE': 'D', 'SPLIT': 'P'}
    
    print("MCTS Blackjack Basic Strategy (Infinite Deck, Dealer hits soft 17)")
    print("H=Hit, S=Stand, D=Double, P=Split")
    print("-" * 45)
    
    header = "Player | " + " ".join(f"{d if d!=1 else 'A':2}" for d in dealer_upcards)
    print("HARD TOTALS")
    print(header)
    for p_total in range(20, 4, -1):
        row = f"  {p_total:2}   | "
        for d in dealer_upcards:
            c1 = min(10, p_total - 2)
            c2 = p_total - c1
            if c1 == c2:
                c1 -= 1
                c2 += 1
            if c1 == 1 or c2 == 1:
                if p_total > 11: c1, c2 = 10, p_total - 10
                else: c1, c2 = 9, p_total - 9
            state = State([{'cards': [c1, c2], 'bet': 1.0, 'done': False}], [d], 0)
            action = mcts_search(state, iterations=50000)
            row += f"{action_map[action]:2} "
        print(row)
        
    print("\nSOFT TOTALS")
    print(header)
    for second_card in range(9, 1, -1):
        row = f" A,{second_card:1}   | "
        for d in dealer_upcards:
            state = State([{'cards': [1, second_card], 'bet': 1.0, 'done': False}], [d], 0)
            action = mcts_search(state, iterations=50000)
            row += f"{action_map[action]:2} "
        print(row)
        
    print("\nPAIRS")
    print(header)
    for pair_card in [1, 10, 9, 8, 7, 6, 5, 4, 3, 2]:
        p_str = "A,A" if pair_card == 1 else f"{pair_card},{pair_card}"
        row = f" {p_str:5} | "
        for d in dealer_upcards:
            state = State([{'cards': [pair_card, pair_card], 'bet': 1.0, 'done': False}], [d], 0)
            action = mcts_search(state, iterations=50000)
            row += f"{action_map[action]:2} "
        print(row)

if __name__ == '__main__':
    generate_strategy()
