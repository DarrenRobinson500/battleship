import os

from datetime import datetime, timedelta

def tasks_done_so_far(total_tasks=750):
    # Define start and end of the week
    now = datetime.now()
    start_of_week = now - timedelta(days=now.weekday(), hours=now.hour - 8, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
    end_of_week = start_of_week + timedelta(days=7)  # Sunday 11:59pm

    # Clamp current time to within the week range
    if now < start_of_week:
        return 0
    if now > end_of_week:
        return total_tasks

    # Calculate elapsed proportion of the week
    total_seconds = (end_of_week - start_of_week).total_seconds()
    elapsed_seconds = (now - start_of_week).total_seconds()
    proportion_done = elapsed_seconds / total_seconds

    # Calculate completed tasks
    should_be_done = int(proportion_done * total_tasks)
    actually_done = read_count()
    remaining = should_be_done - actually_done
    percentage = int(actually_done / should_be_done * 100)
    print(f"Remaining Games: {should_be_done} - {actually_done} = {remaining} ({percentage}%)")

COUNTER_FILE = "function_count.txt"

def read_count():
    if not os.path.exists(COUNTER_FILE):
        return 0
    with open(COUNTER_FILE, "r") as f:
        try:
            return int(f.read())
        except ValueError:
            return 0

def write_count(count):
    with open(COUNTER_FILE, "w") as f:
        f.write(str(count))

def persistent_counter():
    count = read_count()
    count += 1
    write_count(count)
    print(f"Games played: {count}")

def reset_counter():
    write_count(0)
    print("Counter has been reset to 0.")

# Example usage

# To reset the counter, call:
# reset_counter()


# Game counter at zero with 120k
tasks_done_so_far()
