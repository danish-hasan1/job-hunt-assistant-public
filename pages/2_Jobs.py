import streamlit as st
from datetime import date


def _get_cv_bytes_for_session():
    cv = st.session_state.get("cv_bytes", None)
    if cv:
        return cv
    try:
        from engines.auth import load_cv

        email_val = st.session_state.get("user_email", "") or st.session_state.get(
            "user_profile", {}
        ).get("email", "")
        if email_val:
            loaded_cv = load_cv(email_val)
            if loaded_cv:
                st.session_state.cv_bytes = loaded_cv
                return loaded_cv
    except Exception:
        pass
    return None


if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

if "setup_complete" not in st.session_state or not st.session_state.setup_complete:
    st.switch_page("pages/0_Setup.py")

if not st.session_state.get("cv_bytes"):
    _get_cv_bytes_for_session()


st.set_page_config(page_title="💼 Jobs - Job Hunt Assistant", page_icon="💼", layout="wide")
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

st.title("💼 Job Listings")
st.markdown("---")

jobs = st.session_state.get("jobs", [])
if not jobs:
    st.warning("No jobs found yet. Go to 🏠 Home and search first.")
    st.stop()


focus_job_id = st.session_state.pop("focus_job_id", None)


c1, c2, c3, c4 = st.columns(4)
with c1:
    track_filter = st.selectbox(
        "Track",
        ["All", "Track A (Cross-border)", "Track B (Local/Regional)"],
    )
with c2:
    status_filter = st.selectbox("Status", ["All", "new", "approved", "rejected"])
with c3:
    min_score = st.slider("Min Score", 0, 100, 0)
with c4:
    source_options = ["All", "LinkedIn (any)", "LinkedIn Direct", "Other boards"]
    source_filter = st.selectbox("Source", source_options)

t1, t2 = st.columns(2)
with t1:
    hide_junior = st.checkbox("Hide junior / entry roles", value=False)
with t2:
    remote_only = st.checkbox("Remote-friendly only", value=False)


filtered = jobs
if track_filter != "All":
    tv = "A" if "Track A" in track_filter else "B"
    filtered = [j for j in filtered if j.get("track") == tv]
if status_filter != "All":
    filtered = [j for j in filtered if j.get("status") == status_filter]
if min_score > 0:
    filtered = [j for j in filtered if j.get("score", 0) >= min_score]
if source_filter != "All":
    if source_filter == "LinkedIn (any)":
        filtered = [
            j
            for j in filtered
            if "linkedin" in str(j.get("source", "")).lower()
        ]
    elif source_filter == "LinkedIn Direct":
        filtered = [j for j in filtered if j.get("source") == "LinkedIn Direct"]
    else:
        filtered = [
            j
            for j in filtered
            if "linkedin" not in str(j.get("source", "")).lower()
        ]
if hide_junior:
    junior_keys = [
        "junior",
        "entry level",
        "intern",
        "trainee",
        "graduate",
        "coordinator",
        "assistant",
        "sourcer",
    ]
    filtered = [
        j
        for j in filtered
        if not any(k in str(j.get("title", "")).lower() for k in junior_keys)
    ]
if remote_only:
    remote_keys = ["remote", "work from home", "home-based"]
    filtered = [
        j
        for j in filtered
        if any(
            k in str(j.get("location", "")).lower()
            or k in str(j.get("description", "")).lower()
            for k in remote_keys
        )
    ]

sort_options = ["Default order", "Score: high to low", "Cross-border first", "Local/Regional first"]
sort_choice = st.selectbox("Sort by", sort_options, index=0)

if sort_choice == "Score: high to low":
    filtered = sorted(filtered, key=lambda j: j.get("score", 0), reverse=True)
elif sort_choice == "Cross-border first":
    filtered = sorted(
        filtered,
        key=lambda j: 0 if j.get("track") == "A" else 1,
    )
elif sort_choice == "Local/Regional first":
    filtered = sorted(
        filtered,
        key=lambda j: 0 if j.get("track") == "B" else 1,
    )


st.caption(f"Showing {len(filtered)} of {len(jobs)} jobs")


for job in filtered:
    score = job.get("score", 0)
    status = job.get("status", "new")
    status_emoji = {"new": "🔵", "approved": "🟢", "rejected": "🔴", "applied": "✅"}.get(
        status, "🔵"
    )
    expanded_default = focus_job_id is not None and job.get("id") == focus_job_id
    with st.expander(
        f"{status_emoji} {job['title']} | {job['company']} | {job['location']} | Score: {score}",
        expanded=expanded_default,
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
        ca, cb, cc, cd, ce = st.columns(5)
        with ca:
            if st.button("✅ Approve", key=f"ap_{job['id']}"):
                job["status"] = "approved"
                st.rerun()
        with cb:
            if st.button("❌ Reject", key=f"rj_{job['id']}"):
                jobs_list = st.session_state.get("jobs", [])
                remaining = [j for j in jobs_list if j.get("id") != job.get("id")]
                st.session_state.jobs = remaining
                try:
                    from engines.auth import save_user_data

                    email = st.session_state.get("user_email", "")
                    if email:
                        save_user_data(email, "jobs", remaining)
                except Exception:
                    pass
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
                    cv_bytes = _get_cv_bytes_for_session()
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
            st.markdown("**🗂 Job notes & priority**")
            existing_notes = job.get("notes", "")
            existing_priority = job.get("priority", "Medium")
            notes_val = st.text_area(
                "Notes (only visible to you)",
                value=existing_notes,
                key=f"notes_{job['id']}",
                height=80,
            )
            priority_val = st.selectbox(
                "Priority",
                ["Low", "Medium", "High"],
                index=["Low", "Medium", "High"].index(
                    existing_priority if existing_priority in ["Low", "Medium", "High"] else "Medium"
                ),
                key=f"priority_{job['id']}",
            )
            if st.button("💾 Save notes", key=f"save_notes_{job['id']}"):
                job["notes"] = notes_val
                job["priority"] = priority_val
                jobs_list = st.session_state.get("jobs", [])
                for j in jobs_list:
                    if j.get("id") == job.get("id"):
                        j["notes"] = notes_val
                        j["priority"] = priority_val
                        break
                st.session_state.jobs = jobs_list
                try:
                    from engines.auth import save_user_data

                    email = st.session_state.get("user_email", "")
                    if email:
                        save_user_data(email, "jobs", st.session_state.jobs)
                except Exception:
                    pass
                st.success("Notes saved")

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
                        "notes": job.get("notes", ""),
                        "priority": job.get("priority", "Medium"),
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
        with ce:
            source_label = str(job.get("source", "") or "")
            is_linkedin_source = "linkedin" in source_label.lower()
            if is_linkedin_source:
                if st.button("⚡ 1‑Click LinkedIn Apply", key=f"ln_{job['id']}"):
                    profile = st.session_state.get("user_profile", {})
                    cv_bytes = _get_cv_bytes_for_session()
                    if not cv_bytes:
                        st.warning("Please upload your CV in setup first")
                    else:
                        import tempfile, os

                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix=".pdf"
                        ) as tmp:
                            tmp.write(cv_bytes)
                            cv_path = tmp.name
                        from engines.apply_agent import launch_apply_one_click

                        success, message = launch_apply_one_click(job, cv_path, profile)
                        if success:
                            st.info(message)
                        else:
                            st.error(message)

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
                cv_bytes = _get_cv_bytes_for_session()
                if not cv_bytes:
                    st.warning("Please upload your CV in setup first")
                else:
                    with st.spinner("Sending application..."):
                        from engines.email_public import (
                            send_application_email,
                            build_subject,
                            build_body,
                        )

                        profile = st.session_state.get("user_profile", {})
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

        st.markdown("---")
        st.markdown("**🤝 LinkedIn Outreach**")
        from engines.outreach_agent import (
            find_company_contact,
            find_hiring_managers,
            generate_outreach_message,
            launch_outreach_request,
            save_outreach,
        )

        profile = st.session_state.get("user_profile", {})
        groq_key = st.session_state.get("groq_key", "")
        contacts_key = f"outreach_contacts_{job['id']}"
        msgs_key_prefix = f"outreach_msg_{job['id']}_"
        hm_contacts_key = f"outreach_hm_contacts_{job['id']}"
        hm_msgs_prefix = f"outreach_hm_msg_{job['id']}_"

        if st.button("🔍 Find People at Company", key=f"find_contacts_{job['id']}"):
            with st.spinner(f"Searching LinkedIn for people at {job['company']}..."):
                contacts = find_company_contact(job["company"])
                st.session_state[contacts_key] = contacts

        contacts = st.session_state.get(contacts_key, [])
        if contacts:
            st.markdown("**People at this company**")
            for idx, c in enumerate(contacts):
                st.markdown(f"**{c['name']}** — {c['role']}")
                st.caption(c["url"])
                msg_key = f"{msgs_key_prefix}{idx}"
                if st.button("✉ Generate Message", key=f"gen_msg_{job['id']}_{idx}"):
                    message = ""
                    if groq_key and groq_key != "test_mode":
                        try:
                            from groq import Groq

                            client = Groq(api_key=groq_key)
                            message = generate_outreach_message(
                                c["name"],
                                c["company"],
                                job["title"],
                                profile,
                                client,
                            )
                        except Exception:
                            message = ""
                    if not message:
                        first_name = c["name"].split()[0]
                        message = (
                            f"Hi {first_name}, I’ve been following {c['company']} and your work there. "
                            f"My background in {', '.join(profile.get('target_roles', [])) or 'talent acquisition'} "
                            f"seems aligned with roles like {job['title']}. "
                            "Would you be open to connecting and sharing a quick view of how your team is set up?"
                        )
                    st.session_state[msg_key] = message
                message_val = st.session_state.get(msg_key, "")
                if message_val:
                    st.text_area(
                        "Connection message",
                        message_val,
                        height=120,
                        key=f"msg_area_{job['id']}_{idx}",
                    )
                    if st.button(
                        "🚀 Open LinkedIn & Prefill",
                        key=f"send_req_{job['id']}_{idx}",
                    ):
                        try:
                            save_outreach(
                                job.get("id"),
                                c.get("company"),
                                c.get("name"),
                                c.get("role"),
                                c.get("url"),
                                message_val,
                            )
                        except Exception:
                            pass
                        ok, info = launch_outreach_request(c["url"], message_val)
                        if ok:
                            st.info(info)
                        else:
                            st.error(info)

        if st.button(
            "🎯 Find 10 Hiring Managers (role-aligned)",
            key=f"find_hm_{job['id']}",
        ):
            with st.spinner(
                f"Searching LinkedIn for hiring managers at {job['company']}..."
            ):
                target_roles = profile.get("target_roles", [])
                role_hint = ", ".join(target_roles[:3]) if target_roles else job["title"]
                hm_contacts, hm_errors = find_hiring_managers(
                    job["company"], role_hint, max_results=10
                )
                st.session_state[hm_contacts_key] = hm_contacts
                if hm_errors:
                    st.session_state[f"hm_errors_{job['id']}"] = hm_errors

        hm_contacts = st.session_state.get(hm_contacts_key, [])
        if hm_contacts:
            st.markdown("**Hiring managers relevant to your roles**")
            for idx, c in enumerate(hm_contacts):
                st.markdown(f"**{c['contact_name']}** — {c['contact_role']}")
                st.caption(c["linkedin_url"])
                msg_key = f"{hm_msgs_prefix}{idx}"
                if st.button(
                    "✉ Generate Message",
                    key=f"gen_hm_msg_{job['id']}_{idx}",
                ):
                    message = ""
                    if groq_key and groq_key != "test_mode":
                        try:
                            from groq import Groq

                            client = Groq(api_key=groq_key)
                            message = generate_outreach_message(
                                c["contact_name"],
                                c["company"],
                                job["title"],
                                profile,
                                client,
                            )
                        except Exception:
                            message = ""
                    if not message:
                        first_name = c["contact_name"].split()[0]
                        message = (
                            f"Hi {first_name}, I’ve been following {c['company']} and your work there. "
                            f"My background in {', '.join(profile.get('target_roles', [])) or 'talent acquisition'} "
                            f"seems aligned with leadership roles in your team. "
                            "Would you be open to connecting for a brief exchange on how your function is set up?"
                        )
                    st.session_state[msg_key] = message
                message_val = st.session_state.get(msg_key, "")
                if message_val:
                    st.text_area(
                        "Connection message",
                        message_val,
                        height=120,
                        key=f"hm_msg_area_{job['id']}_{idx}",
                    )
                    if st.button(
                        "🚀 Open LinkedIn & Prefill",
                        key=f"send_hm_req_{job['id']}_{idx}",
                    ):
                        try:
                            save_outreach(
                                job.get("id"),
                                c.get("company"),
                                c.get("contact_name"),
                                c.get("contact_role"),
                                c.get("linkedin_url"),
                                message_val,
                            )
                        except Exception:
                            pass
                        ok, info = launch_outreach_request(c["linkedin_url"], message_val)
                        if ok:
                            st.info(info)
                        else:
                            st.error(info)
