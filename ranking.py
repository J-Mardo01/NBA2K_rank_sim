import pandas as pd
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

def extract_and_normalize_stats(row):
    # Extract statistics from the row
    pts = row['PTS']
    three_pt_pct = row['3P%']
    two_pt_pct = row['2P%']
    games_played = row['G']
    minutes_per_game = row['MP']
    
    # Normalize statistics
    max_pts = row['PTS'].max() if pd.api.types.is_numeric_dtype(row['PTS']) else 1.0
    max_games_played = row['G'].max() if pd.api.types.is_numeric_dtype(row['G']) else 1.0
    max_minutes_per_game = row['MP'].max() if pd.api.types.is_numeric_dtype(row['MP']) else 1.0
    
    norm_pts = pts / max_pts
    norm_games_played = games_played / max_games_played
    norm_minutes_per_game = minutes_per_game / max_minutes_per_game
    
    # For percentages, assuming they are already in decimal form
    norm_three_pt_pct = three_pt_pct if pd.api.types.is_numeric_dtype(three_pt_pct) else 0.0
    norm_two_pt_pct = two_pt_pct if pd.api.types.is_numeric_dtype(two_pt_pct) else 0.0
    
    return norm_pts, norm_three_pt_pct, norm_two_pt_pct, norm_games_played, norm_minutes_per_game

def calculate_mvp_score(norm_pts, norm_three_pt_pct, norm_two_pt_pct, norm_games_played, norm_minutes_per_game, weights):
    # Calculate MVP score using weighted sum
    score = (weights['PTS'] * norm_pts +
             weights['3P%'] * norm_three_pt_pct +
             weights['2P%'] * norm_two_pt_pct +
             weights['G'] * norm_games_played +
             weights['MP'] * norm_minutes_per_game)
    
    return score

def player_ranking(data):
    # Sort the DataFrame by 'MVP Score' column in descending order
    sorted_data = data.sort_values(by='MVP Score', ascending=False)

    # Take the top 10 performing players
    top_10_players = sorted_data.head(10).copy()

    # Add a 'Rank' column to the DataFrame
    top_10_players['Rank'] = range(1, 11)

    # Calculate overall rating
    max_mvp_score = top_10_players['MVP Score'].max()
    min_rating = 90
    max_rating = 100
    top_10_players['Overall Rating'] = min_rating + ((top_10_players['MVP Score'] - top_10_players['MVP Score'].min()) / (max_mvp_score - top_10_players['MVP Score'].min())) * (max_rating - min_rating)

    # Round the overall rating
    top_10_players['Overall Rating'] = top_10_players['Overall Rating'].astype(int)


    # Display the top 10 players ranked from 1 to 10
    return top_10_players[['Rank', 'Player', 'MVP Score', 'Overall Rating']].to_string().encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)

# Read data from file using pandas
data = pd.read_csv('/Users/jaymardo/Documents/nba_stats/archive/22-23_stats.csv', encoding='latin1', delimiter=';')

# Example weights (subjective)
weights = {'PTS': 0.4, '3P%': 0.2, '2P%': 0.2, 'G': 0.1, 'MP': 0.1}

# Extract and normalize stats
data['Normalized PTS'], data['Normalized 3P%'], data['Normalized 2P%'], data['Normalized G'], data['Normalized MP'] = zip(*data.apply(extract_and_normalize_stats, axis=1))

# Calculate MVP scores for each player
data['MVP Score'] = data.apply(lambda row: calculate_mvp_score(row['Normalized PTS'], row['Normalized 3P%'], row['Normalized 2P%'], row['Normalized G'], row['Normalized MP'], weights), axis=1)

# Find the player with the highest MVP score
mvp_player = data.loc[data['MVP Score'].idxmax()]

print("Most Valuable Player:", mvp_player['Player'])

# Display the top 10 players ranked from 1 to 10
print(player_ranking(data))
