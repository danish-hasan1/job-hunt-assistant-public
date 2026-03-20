import streamlit as st


st.set_page_config(page_title="Login - Job Hunt Assistant", page_icon="🎯", layout="centered")


st.markdown(
    """<style>
[data-testid="stAppViewContainer"]{background:#0f0f23}
[data-testid="stHeader"]{background:#0f0f23!important}
h1,h2,h3,p,label,.stMarkdown{color:white!important}
.stTextInput input{background:#1a1a2e;color:white;border:1px solid #e94560}
.stButton>button{background:#e94560!important;color:white!important;border:none;border-radius:8px;width:100%;font-weight:bold;padding:10px}
.card{background:#16213e;border:1px solid #0f3460;border-radius:12px;padding:30px;margin:20px 0}
</style>""",
    unsafe_allow_html=True,
)


st.title("🎯 Job Hunt Assistant")
st.caption("AI-powered job search — free forever")
st.markdown("---")


tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])


with tab1:
    st.subheader("Welcome back!")
    email = st.text_input("Email", placeholder="you@gmail.com", key="login_email")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("🚀 Login", key="login_btn"):
        if email and password:
            from engines.auth import login_user

            ok, user, msg = login_user(email, password)
            if ok:
                import json

                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_profile = {
                    "name": user.get("name", ""),
                    "email": user.get("email", ""),
                    "location": user.get("location", ""),
                    "target_roles": json.loads(user.get("target_roles", "[]")),
                    "target_markets": json.loads(user.get("target_markets", "[]")),
                    "years_experience": user.get("years_experience", 0),
                }
                from engines.auth import load_session_data

                keys, jobs, applications, cv_bytes = load_session_data(email)
                if jobs:
                    st.session_state.jobs = jobs
                if applications:
                    st.session_state.applications = applications
                if cv_bytes:
                    st.session_state.cv_bytes = cv_bytes
                if keys:
                    st.session_state.groq_key = keys.get("groq", "")
                    st.session_state.serpapi_key = keys.get("serpapi", "")
                    st.session_state.gmail_address = keys.get("gmail", "")
                    st.session_state.gmail_password = keys.get("gmail_pass", "")
                    st.session_state.gemini_key = keys.get("gemini", "")
                st.session_state.setup_complete = True
                st.success(f"Welcome back, {user.get('name','')}!")
                st.switch_page("pages/1_Home.py")
            else:
                st.error(msg)
        else:
            st.warning("Please enter email and password")


with tab2:
    st.subheader("Create your account")
    st.caption("Takes 2 minutes — completely free")
    reg_name = st.text_input("Full Name", placeholder="Your Name", key="reg_name")
    reg_email = st.text_input("Email", placeholder="you@gmail.com", key="reg_email")
    reg_pass = st.text_input("Password", type="password", key="reg_pass")
    reg_pass2 = st.text_input("Confirm Password", type="password", key="reg_pass2")
    if st.button("📝 Create Account", key="reg_btn"):
        if reg_name and reg_email and reg_pass:
            if reg_pass != reg_pass2:
                st.error("Passwords don't match")
            else:
                from engines.auth import register_user

                ok, msg = register_user(
                    reg_email,
                    reg_pass,
                    {
                        "name": reg_name,
                        "email": reg_email,
                        "location": "",
                        "target_roles": [],
                        "target_markets": [],
                        "years_experience": 0,
                    },
                )
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.user_email = reg_email
                    st.session_state.user_profile = {
                        "name": reg_name,
                        "email": reg_email,
                    }
                    st.session_state.setup_complete = False
                    st.success("Account created! Let's set up your profile.")
                    st.switch_page("pages/0_Setup.py")
                else:
                    st.error(msg)
        else:
            st.warning("Please fill all fields")
