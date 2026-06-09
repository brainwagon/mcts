import functools

def card_prob(v):
    return 4/13.0 if v == 10 else 1/13.0

@functools.lru_cache(None)
def dealer_play_cached(total, soft):
    if total > 21:
        return {'BUST': 1.0}
    if total >= 17:
        if total == 17 and soft:
            pass # H17 rule: dealer hits soft 17
        else:
            return {total: 1.0}
            
    dist = {'BUST': 0.0, 17: 0.0, 18: 0.0, 19: 0.0, 20: 0.0, 21: 0.0}
    for v in range(1, 11):
        p = card_prob(v)
        n_total = total + v
        n_soft = soft
        if v == 1 and not soft and n_total + 10 <= 21:
            n_total += 10
            n_soft = True
        if n_total > 21 and n_soft:
            n_total -= 10
            n_soft = False
        sub_dist = dealer_play_cached(n_total, n_soft)
        for k, prob in sub_dist.items():
            dist[k] += p * prob
    return dist

@functools.lru_cache(None)
def get_dealer_probs(upcard):
    dist = {'BUST': 0.0, 17: 0.0, 18: 0.0, 19: 0.0, 20: 0.0, 21: 0.0}
    weight_sum = 0.0
    for hole in range(1, 11):
        # US Peek rule: skip blackjack hands
        if upcard == 1 and hole == 10:
            continue
        if upcard == 10 and hole == 1:
            continue
            
        p = card_prob(hole)
        weight_sum += p
        
        n_total = upcard + hole
        n_soft = False
        if upcard == 1 or hole == 1:
            n_total += 10
            n_soft = True
            
        sub_dist = dealer_play_cached(n_total, n_soft)
        for k, prob in sub_dist.items():
            dist[k] += p * prob
            
    # Normalize probabilities
    for k in dist:
        dist[k] /= weight_sum
    return dist

@functools.lru_cache(None)
def ev_stand(p_total, upcard):
    if p_total > 21:
        return -1.0
    dealer_probs = get_dealer_probs(upcard)
    ev = 0.0
    for d_final, prob in dealer_probs.items():
        if d_final == 'BUST':
            ev += prob
        elif p_total > d_final:
            ev += prob
        elif p_total < d_final:
            ev -= prob
    return ev

@functools.lru_cache(None)
def ev_optimal(total, soft, upcard):
    if total > 21:
        return -1.0
    stand_val = ev_stand(total, upcard)
    hit_val = get_hit_ev(total, soft, upcard)
    return max(stand_val, hit_val)

@functools.lru_cache(None)
def get_hit_ev(total, soft, upcard):
    hit_val = 0.0
    for v in range(1, 11):
        p = card_prob(v)
        n_total = total + v
        n_soft = soft
        if v == 1 and not soft and n_total + 10 <= 21:
            n_total += 10
            n_soft = True
        if n_total > 21 and n_soft:
            n_total -= 10
            n_soft = False
        hit_val += p * ev_optimal(n_total, n_soft, upcard)
    return hit_val

@functools.lru_cache(None)
def ev_double(total, soft, upcard):
    ev = 0.0
    for v in range(1, 11):
        p = card_prob(v)
        n_total = total + v
        n_soft = soft
        if v == 1 and not soft and n_total + 10 <= 21:
            n_total += 10
            n_soft = True
        if n_total > 21 and n_soft:
            n_total -= 10
            n_soft = False
            
        if n_total > 21:
            ev += p * (-2.0)
        else:
            ev += p * (2.0 * ev_stand(n_total, upcard))
    return ev

@functools.lru_cache(None)
def ev_split(card, upcard):
    ev_non_pair = 0.0
    for v in range(1, 11):
        if v == card:
            continue
            
        p = card_prob(v)
        n_total = card + v
        n_soft = False
        if card == 1 or v == 1:
            n_total += 10
            n_soft = True
            
        if card == 1:
            # Splitting aces -> exactly 1 card. So must stand.
            ev_non_pair += p * ev_stand(n_total, upcard)
        else:
            # Can play optimally on the new 2-card hand
            best_action_val = max(
                ev_stand(n_total, upcard),
                get_hit_ev(n_total, n_soft, upcard),
                ev_double(n_total, n_soft, upcard)
            )
            ev_non_pair += p * best_action_val
            
    p_pair = card_prob(card)
    # Account for infinite re-splits
    return (2.0 * ev_non_pair) / (1.0 - p_pair)

def get_initial_state(c1, c2):
    total = c1 + c2
    soft = False
    if c1 == 1 or c2 == 1:
        total += 10
        soft = True
    return total, soft

def get_best_action(c1, c2, upcard):
    total, soft = get_initial_state(c1, c2)
    
    evs = {}
    evs['S'] = ev_stand(total, upcard)
    evs['H'] = get_hit_ev(total, soft, upcard)
    evs['D'] = ev_double(total, soft, upcard)
    
    if c1 == c2 or (min(c1, 10) == 10 and min(c2, 10) == 10):
        evs['P'] = ev_split(c1, upcard)
        
    return max(evs, key=evs.get)

def generate_strategy():
    dealer_upcards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 1]
    
    print("DP Blackjack Basic Strategy (Infinite Deck, Dealer hits soft 17)")
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
            action = get_best_action(c1, c2, d)
            row += f"{action:2} "
        print(row)
        
    print("\nSOFT TOTALS")
    print(header)
    for second_card in range(9, 1, -1):
        row = f" A,{second_card:1}   | "
        for d in dealer_upcards:
            action = get_best_action(1, second_card, d)
            row += f"{action:2} "
        print(row)
        
    print("\nPAIRS")
    print(header)
    for pair_card in [1, 10, 9, 8, 7, 6, 5, 4, 3, 2]:
        p_str = "A,A" if pair_card == 1 else f"{pair_card},{pair_card}"
        row = f" {p_str:5} | "
        for d in dealer_upcards:
            action = get_best_action(pair_card, pair_card, d)
            row += f"{action:2} "
        print(row)

if __name__ == '__main__':
    generate_strategy()
