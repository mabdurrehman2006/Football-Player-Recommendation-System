import pandas as pd
import numpy as np

def filter_data(raw_df):

    #filters by attacking positions
    forward_positions=[
        "Center Forward", 
        "Secondary Striker", 
        "Left Wing", 
        "Right Wing",
        "Left Center Forward",
        "Right Center Forward"
    ]
    
    #finds names of players that played in these positions
    forward_masks=raw_df["position"].isin(forward_positions)
    forward_player_names=raw_df[forward_masks]['player'].unique()
    
    #filters raw_df to only keep those players
    raw_df=raw_df[raw_df["player"].isin(forward_player_names)].copy()

    #filter shots and passes
    shots_df=raw_df[raw_df["type"]=="Shot"].copy()
    pass_df=raw_df[raw_df["type"]=="Pass"].copy()

    #fills missing xg values with 0 so it doesn't mess up calculations
    shots_df['shot_statsbomb_xg']=shots_df['shot_statsbomb_xg'].fillna(0)

    #calculates goals scored for each player
    league_goals=shots_df[shots_df["shot_outcome"]=="Goal"]
    player_goals=league_goals.groupby("player").size()

    #calculates player xg
    player_xg=shots_df.groupby('player')['shot_statsbomb_xg'].sum()

    #print(player_goals)

    #calculates shots taken by player
    player_shots=shots_df.groupby('player').size()

    #calculates assists for each player
    league_assists=pass_df[pass_df["pass_goal_assist"]==True]
    player_assists=league_assists.groupby("player").size()


    matrix=pd.DataFrame({
        'Goals': player_goals,
        'Expected_Goals': player_xg,
        'Shots': player_shots,
        'Assists': player_assists
    }).fillna(0)

    #keeps players with a sample size of 15 shots
    filtered_matrix=matrix[matrix['Shots'] >= 15]

    return filtered_matrix
