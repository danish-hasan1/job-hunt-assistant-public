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


tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Register", "🔑 Forgot Password"])


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
    ref_code = st.text_input(
        "Referral code (optional)",
        placeholder="DANISH1234",
        key="ref_code",
    )
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
                    if ref_code:
                        from engines.referral import apply_referral_code

                        apply_referral_code(reg_email, ref_code)
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


with tab3:
    st.subheader("Reset your password")
    st.caption("We'll send a 6-digit code to your email")

    if "reset_stage" not in st.session_state:
        st.session_state.reset_stage = "email"

    if st.session_state.reset_stage == "email":
        reset_email = st.text_input(
            "Your email", placeholder="you@gmail.com", key="reset_email"
        )
        reset_gmail = st.text_input(
            "Your Gmail (to receive code)",
            placeholder="sender@gmail.com",
            key="reset_gmail",
        )
        reset_gmail_pass = st.text_input(
            "Gmail App Password", type="password", key="reset_gmail_pass"
        )
        if st.button("📨 Send Reset Code", key="send_reset"):
            if reset_email and reset_gmail and reset_gmail_pass:
                from engines.auth import (
                    generate_reset_code,
                    save_reset_code,
                    send_reset_email,
                    login_user,
                )

                ok, _, _ = login_user(reset_email, "dummy_check_exists")
                exists = ok or True
                code = generate_reset_code()
                save_reset_code(reset_email, code)
                sent = send_reset_email(
                    reset_email, code, reset_gmail, reset_gmail_pass
                )
                if sent:
                    st.session_state.reset_email_val = reset_email
                    st.session_state.reset_stage = "code"
                    st.success("✅ Code sent! Check your email.")
                    st.rerun()
                else:
                    st.error("Failed to send email. Check your Gmail credentials.")
            else:
                st.warning("Fill all fields")

    elif st.session_state.reset_stage == "code":
        st.info(f"Code sent to {st.session_state.get('reset_email_val','')}")
        code_input = st.text_input(
            "Enter 6-digit code", placeholder="123456", key="code_input"
        )
        new_pass = st.text_input("New password", type="password", key="new_pass")
        new_pass2 = st.text_input(
            "Confirm new password", type="password", key="new_pass2"
        )
        if st.button("🔐 Reset Password", key="do_reset"):
            if new_pass != new_pass2:
                st.error("Passwords don't match")
            elif len(new_pass) < 6:
                st.error("Password must be at least 6 characters")
            else:
                from engines.auth import verify_reset_code, reset_password

                ok, msg = verify_reset_code(
                    st.session_state.reset_email_val, code_input
                )
                if ok:
                    ok2, msg2 = reset_password(
                        st.session_state.reset_email_val, new_pass
                    )
                    if ok2:
                        st.success("✅ Password reset! Please login.")
                        st.session_state.reset_stage = "email"
                        st.rerun()
                    else:
                        st.error(msg2)
                else:
                    st.error(msg)
        if st.button("← Back", key="reset_back"):
            st.session_state.reset_stage = "email"
            st.rerun()

