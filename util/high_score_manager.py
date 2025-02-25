def load_high_scores():
    scores = {}
    try:
        with open('high_scores.txt', 'r') as f:
            for line in f:
                game, score = line.strip().split(': ')
                scores[game] = int(score)  # Store scores as integers
    except (FileNotFoundError, ValueError):
        pass  # Return empty scores if file not found or invalid
    return scores

def update_high_score(game_name, score):
    scores = load_high_scores()
    high_score = scores.get(game_name, 0)  # Get current high score or default to 0
    if score > high_score:
        scores[game_name] = score  # Update high score
        with open('high_scores.txt', 'w') as f:
            for game, score in scores.items():
                f.write(f"{game}: {score}\n")  # Write all scores back to the file
        return score  # Return the new high score
    return high_score  # Return the existing high score