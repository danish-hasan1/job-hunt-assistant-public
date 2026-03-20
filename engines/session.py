import streamlit as st


def get_api_keys():
    return {
        "groq": st.session_state.get("groq_key", ""),
        "gemini": st.session_state.get("gemini_key", ""),
        "gmail": st.session_state.get("gmail_address", ""),
        "gmail_pass": st.session_state.get("gmail_password", ""),
        "serpapi": st.session_state.get("serpapi_key", ""),
    }


def get_profile():
    return st.session_state.get("user_profile", {})


def get_cv_text():
    return st.session_state.get("cv_text", "")


def is_setup_complete():
    keys = get_api_keys()
    return bool(keys["groq"] and get_profile() and get_cv_text())

