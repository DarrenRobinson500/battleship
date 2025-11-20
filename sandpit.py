from datetime import timedelta

# Example list of timedeltas
game_times = [timedelta(hours=1), timedelta(hours=2, minutes=30), timedelta(minutes=45)]

# Calculate the average timedelta
average = (sum(game_times, timedelta()) / len(game_times)).total_seconds()

print("Average duration in seconds:", average)
total_seconds = average
print(f"{int(total_seconds // 60)}m {int(total_seconds % 60)}s (Average)")

