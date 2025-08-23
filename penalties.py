# penalties.py
penalty_schedule = {
    1: 60,
    2: 180,
    3: 300,
    4: 86400,
    5: 604800,
    6: 2592000,
}

def get_penalty(count):
    return penalty_schedule.get(count, 2592000)