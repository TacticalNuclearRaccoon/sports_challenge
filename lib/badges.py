import os

from config import BADGE_DIR, BADGE_THRESHOLDS

_FILE_PREFIX = {"burpees": "burpee", "steps": "steps"}


def compute_tier(total: int, challenge_type: str) -> int:
    thresholds = BADGE_THRESHOLDS[challenge_type]
    tier = 1
    for level, threshold in enumerate(thresholds, start=1):
        if total >= threshold:
            tier = level
    return tier


def badge_path(challenge_type: str, tier: int) -> str:
    prefix = _FILE_PREFIX[challenge_type]
    return os.path.join(BADGE_DIR[challenge_type], f"{prefix}_level{tier}.png")
