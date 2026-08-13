import os

from config import BADGE_DIR, NUM_BADGE_TIERS, TIER_SIZE

_FILE_PREFIX = {"burpees": "burpee", "steps": "steps"}


def compute_tier(total: int, challenge_type: str) -> int:
    return min(1 + total // TIER_SIZE[challenge_type], NUM_BADGE_TIERS)


def badge_path(challenge_type: str, tier: int) -> str:
    prefix = _FILE_PREFIX[challenge_type]
    return os.path.join(BADGE_DIR[challenge_type], f"{prefix}_level{tier}.png")
