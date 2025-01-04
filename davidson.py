import math


# Function to calculate expected score


    

def davidson(th_wins, ta_wins, td, home_team, away_team ,home_goals, away_goals,elo_dict,U, k=30):
    Rh_B = elo_dict[home_team]
    Ra_B = elo_dict[away_team]
    H = max(0 , math.log10(th_wins/ta_wins))
    
    if home_goals > away_goals:
        S_home, S_away = 1, 0
    elif home_goals == away_goals:
        S_home, S_away = 0.5, 0.5
    else:
        S_home, S_away = 0, 1

    gd = abs(home_goals - away_goals)
    mov = max(1,math.log2((gd+1)/1.4))
    Sc = 600
    D = Rh_B - Ra_B + H * Sc
    calc = ((math.pow(10,((D*0.5)/Sc)+0.5*U))/(math.pow(10,((0.5*D)/Sc)+math.pow(10,(-0.5*D)/Sc))))
    elo_change_home = k * (S_home - calc) * mov
    elo_change_away = k * (S_away - calc) * mov
    elo_dict[home_team] += elo_change_home
    elo_dict[away_team] -= elo_change_away

    
    
    return elo_dict[home_team], elo_dict[away_team]


def davidson(home_team, away_team, home_goals, away_goals, elo_dict, total_home_wins, total_away_wins, total_matches, U, K=30, Sc=600):
    # Ratings before the match
    R_h = elo_dict[home_team]
    R_a = elo_dict[away_team]

    # Match outcome from home team's perspective
    if home_goals > away_goals:
        s = 1
        total_home_wins += 1
    elif home_goals == away_goals:
        s = 0.5
    else:
        s = 0
        total_away_wins += 1

    # Update total matches (excluding draws for H calculation)
    if home_goals != away_goals:
        total_matches += 1

    # Calculate frequencies with smoothing
    f_home = (total_home_wins + 0.5) / (total_matches + 1)
    f_away = (total_away_wins + 0.5) / (total_matches + 1)

    # Calculate H
    H = math.log10(f_home / f_away)

    # Calculate D with home advantage
    D = R_h - R_a + H * Sc

    # Calculate F(D)
    numerator = math.pow(10, 0.5 * D / Sc) + 0.5 * U
    denominator = math.pow(10, 0.5 * D / Sc) + math.pow(10, -0.5 * D / Sc) + U
    F_D = numerator / denominator

    # Rating changes
    elo_change_home = K * (s - F_D)
    elo_dict[home_team] += elo_change_home

    # For the away team
    s_away = 1 - s
    F_D_away = 1 - F_D
    elo_change_away = K * (s_away - F_D_away)
    elo_dict[away_team] += elo_change_away

    return elo_dict[home_team], elo_dict[away_team], total_home_wins, total_away_wins, total_matches