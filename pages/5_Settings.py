import streamlit as st


if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

if "setup_complete" not in st.session_state or not st.session_state.setup_complete:
    st.switch_page("pages/0_Setup.py")


st.set_page_config(
    page_title="Settings - Job Hunt Assistant",
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


tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔑 API Keys", "🔄 Reset"])


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
        min_salary = st.text_input(
            "Min Salary EUR", value=str(profile.get("min_salary_eur", ""))
        )
    target_roles = st.multiselect(
        "Target Roles",
        [
            "Talent Acquisition Manager",
            "Head of Talent",
            "VP Talent",
            "RPO Manager",
            "Associate Director Recruitment",
            "Recruitment Director",
            "Senior TA Manager",
        ],
        default=profile.get("target_roles", []),
    )
    target_markets = st.multiselect(
        "Target Markets",
        ["Spain", "Belgium", "France", "Netherlands", "UK", "Germany", "Europe", "India", "UAE"],
        default=profile.get("target_markets", []),
    )
    if st.button("💾 Save Profile"):
        st.session_state.user_profile.update(
            {
                "name": name,
                "email": email,
                "phone": phone,
                "location": location,
                "years_experience": experience,
                "relocate": relocate == "Yes",
                "notice_period": notice,
                "min_salary_eur": min_salary,
                "target_roles": target_roles,
                "target_markets": target_markets,
            }
        )
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
        st.success("✅ API keys updated!")


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
