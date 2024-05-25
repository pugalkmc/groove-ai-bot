from datetime import datetime, timedelta
from collections import deque

MAX_MESSAGES = 10  # Max number of messages
TIME_WINDOW = 60  # Time window in seconds

# In-memory storage for rate limiting
user_message_times = {}

# Helper function to check and record message timestamps
def check_and_record(user_id):
    now = datetime.now()
    if user_id not in user_message_times:
        user_message_times[user_id] = deque()
    
    # Remove old timestamps outside the time window
    while user_message_times[user_id] and user_message_times[user_id][0] < now - timedelta(seconds=TIME_WINDOW):
        user_message_times[user_id].popleft()

    # Check if user is over the message limit
    if len(user_message_times[user_id]) >= MAX_MESSAGES:
        return False

    # Record the new message timestamp
    user_message_times[user_id].append(now)
    return True