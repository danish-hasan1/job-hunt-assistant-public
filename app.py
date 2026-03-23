import streamlit as st


st.set_page_config(
    page_title="Job Hunt Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)


if not st.session_state.get("logged_in"):
    st.switch_page("pages/landing.py")
elif not st.session_state.get("setup_complete"):
    st.switch_page("pages/0_Setup.py")
else:
    pages = [
        st.Page("pages/1_Home.py", title="Home", icon="🎯"),
        st.Page("pages/0_Setup.py", title="Setup", icon="🛠"),
        st.Page("pages/2_Jobs.py", title="Jobs", icon="💼"),
        st.Page("pages/3_Applications.py", title="Applications", icon="📋"),
        st.Page("pages/4_Interview_Prep.py", title="Interview Prep", icon="🎤"),
        st.Page("pages/5_Settings.py", title="Settings", icon="⚙️"),
    ]
    nav = st.navigation(pages)
    nav.run()
