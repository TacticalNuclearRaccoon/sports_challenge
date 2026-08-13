import streamlit as st
from supabase import Client, create_client


def get_supabase() -> Client:
    """Return this browser session's Supabase client.

    Deliberately stored in st.session_state rather than st.cache_resource:
    a cached resource would be a single Client shared by every visitor on
    this server process, and supabase-py mutates a shared Authorization
    header in place on auth events, so one friend's request could execute
    as another friend's. One Client per session avoids that.
    """
    if "sb" not in st.session_state:
        st.session_state.sb = create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["anon_key"],
        )
    return st.session_state.sb
