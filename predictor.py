from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from data_loader import get_wsl_data
from main import filter_data

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