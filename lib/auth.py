import streamlit as st

from lib.data import create_profile
from lib.supabase_client import get_supabase


def _handle_login(email: str, password: str) -> None:
    sb = get_supabase()
    try:
        resp = sb.auth.sign_in_with_password({"email": email, "password": password})
    except Exception as e:
        st.error(f"Login failed: {e}")
        return
    st.session_state.user_id = resp.user.id
    st.session_state.user_email = resp.user.email
    st.rerun()


def _handle_signup(email: str, password: str) -> None:
    sb = get_supabase()
    try:
        resp = sb.auth.sign_up({"email": email, "password": password})
    except Exception as e:
        st.error(f"Sign up failed: {e}")
        return

    if resp.user and not resp.user.identities:
        st.warning("That email may already be registered — try logging in instead.")
        return

    if resp.session is None:
        st.info("Check your email to confirm your account, then log in.")
        return

    st.session_state.user_id = resp.user.id
    st.session_state.user_email = resp.user.email
    st.rerun()


def _render_login_signup() -> None:
    st.title("🏋️ Burpee / Steps Challenge")
    login_tab, signup_tab = st.tabs(["Log in", "Sign up"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Log in"):
                _handle_login(email, password)

    with signup_tab:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            if st.form_submit_button("Sign up"):
                if not email or not password:
                    st.error("Email and password are required.")
                else:
                    _handle_signup(email, password)


def require_auth() -> None:
    """Gate the rest of the app behind login. Stops execution if not authenticated."""
    sb = get_supabase()

    if st.session_state.get("user_id"):
        session = sb.auth.get_session()
        if session is None:
            for key in ("user_id", "user_email", "sb", "profile"):
                st.session_state.pop(key, None)

    if not st.session_state.get("user_id"):
        _render_login_signup()
        st.stop()


def render_onboarding(user_id: str) -> dict | None:
    """First-login screen: pick a display name and a challenge. Returns the
    new profile dict once created, or None while still awaiting input."""
    sb = get_supabase()

    st.title("Welcome! Let's set up your profile")
    with st.form("onboarding_form"):
        display_name = st.text_input("Your name (shown on the scoreboard)")
        challenge_type = st.radio(
            "Pick your challenge",
            options=["burpees", "steps"],
            format_func=lambda c: "1500 burpees" if c == "burpees" else "150,000 steps",
        )
        submitted = st.form_submit_button("Start the challenge")

    if not submitted:
        return None

    if not display_name.strip():
        st.error("Please enter a display name.")
        return None

    create_profile(sb, user_id, display_name.strip(), challenge_type)
    st.rerun()


def sign_out() -> None:
    sb = get_supabase()
    sb.auth.sign_out()
    for key in ("user_id", "user_email", "sb", "profile"):
        st.session_state.pop(key, None)
    st.rerun()
