from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from data_loader import get_wsl_data

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

def get_similar_players(matrix, target_player_name, top_n=5):
    """
    Calculates the similarity of a player to others based on normalised stats. Uses Cosine Similarity. 
    """
    if target_player_name not in matrix.index:
        return f"Player '{target_player_name}' not in the filtered data."

    #scale the data (Min Max Scaling)
    #this ensures that features with large ranges (like shots) don't mess up the recommendations
    scaler=MinMaxScaler()
    scaled_data=scaler.fit_transform(matrix)
    
    #create a dataframe from scaled data to keep track of labels
    normalized_df=pd.DataFrame(scaled_data, columns=matrix.columns, index=matrix.index)

    #calculate cosine similarity matrix
    sim_matrix=cosine_similarity(normalized_df)
    sim_df=pd.DataFrame(sim_matrix, index=matrix.index, columns=matrix.index)

    #extract similarities for the specific player
    target_similarities=sim_df[target_player_name].sort_values(ascending=False)
    
    #exclude the player themselves
    recommendations=target_similarities.drop(target_player_name).head(top_n)
    
    #puts names, similarity scores, and raw stats together
    output_results=[]
    for player, similarity_score in recommendations.items():
        output_results.append({
            "Player": player,
            "Similarity": similarity_score * 100, # Convert decimal to percentage
            "Goals": int(matrix.loc[player, 'Goals']),
            "Expected_Goals": matrix.loc[player, 'Expected_Goals'],
            "Shots": int(matrix.loc[player, 'Shots']),
            "Assists": int(matrix.loc[player, 'Assists'])
        })
        
    return output_results

def recommend_striker_profile(matrix, striker_name):
    """
    Prints a recommendation list for a given striker name.
    """
    if striker_name not in matrix.index:
        print(f"\nPlayer '{striker_name}' not found or doesn't meet minimum data thresholds.")
        return

    print(f"\n==========================================")
    print(f" SCOUTING REPORT: {striker_name.upper()}")
    print(f"==========================================")
    
    #find and print the target player's raw stats first
    print("CURRENT PROFILE:")
    print(f"    Goals:   {int(matrix.loc[striker_name, 'Goals'])}")
    print(f"    xG:      {matrix.loc[striker_name, 'Expected_Goals']:.2f}")
    print(f"    Shots:   {int(matrix.loc[striker_name, 'Shots'])}")
    print(f"    Assists: {int(matrix.loc[striker_name, 'Assists'])}")
    
    print("-"*42) # Divider line between target and recommendations

    
    print(f"\n--- Recommendation for {striker_name} ---")
    results=get_similar_players(matrix, striker_name)
    
    if isinstance(results, str):
        print(results)
    elif not results:
        print("No similar players found with sufficient data.")
    else:
        #loop through list of players recommended and print them properly
        for i, player_data in enumerate(results, 1):
            print(f"\n{i}. {player_data['Player']} ({player_data['Similarity']:.2f}% Match)")
            print(f"    Goals:   {player_data['Goals']}")
            print(f"    xG:      {player_data['Expected_Goals']:.2f}")
            print(f"    Shots:   {player_data['Shots']}")
            print(f"    Assists: {player_data['Assists']}")
        print("\n"+"="*42)

# Example usage (Uncomment and update striker name to test):
data=get_wsl_data()
filtered_data=filter_data(data)
recommend_striker_profile(filtered_data, "Lauren James")
