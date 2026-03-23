import streamlit as st
import pandas as pd


if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

if "setup_complete" not in st.session_state or not st.session_state.setup_complete:
    st.switch_page("pages/0_Setup.py")


st.set_page_config(
    page_title="📋 Applications - Job Hunt Assistant",
    page_icon="📋",
    layout="wide",
)
st.markdown(
    """<style>
[data-testid="stAppViewContainer"]{background:#0f0f23}
[data-testid="stSidebar"]{background:#1a1a2e}
[data-testid="stSidebar"] *{color:white!important}
[data-testid="stHeader"]{background:#0f0f23!important}
h1,h2,h3,p,label{color:white!important}
.stButton>button{background:#e94560!important;color:white!important;border:none;border-radius:8px;font-weight:bold}
div[data-testid="stSidebarNav"] a{padding:8px 16px;margin:2px 8px;border-radius:8px;font-weight:500}
div[data-testid="stSidebarNav"] a[aria-current="page"]{background:#1f2937!important;font-weight:600}
div[data-testid="stSidebarNav"] a[href*='landing']{display:none!important}
div[data-testid="stSidebarNav"] a[href*='login']{display:none!important}
</style>""",
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown(
        f"👤 **{st.session_state.get('user_profile', {}).get('name', '')}**"
    )
    st.caption(st.session_state.get("user_email", ""))
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/login.py")


st.title("📋 Applications Tracker")
st.markdown("---")


applications = st.session_state.get("applications", [])


if not applications:
    st.info("No applications yet. Go to 💼 Jobs, approve a job and click 'Mark Applied'.")
    st.stop()


c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Applied", len(applications))
with c2:
    interviews = len([a for a in applications if a.get("status") == "interview"])
    st.metric("Interviews", interviews)
with c3:
    offers = len([a for a in applications if a.get("status") == "offer"])
    st.metric("Offers", offers)
with c4:
    track_a = len([a for a in applications if a.get("track") == "A"])
    st.metric("Track A / B", f"{track_a} / {len(applications) - track_a}")


st.markdown("---")


df = pd.DataFrame(applications)[
    ["company", "role", "location", "track", "status", "date_applied", "score"]
]
df.columns = ["Company", "Role", "Location", "Track", "Status", "Date Applied", "Score"]
st.dataframe(df, use_container_width=True, hide_index=True)


st.markdown("---")


st.subheader("📝 Update Status")
for app in applications:
    with st.expander(
        f"{'✅' if app['status']=='applied' else '🎤' if app['status']=='interview' else '🎉'} {app['role']} at {app['company']}"
    ):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Applied:** {app['date_applied']}")
            st.markdown(f"**Location:** {app['location']}")
            st.markdown(f"**Score:** {app['score']}/100")
        with c2:
            track_value = app.get("track")
            if track_value == "A":
                track_label = "🌍 Cross-border (Track A)"
            elif track_value == "B":
                track_label = "🏙 Local / Regional (Track B)"
            else:
                track_label = "Track not set"
            st.markdown(f"**Track:** {track_label}")
            st.markdown(f"**Status:** {app['status'].upper()}")
        if app.get("cv_summary"):
            st.markdown(f"**CV Summary used:** {app['cv_summary'][:200]}...")
        ca, cb, cc = st.columns(3)
        with ca:
            if st.button("🎤 Interview Scheduled", key=f"int_{app['id']}"):
                app["status"] = "interview"
                st.rerun()
        with cb:
            if st.button("🎉 Offer Received", key=f"off_{app['id']}"):
                app["status"] = "offer"
                st.rerun()
        with cc:
            if st.button("❌ Rejected", key=f"rej_{app['id']}"):
                app["status"] = "rejected"
                st.rerun()
