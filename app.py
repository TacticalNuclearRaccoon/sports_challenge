from datetime import date

import streamlit as st

from config import CHALLENGE_END, CHALLENGE_LABEL, CHALLENGE_START
from lib.auth import render_onboarding, require_auth, sign_out
from lib.avatar import generate_avatar
from lib.badges import badge_path, compute_tier
from lib.data import fetch_profile, fetch_scoreboard, insert_entry
from lib.supabase_client import get_supabase

st.set_page_config(page_title="Burpee/Steps Challenge", page_icon=":octopus:", layout="centered")

require_auth()

sb = get_supabase()
user_id = st.session_state.user_id

if "profile" not in st.session_state:
    st.session_state.profile = fetch_profile(sb, user_id)

if st.session_state.profile is None:
    render_onboarding(user_id)
    st.stop()

profile = st.session_state.profile
challenge_type = profile["challenge_type"]
label = CHALLENGE_LABEL[challenge_type]

with st.sidebar:
    st.write(f"Logged in as **{profile['display_name']}**")
    if st.button("Log out"):
        sign_out()

tab_log, tab_scoreboard = st.tabs(["Log entry", "Scoreboard"])

with tab_log:
    st.subheader(f"Log your {label}")

    if st.session_state.pop("just_logged", None):
        st.success("Logged! Your entry has been recorded.")
        st.balloons()

    default_date = min(max(date.today(), CHALLENGE_START), CHALLENGE_END)
    with st.form("entry_form"):
        entry_date = st.date_input(
            "Date", value=default_date, min_value=CHALLENGE_START, max_value=CHALLENGE_END
        )
        amount = st.number_input(f"How many {label} today?", min_value=0, step=1)
        message = st.text_input("Optional message for the group", max_chars=200)
        submitted = st.form_submit_button("Log it")

    if submitted:
        insert_entry(sb, user_id, entry_date, int(amount), message)
        st.session_state.just_logged = True
        st.rerun()

with tab_scoreboard:
    st.subheader("Scoreboard")
    rows = fetch_scoreboard(sb)

    if not rows:
        st.info("No one has joined the challenge yet.")

    for row in rows:
        tier = compute_tier(row["total"], row["challenge_type"])
        badge = badge_path(row["challenge_type"], tier)
        avatar_bytes = generate_avatar(row["user_id"], row["display_name"])
        row_label = CHALLENGE_LABEL[row["challenge_type"]]

        col_avatar, col_badge, col_info = st.columns([1, 1, 4])
        with col_avatar:
            st.image(avatar_bytes, width=64)
        with col_badge:
            st.image(badge, width=64)
        with col_info:
            st.write(f"**{row['display_name']}** — {row['total']} / {row['target']} {row_label}")
            progress = row["total"] / row["target"] if row["target"] else 0
            st.progress(min(progress, 1.0))
            if row["latest_message"]:
                st.caption(f"“{row['latest_message']}”")
            elif row["total"] == 0:
                st.caption("No entries yet.")
        st.divider()
