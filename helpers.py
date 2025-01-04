from datetime import datetime,timedelta
import requests
import logging
from typing import List, Dict
import pandas as pd
import math


def generate_custom_date_range(start_date: str, end_date: str) -> list:
    """
    Generates a list of dates from start_date to end_date (inclusive).
    Dates should be provided in 'YYYY-MM-DD' format.
    """
    date_list = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    while current_date <= end_date:
        date_list.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    return date_list


def fetch_data(url: str) -> Dict:
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def fetch_scheduled_events(date: str, tournament_ids: List[int]) -> List[Dict]:
    url = f"https://www.sofascore.com/api/v1/sport/football/scheduled-events/{date}"
    try:
        data = fetch_data(url)
        events = data.get("events", [])
        # Filter events based on the tournament IDs
        filtered_events = [
            event for event in events
            if event['tournament']['uniqueTournament']['id'] in tournament_ids
        ]
        return filtered_events
    except Exception as e:
        logging.error(f"Error fetching events for date {date}: {e}")
        return []
    
    
# Convert percentage function to handle string values
def convert_percentage(value):
    if isinstance(value, str) and '(' in value and '%' in value:
        percentage = value.split('(')[-1].replace('%', '').replace(')', '').strip()
        return float(percentage) / 100
    return value  # Return value as is if it's not a string with percentage




def calculate_rolling_feature(df, feature_name, home_feature, away_feature, window=5):
    # Prepare home DataFrame
    home_df = df[['index', 'homeId', home_feature]]
    home_df = home_df.rename(columns={
        'homeId': 'teamId',
        home_feature: 'featureValue'
    })
    
    # Prepare away DataFrame
    away_df = df[['index', 'awayId', away_feature]]
    away_df = away_df.rename(columns={
        'awayId': 'teamId',
        away_feature: 'featureValue'
    })
    
    # Concatenate
    feature_df = pd.concat([home_df, away_df], ignore_index=True)
    
    # Calculate rolling average excluding current match
    feature_df['shiftedFeature'] = feature_df.groupby('teamId')['featureValue'].shift()
    
    feature_df['rollingAvg'] = feature_df.groupby('teamId')['shiftedFeature'].rolling(window=window, min_periods=1).mean().reset_index(level=0, drop=True)
    
    # Merge back to original DataFrame for home teams
    home_features = feature_df[feature_df['teamId'].isin(df['homeId'])][['index', 'teamId', 'rollingAvg']]
    home_features = home_features.rename(columns={'rollingAvg': f'homeRollingAvg{feature_name}'})
    
    df = df.merge(
        home_features,
        left_on=['index', 'homeId'],
        right_on=['index', 'teamId'],
        how='left'
    ).drop('teamId', axis=1)
    
    # Merge back for away teams
    away_features = feature_df[feature_df['teamId'].isin(df['awayId'])][['index', 'teamId', 'rollingAvg']]
    away_features = away_features.rename(columns={'rollingAvg': f'awayRollingAvg{feature_name}'})
    
    df = df.merge(
        away_features,
        left_on=['index', 'awayId'],
        right_on=['index', 'teamId'],
        how='left'
    ).drop('teamId', axis=1)
    
    return df


def update_player_elo(agg_elo_home, agg_elo_away,
                      total_home_wins, total_away_wins, total_matches,
                      gd,
                      player_id,
                      rating,
                      minutes_played,
                      position,
                      player_elo_df,
                      U=0.8,
                      K=30,
                      sc=600,
                      away=False):
    """
    Update player ELO based on their performance, minutes played, and match outcome.
    outcome: 1 for win, 0 for draw, -1 for loss
    """
    
    
    
    if pd.isna(rating) or pd.isna(minutes_played) or minutes_played == 0:
        return

        
    mov = max(1, math.log2(abs(gd) + 1))
    performance_factor = rating / 10  # Normalize rating (assuming it's out of 10)
    time_factor = minutes_played / 90  # Weight based on minutes played
    f_home = (total_home_wins + 0.5) / (total_matches + 1)
    f_away = (total_away_wins + 0.5) / (total_matches + 1)
    H = math.log10(f_home / f_away)
        
    R_h = player_elo_df.loc[player_id, 'elo']
    R_a = agg_elo_away
    
    

    
    if away == True:
        R_h = agg_elo_home
        R_a = player_elo_df.loc[player_id, 'elo']
        
    if gd>0:
        s = 1
    if gd == 0:
        s = 0.5
    if gd<0:
        s=0

    
    D = R_h - R_a + H * sc
    numerator = math.pow(10, 0.5 * D / sc) + 0.5 * U
    denominator = math.pow(10, 0.5 * D / sc) + math.pow(10, -0.5 * D / sc) + U
    F_D = numerator / denominator
    s_away = 1 - s
    F_D_away = 1 - F_D
    
    
   # else:
   #     adjustment = K * (s_away - F_D_away) * mov * (performance_factor) * time_factor
    
    
    
    if gd > 0: 
        if away == False:
            adjustment = K * (s - F_D) * mov * performance_factor * time_factor
        else:
            adjustment = K * (s_away - F_D_away) * mov * (1 - performance_factor) * time_factor
                    
    elif gd == 0:
        if away == False:
            if R_h >= R_a:
                adjustment = K * (s - F_D) * mov * (1 - performance_factor) * time_factor  # Corrected
            else:
                adjustment = K * (s - F_D) * mov * performance_factor * time_factor
        else:
            if R_a > R_h:
                adjustment = K * (s_away - F_D_away) * mov * (1 - performance_factor) * time_factor
            else:
                adjustment = K * (s_away - F_D_away) * mov * performance_factor * time_factor
                        
    elif gd < 0:
        if away == True:
            adjustment = K * (s_away - F_D_away) * mov * performance_factor * time_factor
        else:
            adjustment = K * (s - F_D) * mov * (1 - performance_factor) * time_factor

    # Update player's ELO
    player_elo_df.loc[player_id, 'elo'] += adjustment
    player_elo_df.at[player_id, 'position'] = position


    
def aggregate_team_elo(team_id, match_player_data,player_elo_df):
    """
    Calculate the average ELO for a team based on its players.

    Parameters:
    - team_id (int/str): Identifier for the team.
    - match_player_data (pd.DataFrame): DataFrame containing player match data.
      Expected columns: ['id', 'teamId', 'substitute', ...]

    Returns:
    - float: Average ELO of the team.
    """

    # Filter players belonging to the team and not substitutes
    team_players = match_player_data[
        (match_player_data['teamId'] == team_id) & 
        (match_player_data['substitute'] == False)
    ]
    # Extract player IDs from the filtered players
    player_ids = team_players['id'].tolist()

    # Retrieve ELO ratings from the DataFrame for these player IDs
    # Assuming 'player_id' in player_elo_df corresponds to 'id' in match_player_data
    team_elos = player_elo_df.loc[player_ids, 'elo'].tolist()
    #print(team_elos)
    # Calculate and return the average ELO, or default if no players found
    if len(team_elos) > 0:
        average_elo = sum(team_elos) / len(team_elos)
        logging.debug(f"Aggregated ELO for team ID {team_id}: {average_elo}")
        return average_elo
    else:
        logging.warning(f"No ELO data found for team ID {team_id}. Using default ELO 1300.")
        return 1300  # Default ELO if no players found


def initialize_player_elo(player_id, player_name, team_id, position, elo, date, player_elo_df):
    """
    Initialize or update a player's ELO rating in the DataFrame.

    Parameters:
    - player_id (int/str): Unique identifier for the player.
    - player_name (str): Name of the player.
    - team_id (int/str): Identifier for the player's team.
    - elo (float): Current or new ELO rating of the player.
    - date (str): Date when the ELO was last updated (YYYY-MM-DD).
    """

    if player_id in player_elo_df.index:
        # Update existing player's ELO and last_updated date
        player_elo_df.at[player_id, 'elo'] = elo
        player_elo_df.at[player_id, 'position'] = position
        player_elo_df.at[player_id, 'last_updated'] = date
        logging.debug(f"Updated ELO for player ID: {player_id} to {elo}.")
    else:
        # Add new player to the DataFrame
        player_elo_df.loc[player_id] = {
            'player_name': player_name,
            'team_id': team_id,
            'positions': position,
            'elo': elo,
            'last_updated': date
        }
        #logging.info(f"Added new player to DataFrame: {player_id} - {player_name} with ELO {elo}.")

def davidson_mov(home_team,
                 away_team,
                 gd,
                 elo_dict,
                 total_home_wins, total_away_wins, total_matches,
                 U=0.8,
                 K=30,
                 sc=600):
    
    
    R_h = elo_dict[home_team]
    R_a = elo_dict[away_team]
    
    
    if gd>0:
        s=1
    elif gd<0:
        s=0
    elif gd==0:
        s=0.5
        
    gd = abs(gd)
    mov = max(1, math.log2(gd + 1))
    
     # Calculate frequencies with smoothing
    f_home = (total_home_wins + 0.5) / (total_matches + 1)
    f_away = (total_away_wins + 0.5) / (total_matches + 1)

    # Calculate H
    H = math.log10(f_home / f_away)
    
    # Calculate D with home advantage
    D = R_h - R_a + H * sc

    # Calculate F(D)
    numerator = math.pow(10, 0.5 * D / sc) + 0.5 * U
    denominator = math.pow(10, 0.5 * D / sc) + math.pow(10, -0.5 * D / sc) + U
    F_D = numerator / denominator

    # Rating changes
    elo_change_home = K * (s - F_D) * mov
    elo_dict[home_team] += elo_change_home

    # For the away team
    s_away = 1 - s
    F_D_away = 1 - F_D
    elo_change_away = K * (s_away - F_D_away) * mov
    elo_dict[away_team] += elo_change_away

    return R_h , R_a
    
    
# def initialize_team_elo(team_id, team_elo_df, team_name, elo=1500, date=None):
#     """
#     Initialize or update a team's ELO rating in the DataFrame.

#     Parameters:
#     - team_id (int/str): Unique identifier for the team.
#     - team_name (str): Name of the team.
#     - elo (float): Current or new ELO rating of the team (default is 1500).
#     - date (str): Date when the ELO was last updated (YYYY-MM-DD).
#     """

#     if team_id in team_elo_df.index:
#         # Update existing team's ELO and last_updated date
#         team_elo_df.at[team_id, 'elo'] = elo
#         team_elo_df.at[team_id, 'last_updated'] = date
#         logging.debug(f"Updated ELO for team ID: {team_id} to {elo}.")
#     else:
#         # Add new team to the DataFrame
#         team_elo_df.loc[team_id] = {
#             'team_name': team_name,
#             'elo': elo,
#             'last_updated': date
#         }
#         logging.info(f"Added new team to DataFrame: {team_id} - {team_name} with ELO {elo}.")
