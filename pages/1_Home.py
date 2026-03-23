import streamlit as st
import pandas as pd
from datetime import datetime

CITY_OPTIONS = [
    "Amsterdam, Netherlands",
    "Barcelona, Spain",
    "Berlin, Germany",
    "Brussels, Belgium",
    "Dublin, Ireland",
    "Frankfurt, Germany",
    "Hamburg, Germany",
    "Lisbon, Portugal",
    "London, UK",
    "Madrid, Spain",
    "Manchester, UK",
    "Milan, Italy",
    "Munich, Germany",
    "Paris, France",
    "Rome, Italy",
    "Stockholm, Sweden",
    "Vienna, Austria",
    "Zurich, Switzerland",
    "Bangalore, India",
    "Chennai, India",
    "Delhi, India",
    "Gurgaon, India",
    "Hyderabad, India",
    "Mumbai, India",
    "Pune, India",
    "Singapore",
    "Dubai, UAE",
    "Abu Dhabi, UAE",
    "Doha, Qatar",
    "New York, USA",
    "Boston, USA",
    "Chicago, USA",
    "San Francisco, USA",
    "Seattle, USA",
    "Toronto, Canada",
    "Vancouver, Canada",
    "Sydney, Australia",
    "Melbourne, Australia",
    "Auckland, New Zealand",
    "Remote",
    "Hybrid",
]


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
div[data-testid="stSidebarNav"] a[href*='app']{display:none!important}
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
    profile = st.session_state.get("user_profile", {})
    with c1:
        role = st.text_input(
            "Job Title",
            placeholder="Head of Talent Acquisition",
            value=st.session_state.get("search_role", ""),
        )
        default_location = st.session_state.get(
            "search_location",
            profile.get("location", "")
            or (", ".join(profile.get("target_markets", [])) if profile.get("target_markets") else ""),
        )
        city_options = ["Custom / Other"] + CITY_OPTIONS
        if default_location and default_location in CITY_OPTIONS:
            default_index = city_options.index(default_location)
        else:
            default_index = 0
        city_choice = st.selectbox(
            "Location (city or market)",
            city_options,
            index=default_index,
        )
        custom_location = ""
        if city_choice == "Custom / Other":
            custom_location = st.text_input(
                "Custom location",
                placeholder="e.g. Hyderabad, Spain, Europe, Remote",
                value=default_location if default_location not in CITY_OPTIONS else "",
            )
        location = custom_location or (city_choice if city_choice != "Custom / Other" else "")
    with c2:
        seniority = st.multiselect(
            "Seniority",
            ["Director", "Head", "VP", "Senior Manager", "Associate Director", "Manager"],
            default=["Director", "Head", "VP", "Senior Manager", "Associate Director"],
        )
        other_seniority = st.text_input(
            "Other seniority levels (comma-separated, optional)",
            key="other_seniority_levels",
        )

    extra_seniority = [
        s.strip() for s in other_seniority.split(",") if s.strip()
    ]
    st.session_state.search_role = role
    st.session_state.search_location = location
    st.session_state.search_seniority = seniority + extra_seniority


col1, col2 = st.columns(2)
with col1:
    if st.button("▶ Search Jobs", use_container_width=True):
        with st.spinner("Searching jobs across the internet..."):
            from scrapers.scraper_public import search_jobs_serpapi, score_jobs_with_groq

            serpapi_key = st.session_state.get("serpapi_key", "")
            groq_key = st.session_state.get("groq_key", "")
            profile = st.session_state.get("user_profile", {})
            loc_basis = (location or profile.get("location", "") or "").lower()
            track_val = "A" if "india" in loc_basis else "B"
            jobs = search_jobs_serpapi(
                role or "talent acquisition manager",
                location or "Europe",
                track_val,
                serpapi_key,
            )
            if jobs:
                with st.spinner(f"Scoring {len(jobs)} jobs with AI..."):
                    jobs = score_jobs_with_groq(jobs, profile, groq_key)
                st.session_state.jobs = jobs
                try:
                    from engines.tracker import track_event
                    from engines.auth import save_user_data

                    email = st.session_state.get("user_email", "")
                    track_event(email, "job_search", {"role": role, "count": len(jobs)})
                    save_user_data(email, "jobs", jobs)
                except Exception:
                    pass
                st.success(f"✅ Found {len(jobs)} jobs, scored by AI!")
                st.rerun()
            else:
                st.warning("No jobs found. Try different search terms.")


with col2:
    if st.button("🧠 Score All Jobs", use_container_width=True):
        if st.session_state.get("groq_key") == "test_mode":
            st.info("Scoring skipped in test mode")
        else:
            st.info("Scoring not implemented yet")
