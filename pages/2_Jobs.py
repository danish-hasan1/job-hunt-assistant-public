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

st.title("💼 Job Listings")
st.markdown("---")

jobs = st.session_state.get("jobs", [])
if not jobs:
    st.warning("No jobs found yet. Go to 🏠 Home and search first.")
    st.stop()


c1, c2, c3 = st.columns(3)
with c1:
    track_filter = st.selectbox(
        "Track",
        ["All", "Track A (Cross-border)", "Track B (Local/Regional)"],
    )
with c2:
    status_filter = st.selectbox("Status", ["All", "new", "approved", "rejected"])
with c3:
    min_score = st.slider("Min Score", 0, 100, 0)


filtered = jobs
if track_filter != "All":
    tv = "A" if "Track A" in track_filter else "B"
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
            track_value = job.get("track")
            if track_value == "A":
                track_label = "🌍 Cross-border (Track A)"
            elif track_value == "B":
                track_label = "🏙 Local / Regional (Track B)"
            else:
                track_label = "Track not set"
            st.markdown(f"**Track:** {track_label}")
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
                with st.spinner("Tailoring your CV..."):
                    from engines.cv_public import (
                        extract_cv_summary,
                        tailor_cv_summary,
                        generate_cover_letter,
                        create_tailored_cv_bytes,
                    )

                    groq_key = st.session_state.get("groq_key", "")
                    profile = st.session_state.get("user_profile", {})
                    cv_bytes = st.session_state.get("cv_bytes", None)
                    if not cv_bytes:
                        st.warning("Please upload your CV in setup first")
                    else:
                        cv_summary = extract_cv_summary(cv_bytes)
                        tailored = tailor_cv_summary(cv_summary, job, profile, groq_key)
                        cover_letter = generate_cover_letter(job, profile, groq_key)
                        tailored_cv_bytes = create_tailored_cv_bytes(
                            cv_bytes, tailored, job
                        )
                        st.session_state[f"cv_ready_{job['id']}"] = True
                        st.session_state[f"cv_summary_{job['id']}"] = tailored
                        st.session_state[f"cv_bytes_{job['id']}"] = tailored_cv_bytes
                        st.session_state[f"cl_{job['id']}"] = cover_letter
                        try:
                            from engines.tracker import track_event
                            from engines.auth import save_user_data

                            email = st.session_state.get("user_email", "")
                            track_event(
                                email,
                                "cv_generated",
                                {
                                    "company": job["company"],
                                    "role": job["title"],
                                },
                            )
                        except Exception:
                            pass
                        st.success("✅ CV tailored!")
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
                try:
                    from engines.auth import save_user_data

                    email = st.session_state.get("user_email", "")
                    if email:
                        save_user_data(email, "jobs", st.session_state.jobs)
                        save_user_data(
                            email,
                            "applications",
                            st.session_state.get("applications", []),
                        )
                except Exception:
                    pass
                st.rerun()

        if st.session_state.get(f"cv_ready_{job['id']}"):
            st.info("📄 **Tailored Summary:**")
            st.write(st.session_state.get(f"cv_summary_{job['id']}", ""))
            cv_b = st.session_state.get(f"cv_bytes_{job['id']}")
            if cv_b:
                st.download_button(
                    "⬇️ Download Tailored CV",
                    data=cv_b,
                    file_name=f"CV_{job['company']}_{job['title'][:20]}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"dl_{job['id']}",
                )
            cl = st.session_state.get(f"cl_{job['id']}", "")
            if cl:
                with st.expander("📝 View Cover Letter"):
                    st.text_area(
                        "Cover Letter",
                        cl,
                        height=300,
                        key=f"clview_{job['id']}",
                    )
                st.download_button(
                    "⬇️ Download Cover Letter",
                    data=cl.encode(),
                    file_name=f"CoverLetter_{job['company']}.txt",
                    mime="text/plain",
                    key=f"cldl_{job['id']}",
                )

        st.markdown("---")
        st.markdown("**📧 Email Application**")
        gmail = st.session_state.get("gmail_address", "")
        if not gmail:
            st.caption("Add Gmail in Settings to enable email applications")
        else:
            from engines.email_public import extract_email_from_jd, find_company_email_groq

            found_email = extract_email_from_jd(job.get("description", ""))
            if not found_email:
                if st.button("🔍 Find Company Email", key=f"femail_{job['id']}"):
                    with st.spinner("Searching..."):
                        found_email = find_company_email_groq(
                            job["company"], st.session_state.get("groq_key", "")
                        )
                        if found_email:
                            st.session_state[f"to_email_{job['id']}"] = found_email
                        else:
                            st.session_state[f"to_email_{job['id']}"] = ""
                            st.warning("No email found — enter manually")
            to_email = st.text_input(
                "Recipient email:",
                value=st.session_state.get(f"to_email_{job['id']}", found_email or ""),
                key=f"emailinput_{job['id']}",
            )
            if to_email and st.button("📧 Send Application", key=f"send_{job['id']}"):
                if not st.session_state.get(f"cv_ready_{job['id']}"):
                    st.warning("Generate CV first before sending!")
                else:
                    with st.spinner("Sending application..."):
                        from engines.email_public import (
                            send_application_email,
                            build_subject,
                            build_body,
                        )

                        profile = st.session_state.get("user_profile", {})
                        cv_bytes = st.session_state.get(f"cv_bytes_{job['id']}")
                        cl_text = st.session_state.get(f"cl_{job['id']}", "")
                        gmail_pass = st.session_state.get("gmail_password", "")
                        subject = build_subject(job, profile)
                        body = build_body(job, profile, cl_text)
                        success, message = send_application_email(
                            to_email,
                            subject,
                            body,
                            cv_bytes,
                            cl_text,
                            gmail,
                            gmail_pass,
                            profile,
                        )
                        if success:
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
                                    "score": job.get("score", 0),
                                    "cv_summary": st.session_state.get(
                                        f"cv_summary_{job['id']}", ""
                                    ),
                                }
                            )
                            try:
                                from engines.tracker import track_event
                                from engines.auth import save_user_data

                                email_addr = st.session_state.get("user_email", "")
                                track_event(
                                    email_addr,
                                    "email_applied",
                                    {"company": job["company"]},
                                )
                                save_user_data(
                                    email_addr,
                                    "applications",
                                    st.session_state.applications,
                                )
                            except Exception:
                                pass
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(message)
