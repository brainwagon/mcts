import blackjack_dp

def calc_edge():
    total_ev = 0.0
    for d in range(1, 11):
        p_d = blackjack_dp.card_prob(d)
        d_bj_prob = 0.0
        if d == 1: d_bj_prob = blackjack_dp.card_prob(10)
        elif d == 10: d_bj_prob = blackjack_dp.card_prob(1)
        
        for c1 in range(1, 11):
            for c2 in range(1, 11):
                p_c1 = blackjack_dp.card_prob(c1)
                p_c2 = blackjack_dp.card_prob(c2)
                prob = p_d * p_c1 * p_c2
                
                p_bj = (c1 == 1 and c2 == 10) or (c1 == 10 and c2 == 1)
                
                if p_bj:
                    ev = d_bj_prob * 0.0 + (1.0 - d_bj_prob) * 1.5
                else:
                    total, soft = blackjack_dp.get_initial_state(c1, c2)
                    evs = {}
                    evs['S'] = blackjack_dp.ev_stand(total, d)
                    evs['H'] = blackjack_dp.get_hit_ev(total, soft, d)
                    evs['D'] = blackjack_dp.ev_double(total, soft, d)
                    if c1 == c2 or (min(c1, 10) == 10 and min(c2, 10) == 10):
                        evs['P'] = blackjack_dp.ev_split(c1, d)
                    best_ev = max(evs.values())
                    ev = d_bj_prob * (-1.0) + (1.0 - d_bj_prob) * best_ev
                    
                total_ev += prob * ev
    print(f"Total EV (Player Advantage): {total_ev * 100:.4f}%")

if __name__ == '__main__':
    calc_edge()
