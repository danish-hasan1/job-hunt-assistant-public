import streamlit as st


if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

if "setup_complete" not in st.session_state or not st.session_state.setup_complete:
    st.switch_page("pages/0_Setup.py")


st.set_page_config(
    page_title="⚙️ Settings - Job Hunt Assistant",
    page_icon="⚙️",
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


st.title("⚙️ Settings")
st.markdown("---")


profile = st.session_state.get("user_profile", {})


tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["👤 Profile", "🔑 API Keys", "🔄 Reset", "🔔 Job Alerts", "🎁 Refer Friends"]
)


with tab1:
    st.subheader("Your Profile")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Full Name", value=profile.get("name", ""))
        email = st.text_input("Email", value=profile.get("email", ""))
        phone = st.text_input("Phone", value=profile.get("phone", ""))
        location = st.text_input("Location", value=profile.get("location", ""))
    with c2:
        experience = st.number_input(
            "Years Experience", value=int(profile.get("years_experience", 5))
        )
        relocate = st.selectbox(
            "Open to Relocate?",
            ["Yes", "No"],
            index=0 if profile.get("relocate") else 1,
        )
        notice = st.selectbox(
            "Notice Period",
            ["Immediate", "2 weeks", "1 month", "2 months", "3 months"],
        )
        sc1, sc2 = st.columns([2, 1])
        with sc1:
            min_salary = st.text_input(
                "Min Salary (Annual)",
                value=str(
                    profile.get("min_salary", profile.get("min_salary_eur", ""))
                ),
            )
        with sc2:
            salary_currency = st.selectbox(
                "Currency",
                ["EUR", "GBP", "USD", "INR", "AED", "CAD", "AUD", "SGD"],
                index=["EUR", "GBP", "USD", "INR", "AED", "CAD", "AUD", "SGD"].index(
                    profile.get("salary_currency", "EUR")
                )
                if profile.get("salary_currency", "EUR")
                in ["EUR", "GBP", "USD", "INR", "AED", "CAD", "AUD", "SGD"]
                else 0,
            )
    suggested_roles = []
    cv_notes = {}
    try:
        from engines.gemini_engine import load_cv_notes

        cv_notes = load_cv_notes()
        for key in ["target_roles", "suggested_roles"]:
            val = cv_notes.get(key, [])
            if isinstance(val, str):
                suggested_roles.append(val)
            elif isinstance(val, list):
                suggested_roles.extend(val)
        strategy = cv_notes.get("job_search_strategy", {})
        for key in ["roles", "titles", "role_titles"]:
            val = strategy.get(key, [])
            if isinstance(val, str):
                suggested_roles.append(val)
            elif isinstance(val, list):
                suggested_roles.extend(val)
    except Exception:
        suggested_roles = []

    try:
        cv_bytes_state = st.session_state.get("cv_bytes")
        if cv_bytes_state:
            from engines.cv_public import infer_target_roles_from_cv

            groq_key = st.session_state.get("groq_key", "")
            inferred_roles = infer_target_roles_from_cv(cv_bytes_state, groq_key)
            for r in inferred_roles:
                if r and r not in suggested_roles:
                    suggested_roles.append(r)
    except Exception:
        pass

    base_roles = [
        "Product Manager",
        "Project Manager",
        "Operations Manager",
        "Business Analyst",
        "Customer Success Manager",
        "Sales Manager",
        "Marketing Manager",
        "Head of Department",
    ]
    role_options = []
    for r in suggested_roles + base_roles + profile.get("target_roles", []):
        if r and r not in role_options:
            role_options.append(r)
    existing_roles = profile.get("target_roles", [])
    default_roles = existing_roles or suggested_roles or base_roles[:2]
    target_roles = st.multiselect(
        "Target Roles",
        role_options,
        default=default_roles,
    )
    extra_existing_roles = [r for r in existing_roles if r not in default_roles]
    other_roles = st.text_input(
        "Other roles (comma-separated, optional)",
        value=", ".join(extra_existing_roles),
        key="settings_other_target_roles",
    )
    markets_suggested = []
    strategy = cv_notes.get("job_search_strategy", {}) if isinstance(cv_notes, dict) else {}
    for key in ["markets", "locations", "target_locations"]:
        val = strategy.get(key, [])
        if isinstance(val, str):
            markets_suggested.append(val)
        elif isinstance(val, list):
            markets_suggested.extend(val)
    base_markets = [
        "Remote",
        "Global",
        "Europe",
        "North America",
        "UK",
        "India",
        "Middle East",
        "APAC",
        "Latin America",
    ]
    saved_markets = profile.get("target_markets", [])
    market_options = []
    for m in markets_suggested + base_markets + saved_markets:
        if m and m not in market_options:
            market_options.append(m)
    default_markets = (
        [m for m in saved_markets if m in market_options]
        or markets_suggested
        or base_markets[:2]
    )
    target_markets = st.multiselect(
        "Target Markets",
        market_options,
        default=default_markets,
    )
    extra_existing_markets = [m for m in saved_markets if m not in default_markets]
    other_markets = st.text_input(
        "Other markets (comma-separated, optional)",
        value=", ".join(extra_existing_markets),
        key="settings_other_target_markets",
    )
    if st.button("💾 Save Profile"):
        all_roles = target_roles + [
            r.strip() for r in other_roles.split(",") if r.strip()
        ]
        all_markets = target_markets + [
            m.strip() for m in other_markets.split(",") if m.strip()
        ]
        st.session_state.user_profile.update(
            {
                "name": name,
                "email": email,
                "phone": phone,
                "location": location,
                "years_experience": experience,
                "relocate": relocate == "Yes",
                "notice_period": notice,
                "min_salary": min_salary,
                "salary_currency": salary_currency,
                "min_salary_eur": min_salary,
                "target_roles": all_roles,
                "target_markets": all_markets,
            }
        )
        try:
            from engines.auth import save_user_data

            email_val = st.session_state.get("user_email", "")
            if email_val:
                save_user_data(email_val, "profile", st.session_state.user_profile)
        except Exception:
            pass
        if all_roles:
            st.session_state.search_role = all_roles[0]
        else:
            st.session_state.search_role = ""
        st.session_state.search_locations = all_markets or (
            [location] if location else []
        )
        st.session_state.search_seniority = []
        st.success("✅ Profile saved!")


with tab2:
    st.subheader("API Keys")
    st.caption("Update your API keys here. Never shared or stored permanently.")
    groq = st.text_input(
        "Groq API Key",
        value=st.session_state.get("groq_key", ""),
        type="password",
    )
    serpapi = st.text_input(
        "SerpAPI Key",
        value=st.session_state.get("serpapi_key", ""),
        type="password",
    )
    gmail = st.text_input(
        "Gmail Address",
        value=st.session_state.get("gmail_address", ""),
    )
    gmail_pass = st.text_input(
        "Gmail App Password",
        value=st.session_state.get("gmail_password", ""),
        type="password",
    )
    gemini = st.text_input(
        "Gemini API Key",
        value=st.session_state.get("gemini_key", ""),
        type="password",
    )
    if st.button("💾 Save API Keys"):
        st.session_state.groq_key = groq
        st.session_state.serpapi_key = serpapi
        st.session_state.gmail_address = gmail
        st.session_state.gmail_password = gmail_pass
        st.session_state.gemini_key = gemini
        try:
            from engines.auth import save_api_keys

            email = st.session_state.get("user_email", "")
            if email:
                save_api_keys(email, groq, serpapi, gmail, gmail_pass, gemini)
            st.success("✅ API keys saved permanently!")
        except Exception:
            st.success("✅ API keys updated for this session")


with tab3:
    st.subheader("Reset")
    st.warning("This will clear all your data and return to setup.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Jobs Only"):
            st.session_state.jobs = []
            st.session_state.applications = []
            st.success("Jobs cleared!")
    with col2:
        if st.button("🔄 Full Reset — Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("pages/0_Setup.py")


with tab4:
    st.subheader("🔔 Job Alerts")
    st.caption("Get email notifications when new matching jobs are found")

    from engines.alerts import save_alert, get_user_alerts, delete_alert

    email = st.session_state.get("user_email", "")
    profile = st.session_state.get("user_profile", {})

    st.markdown("**Set up a new alert:**")
    c1, c2, c3 = st.columns(3)
    with c1:
        alert_role = st.text_input(
            "Job Title",
            value=profile.get("target_roles", [""])[0]
            if profile.get("target_roles")
            else "",
            key="alert_role",
        )
    with c2:
        alert_location = st.text_input(
            "Location",
            value=profile.get("target_markets", ["Europe"])[0]
            if profile.get("target_markets")
            else "Europe",
            key="alert_location",
        )
    with c3:
        alert_freq = st.selectbox("Frequency", ["daily", "weekly"], key="alert_freq")

    if st.button("➕ Add Alert", key="add_alert"):
        if alert_role and alert_location:
            gmail_check = st.session_state.get("gmail_address", "")
            if not gmail_check:
                st.warning("Please add Gmail in API Keys tab first")
            else:
                ok = save_alert(email, alert_role, alert_location, alert_freq)
                if ok:
                    st.success(f"✅ Alert set for '{alert_role}' in {alert_location}!")
                    st.rerun()
        else:
            st.warning("Fill in role and location")

    st.markdown("---")
    st.markdown("**Your active alerts:**")
    alerts = get_user_alerts(email)
    if not alerts:
        st.info("No alerts set up yet.")
    for alert in alerts:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(
                f"🔔 **{alert['role']}** in {alert['location']} — {alert['frequency']}"
            )
        with c2:
            if st.button("🗑️ Delete", key=f"del_alert_{alert['id']}"):
                delete_alert(alert["id"])
                st.rerun()

    st.markdown("---")
    st.markdown("**Test your alert:**")
    if st.button("📧 Send Test Alert Now"):
        gmail = st.session_state.get("gmail_address", "")
        gmail_pass = st.session_state.get("gmail_password", "")
        if not gmail or not gmail_pass:
            st.warning("Add Gmail credentials first")
        else:
            from engines.alerts import send_job_alert_email

            test_jobs = st.session_state.get("jobs", [])[:3]
            if test_jobs:
                ok = send_job_alert_email(
                    email,
                    test_jobs,
                    alert_role or "Talent Acquisition",
                    alert_location or "Europe",
                    gmail,
                    gmail_pass,
                )
                if ok:
                    st.success("✅ Test alert sent! Check your email.")
                else:
                    st.error("Failed to send. Check Gmail credentials.")
            else:
                st.warning("Search for jobs first to test alerts")


with tab5:
    st.subheader("🎁 Refer Friends")
    st.caption("Share Job Hunt Assistant with friends and track who you've helped!")

    from engines.referral import get_or_create_referral_code, get_referral_stats

    email = st.session_state.get("user_email", "")
    profile = st.session_state.get("user_profile", {})
    name = profile.get("name", "User")

    code = get_or_create_referral_code(email, name)

    if code:
        st.markdown("**Your unique referral link:**")
        referral_url = f"https://job-hunt-assistant-public.streamlit.app?ref={code}"
        st.code(referral_url)
        st.caption(
            "Share this link with friends. When they sign up, they'll be linked to you."
        )

        st.markdown("**Share message:**")
        share_msg = f"""Hey! I've been using this free AI-powered job search tool called Job Hunt Assistant. 

 It finds jobs across the internet, scores them against your profile, tailors your CV automatically and even helps prep for interviews — all free! 

 Sign up here: {referral_url}"""
        st.text_area("Copy and share:", share_msg, height=150, key="share_msg")

        st.markdown("---")
        st.markdown("**Your referrals:**")
        referrals = get_referral_stats(email)
        if not referrals:
            st.info("No referrals yet. Share your link to get started!")
        else:
            st.success(f"🎉 You've referred {len(referrals)} people!")
            for r in referrals:
                st.markdown(
                    f"✅ {r['referred_email']} — joined {r['created_at'][:10]}"
                )
    else:
        st.error("Could not generate referral code. Try refreshing.")
