from datetime import date

CHALLENGE_START = date(2026, 9, 1)
CHALLENGE_END = date(2026, 9, 30)

TARGET = {"burpees": 1500, "steps": 150000}
BADGE_DIR = {"burpees": "assets/burpee_badges", "steps": "assets/steps_badges"}

# Minimum totals required to unlock each badge tier, in ascending order.
# Tiers 1-5 unlock every 300 burpees / 30000 steps up to the challenge target;
# tiers 6-8 are bonus badges for exceeding the 1500-burpee target.
BADGE_THRESHOLDS = {
    "burpees": [0, 300, 600, 900, 1200, 1600, 1700, 1800],
    "steps": [0, 30000, 60000, 90000, 120000],
}

CHALLENGE_LABEL = {"burpees": "burpees", "steps": "steps"}
