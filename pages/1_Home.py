import streamlit as st
import pandas as pd
from datetime import datetime


if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

if "setup_complete" not in st.session_state or not st.session_state.setup_complete:
    st.switch_page("pages/0_Setup.py")


profile = st.session_state.get("user_profile", {})


st.set_page_config(page_title="Job Hunt Assistant", page_icon="🎯", layout="wide")


st.markdown(
    """<style>
[data-testid="stAppViewContainer"]{background:#0f0f23}
[data-testid="stSidebar"]{background:#1a1a2e}
[data-testid="stSidebar"] *{color:white!important}
[data-testid="stHeader"]{background:#0f0f23!important}
h1,h2,h3,p,label{color:white!important}
.metric-card{background:#16213e;border:1px solid #0f3460;border-radius:10px;padding:20px;text-align:center}
.metric-value{font-size:2.5em;font-weight:bold;color:#e94560}
.metric-label{font-size:0.9em;color:#aaa;margin-top:5px}
.stButton>button{background:#e94560!important;color:white!important;border:none;border-radius:8px;font-weight:bold}
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


st.title(f"Welcome back, {profile.get('name', 'there')}! 👋")
st.caption(f"Today is {datetime.now().strftime('%A, %d %B %Y')}")
st.markdown("---")


jobs = st.session_state.get("jobs", [])
applications = st.session_state.get("applications", [])
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{len(jobs)}</div><div class="metric-label">🔍 Jobs Found</div></div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{len(applications)}</div><div class="metric-label">✅ Applications Sent</div></div>',
        unsafe_allow_html=True,
    )
with c3:
    reviewed = len([j for j in jobs if j.get("status") == "approved"])
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{reviewed}</div><div class="metric-label">⏳ Awaiting Review</div></div>',
        unsafe_allow_html=True,
    )
with c4:
    interviews = len([a for a in applications if a.get("status") == "interview"])
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{interviews}</div><div class="metric-label">🎤 Interviews</div></div>',
        unsafe_allow_html=True,
    )


st.markdown("---")


st.subheader("🔍 Find Jobs")
with st.expander("⚙️ Search Settings", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        role = st.text_input("Job Title", placeholder="Head of Talent Acquisition")
        location = st.text_input("Location", placeholder="Spain, Europe, India")
    with c2:
        track = st.selectbox(
            "Track",
            ["Both", "A - India Based (EU-facing)", "B - Europe Direct"],
        )
        seniority = st.multiselect(
            "Seniority",
            ["Director", "Head", "VP", "Senior Manager", "Associate Director", "Manager"],
            default=["Director", "Head", "VP", "Senior Manager", "Associate Director"],
        )


col1, col2 = st.columns(2)
with col1:
    if st.button("▶ Search Jobs", use_container_width=True):
        if st.session_state.get("serpapi_key") == "test_mode":
            st.session_state.jobs = [
                {
                    "id": 1,
                    "title": "Head of Talent Acquisition",
                    "company": "Cielo Talent",
                    "location": "Barcelona, Spain",
                    "track": "B",
                    "score": 92,
                    "status": "new",
                    "url": " `https://linkedin.com` ",
                    "description": "Lead RPO delivery for pharma clients across Europe",
                    "source": "Google Jobs",
                },
                {
                    "id": 2,
                    "title": "RPO Delivery Manager",
                    "company": "Randstad",
                    "location": "Mumbai, India",
                    "track": "A",
                    "score": 85,
                    "status": "new",
                    "url": " `https://linkedin.com` ",
                    "description": "Manage European client recruitment from India delivery centre",
                    "source": "Google Jobs",
                },
                {
                    "id": 3,
                    "title": "Senior TA Manager EMEA",
                    "company": "Allegis Group",
                    "location": "Amsterdam, Netherlands",
                    "track": "B",
                    "score": 78,
                    "status": "new",
                    "url": " `https://linkedin.com` ",
                    "description": "Lead EMEA talent acquisition strategy",
                    "source": "Google Jobs",
                },
                {
                    "id": 4,
                    "title": "Associate Director Recruitment",
                    "company": "Korn Ferry",
                    "location": "Bengaluru, India",
                    "track": "A",
                    "score": 75,
                    "status": "new",
                    "url": " `https://linkedin.com` ",
                    "description": "Drive European hiring programmes from India hub",
                    "source": "Google Jobs",
                },
                {
                    "id": 5,
                    "title": "Global Talent Director",
                    "company": "BCG",
                    "location": "Madrid, Spain",
                    "track": "B",
                    "score": 88,
                    "status": "new",
                    "url": " `https://linkedin.com` ",
                    "description": "Lead global talent acquisition for BCG Europe",
                    "source": "Google Jobs",
                },
            ]
            st.success(f"✅ Found {len(st.session_state.jobs)} jobs! (Test mode)")
            st.rerun()
        else:
            with st.spinner("Searching jobs..."):
                from scrapers.scraper_google_jobs import scrape_custom_google_jobs

                serpapi_key = st.session_state.get("serpapi_key")
                results = scrape_custom_google_jobs(
                    role or "talent acquisition manager",
                    location or "Europe",
                    "B",
                    [],
                    serpapi_key,
                )
                st.session_state.jobs = results
                count = len(results)
                st.success(f"✅ Found {count} jobs!")
                try:
                    from engines.tracker import track_event

                    profile = st.session_state.get("user_profile", {})
                    track_event(
                        profile.get("email", "anonymous"),
                        "job_search",
                        {"role": role, "location": location, "results": count},
                    )
                except Exception:
                    pass
                st.rerun()


with col2:
    if st.button("🧠 Score All Jobs", use_container_width=True):
        if st.session_state.get("groq_key") == "test_mode":
            st.info("Scoring skipped in test mode")
        else:
            st.info("Scoring not implemented yet")
