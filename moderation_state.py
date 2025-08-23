# moderation_state.py
from collections import defaultdict

violation_counts = defaultdict(int)
violations = defaultdict(list)  # user_id -> list of timestamps