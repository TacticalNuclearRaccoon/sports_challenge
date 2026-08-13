from datetime import date

import pandas as pd

from config import CHALLENGE_END, CHALLENGE_START, TARGET


def fetch_profile(sb, user_id: str) -> dict | None:
    resp = sb.table("profiles").select("*").eq("id", user_id).execute()
    return resp.data[0] if resp.data else None


def create_profile(sb, user_id: str, display_name: str, challenge_type: str) -> dict:
    resp = (
        sb.table("profiles")
        .insert({"id": user_id, "display_name": display_name, "challenge_type": challenge_type})
        .execute()
    )
    return resp.data[0]


def insert_entry(sb, user_id: str, entry_date: date, amount: int, message: str | None) -> None:
    sb.table("entries").insert(
        {
            "user_id": user_id,
            "entry_date": entry_date.isoformat(),
            "amount": amount,
            "message": message.strip() if message and message.strip() else None,
        }
    ).execute()


def fetch_scoreboard(sb) -> list[dict]:
    profiles = sb.table("profiles").select("*").execute().data

    entries = (
        sb.table("entries")
        .select("user_id, entry_date, amount, message, created_at")
        .gte("entry_date", CHALLENGE_START.isoformat())
        .lte("entry_date", CHALLENGE_END.isoformat())
        .order("created_at", desc=True)
        .execute()
        .data
    )
    entries_df = pd.DataFrame(entries)

    rows = []
    for profile in profiles:
        uid = profile["id"]
        challenge_type = profile["challenge_type"]
        target = TARGET[challenge_type]

        if not entries_df.empty:
            user_entries = entries_df[entries_df["user_id"] == uid]
        else:
            user_entries = entries_df

        total = int(user_entries["amount"].sum()) if not user_entries.empty else 0

        latest_message = None
        if not user_entries.empty:
            messaged = user_entries[
                user_entries["message"].notna() & (user_entries["message"].str.strip() != "")
            ]
            if not messaged.empty:
                latest_message = messaged.iloc[0]["message"]

        rows.append(
            {
                "user_id": uid,
                "display_name": profile["display_name"],
                "challenge_type": challenge_type,
                "total": total,
                "target": target,
                "latest_message": latest_message,
            }
        )

    rows.sort(key=lambda r: (r["total"] / r["target"]) if r["target"] else 0, reverse=True)
    return rows
