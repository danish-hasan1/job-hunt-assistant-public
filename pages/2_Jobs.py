import streamlit as st
from datetime import date


if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

if "setup_complete" not in st.session_state or not st.session_state.setup_complete:
    st.switch_page("pages/0_Setup.py")


st.set_page_config(page_title="Jobs - Job Hunt Assistant", page_icon="💼", layout="wide")
st.markdown(
    """<style>
[data-testid="stAppViewContainer"]{background:#0f0f23}
[data-testid="stSidebar"]{background:#1a1a2e}
[data-testid="stSidebar"] *{color:white!important}
[data-testid="stHeader"]{background:#0f0f23!important}
h1,h2,h3,p,label{color:white!important}
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

st.title("💼 Job Listings")
st.markdown("---")

jobs = st.session_state.get("jobs", [])
if not jobs:
    st.warning("No jobs found yet. Go to 🏠 Home and search first.")
    st.stop()


c1, c2, c3 = st.columns(3)
with c1:
    track_filter = st.selectbox("Track", ["All", "A - India Based", "B - Europe Direct"])
with c2:
    status_filter = st.selectbox("Status", ["All", "new", "approved", "rejected"])
with c3:
    min_score = st.slider("Min Score", 0, 100, 0)


filtered = jobs
if track_filter != "All":
    tv = "A" if "A" in track_filter else "B"
    filtered = [j for j in filtered if j.get("track") == tv]
if status_filter != "All":
    filtered = [j for j in filtered if j.get("status") == status_filter]
if min_score > 0:
    filtered = [j for j in filtered if j.get("score", 0) >= min_score]


st.caption(f"Showing {len(filtered)} of {len(jobs)} jobs")


for job in filtered:
    score = job.get("score", 0)
    status = job.get("status", "new")
    status_emoji = {"new": "🔵", "approved": "🟢", "rejected": "🔴", "applied": "✅"}.get(
        status, "🔵"
    )
    with st.expander(
        f"{status_emoji} {job['title']} | {job['company']} | {job['location']} | Score: {score}"
    ):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**Company:** {job['company']}")
            st.markdown(f"**Location:** {job['location']}")
        with c2:
            st.markdown(
                f"**Track:** {'🇮🇳 India-Based' if job.get('track')=='A' else '🇪🇺 Europe Direct'}"
            )
            st.markdown(f"**Source:** {job.get('source','LinkedIn')}")
        with c3:
            st.markdown(f"**Score:** {score}/100")
            if job.get("url"):
                st.markdown(f"[🔗 View Job]({job['url']})")
        if job.get("description"):
            st.markdown(f"**Description:** {job['description'][:300]}...")
        st.markdown("---")
        ca, cb, cc, cd = st.columns(4)
        with ca:
            if st.button("✅ Approve", key=f"ap_{job['id']}"):
                job["status"] = "approved"
                st.rerun()
        with cb:
            if st.button("❌ Reject", key=f"rj_{job['id']}"):
                job["status"] = "rejected"
                st.rerun()
        with cc:
            if st.button("📄 Generate CV", key=f"cv_{job['id']}"):
                with st.spinner("Generating tailored CV..."):
                    groq_key = st.session_state.get("groq_key")
                    profile = st.session_state.get("user_profile", {})
                    cv_text = st.session_state.get("cv_text", "")
                    if groq_key == "test_mode":
                        st.session_state[f"cv_ready_{job['id']}"] = True
                        st.session_state[f"cv_summary_{job['id']}"] = (
                            f"Tailored summary for {job['title']} at {job['company']} — test mode"
                        )
                        st.success("✅ CV generated! (Test mode)")
                    else:
                        from groq import Groq

                        client = Groq(api_key=groq_key)
                        prompt = (
                            f"Tailor this CV summary for: {job['title']} at {job['company']}.\n"
                            f"JD: {job['description'][:500]}\n"
                            f"CV: {cv_text[:500]}\n"
                            f"Return only 4-5 sentences."
                        )
                        r = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}],
                        )
                        st.session_state[f"cv_summary_{job['id']}"] = r.choices[0].message.content
                        st.session_state[f"cv_ready_{job['id']}"] = True
                        st.success("✅ CV tailored!")
                    try:
                        from engines.tracker import track_event

                        profile = st.session_state.get("user_profile", {})
                        track_event(
                            profile.get("email", "anonymous"),
                            "cv_generated",
                            {"company": job["company"], "role": job["title"]},
                        )
                    except Exception:
                        pass
        with cd:
            if st.button("📋 Mark Applied", key=f"done_{job['id']}"):
                job["status"] = "applied"
                if "applications" not in st.session_state:
                    st.session_state.applications = []
                st.session_state.applications.append(
                    {
                        "id": len(st.session_state.applications) + 1,
                        "company": job["company"],
                        "role": job["title"],
                        "location": job["location"],
                        "track": job.get("track"),
                        "status": "applied",
                        "date_applied": date.today().isoformat(),
                        "score": score,
                        "cv_summary": st.session_state.get(
                            f"cv_summary_{job['id']}", ""
                        ),
                    }
                )
                st.rerun()

        if st.session_state.get(f"cv_ready_{job['id']}"):
            st.info("📄 **Tailored Summary:**")
            st.write(st.session_state.get(f"cv_summary_{job['id']}", ""))

        st.markdown("---")
        st.markdown("**📧 Email Application**")
        gmail = st.session_state.get("gmail_address", "")
        if not gmail:
            st.caption("Add Gmail in setup to enable email applications")
        else:
            to_email = st.text_input("Recipient email:", key=f"email_{job['id']}")
            if st.button("📧 Send Application", key=f"send_{job['id']}"):
                st.info("Email sending coming soon!")
