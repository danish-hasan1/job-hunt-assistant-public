import streamlit as st
import json
from docx import Document
import io

st.set_page_config(
    page_title="Setup - Job Hunt Assistant",
    page_icon="🎯",
    layout="centered",
)

st.markdown(
    """<style>
[data-testid="stAppViewContainer"]{background:#0f0f23}
[data-testid="stHeader"]{background:#0f0f23}
h1,h2,h3,p,label,.stMarkdown{color:white!important}
.stButton>button{background:#e94560!important;color:white!important;border:none;border-radius:8px;width:100%;font-weight:bold}
.card{background:#16213e;border:1px solid #0f3460;border-radius:12px;padding:20px;margin:10px 0}
div[data-testid="stSidebarNav"] a[href*='app']{display:none!important}
div[data-testid="stSidebarNav"] a[href*='landing']{display:none!important}
div[data-testid="stSidebarNav"] a[href*='login']{display:none!important}
</style>""",
    unsafe_allow_html=True,
)


if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

if "setup_step" not in st.session_state:
    st.session_state.setup_step = 1


def show_progress(current):
    steps = ["Upload CV", "Your Profile", "API Keys", "Ready!"]
    cols = st.columns(4)
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            color = (
                "#e94560"
                if i + 1 == current
                else ("#00aa00" if i + 1 < current else "#333")
            )
            st.markdown(
                f'<div style="text-align:center;padding:8px;background:{color};border-radius:8px;font-size:12px;color:white">{i+1}. {step}</div>',
                unsafe_allow_html=True,
            )


st.title("🎯 Job Hunt Assistant")
st.caption("Your personal AI-powered job search — free forever")
st.markdown("---")
show_progress(st.session_state.setup_step)
st.markdown("---")


if st.session_state.setup_step == 1:
    st.subheader("📄 Step 1: Upload Your CV")
    cv_file = st.file_uploader("Upload CV (.docx)", type=["docx"])
    if cv_file:
        doc = Document(io.BytesIO(cv_file.read()))
        cv_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        st.session_state.cv_text = cv_text
        st.session_state.cv_bytes = cv_file.getvalue()
        try:
            from engines.auth import save_cv

            email = st.session_state.get("user_email", "")
            if email:
                save_cv(email, cv_file.getvalue())
        except Exception:
            pass
        st.success(f"✅ CV uploaded! ({len(cv_text)} characters)")
        st.text_area("Preview:", cv_text[:400] + "...", height=120)
    if st.button("Next →"):
        if st.session_state.get("cv_text"):
            st.session_state.setup_step = 2
            st.rerun()
        else:
            st.warning("Please upload your CV first")

elif st.session_state.setup_step == 2:
    st.subheader("👤 Step 2: Your Profile")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Full Name *", placeholder="Your Name")
        email = st.text_input("Email *", placeholder="you@gmail.com")
        phone = st.text_input("Phone", placeholder="+91 9999999999")
        experience = st.number_input("Years Experience", 0, 40, 5)
    with c2:
        location = st.text_input("Current Location", placeholder="City, Country")
        relocate = st.selectbox("Open to Relocate?", ["Yes", "No"])
        notice = st.selectbox(
            "Notice Period",
            ["Immediate", "2 weeks", "1 month", "2 months", "3 months"],
        )
        sc1, sc2 = st.columns([2, 1])
        with sc1:
            min_salary = st.text_input(
                "Min Salary (Annual)", placeholder="60000 (annual)"
            )
        with sc2:
            salary_currency = st.selectbox(
                "Currency",
                ["EUR", "GBP", "USD", "INR", "AED", "CAD", "AUD", "SGD"],
            )
    suggested_roles = []
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

    base_roles = [
        "Talent Acquisition Manager",
        "Head of Talent",
        "VP Talent",
        "RPO Manager",
        "Associate Director Recruitment",
        "Recruitment Director",
        "Senior TA Manager",
    ]
    role_options = []
    for r in suggested_roles + base_roles:
        if r and r not in role_options:
            role_options.append(r)
    default_roles = suggested_roles or ["Head of Talent", "RPO Manager"]
    target_roles = st.multiselect(
        "Target Roles *",
        role_options,
        default=default_roles,
    )
    other_roles = st.text_input(
        "Other roles (comma-separated, optional)", key="other_target_roles"
    )
    target_markets = st.multiselect(
        "Target Markets *",
        ["Spain", "Belgium", "France", "Netherlands", "UK", "Germany", "Europe", "India", "UAE"],
        default=["Spain", "Belgium", "France", "Europe"],
    )
    industries = st.multiselect(
        "Preferred Industries",
        ["Pharma", "Life Sciences", "Tech", "Finance", "Consulting", "FMCG", "Any"],
        default=["Pharma", "Tech", "Consulting"],
    )
    cb, cn = st.columns(2)
    with cb:
        if st.button("← Back"):
            st.session_state.setup_step = 1
            st.rerun()
    with cn:
        if st.button("Next →"):
            missing = []
            if not name.strip():
                missing.append("Full Name")
            if not email.strip():
                missing.append("Email")
            extra_roles = [
                r.strip() for r in other_roles.split(",") if r.strip()
            ]
            all_roles = target_roles + extra_roles
            if not all_roles:
                missing.append("Target Roles")
            if not target_markets:
                missing.append("Target Markets")
            if not missing:
                st.session_state.user_profile = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "location": location,
                    "relocate": relocate == "Yes",
                    "notice_period": notice,
                    "min_salary": min_salary,
                    "salary_currency": salary_currency,
                    "min_salary_eur": min_salary,
                    "years_experience": experience,
                    "target_roles": all_roles,
                    "target_markets": target_markets,
                    "industries": industries,
                    "experience_markets": target_markets or ([location] if location else []),
                    "skills": [],
                }
                st.session_state.setup_step = 3
                st.rerun()
            else:
                st.warning("Please fill required fields (*): " + ", ".join(missing))

elif st.session_state.setup_step == 3:
    st.subheader("🔑 Step 3: API Keys")
    st.caption("All free. Never stored — stays in your browser session only.")
    st.markdown("**🤖 Groq API Key** (Required)")
    st.markdown(" `https://console.groq.com` ")
    st.caption(
        "Create a free Groq account, go to API Keys in the console, generate a key "
        "starting with `gsk_` and paste it here."
    )
    groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    st.markdown("**🔍 SerpAPI Key** (Required)")
    st.markdown(" `https://serpapi.com` ")
    st.caption(
        "Sign up on SerpAPI, open your dashboard, copy the API key from the top "
        "of the page and paste it here."
    )
    serpapi_key = st.text_input("SerpAPI Key", type="password", placeholder="...")
    st.markdown("**📧 Gmail** (Optional — for email applications)")
    st.markdown(" `https://support.google.com/accounts/answer/185833` ")
    st.caption(
        "Use a Gmail App Password, not your normal password. Turn on 2‑Step "
        "Verification in your Google Account, create an App Password for Mail, "
        "then paste the 16‑character password here."
    )
    gmail = st.text_input("Gmail Address", placeholder="you@gmail.com")
    gmail_pass = st.text_input(
        "Gmail App Password", type="password", placeholder="xxxx xxxx xxxx xxxx"
    )
    st.markdown("**✨ Gemini API Key** (Optional — better CV tailoring)")
    st.markdown(" `https://aistudio.google.com` ")
    st.caption(
        "Create a key in Google AI Studio, copy the `AIza...` key from the API Keys "
        "page and paste it here."
    )
    gemini_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...")
    with st.expander("Need more help? Click for detailed instructions"):
        st.markdown("**Groq API Key – detailed steps**")
        st.markdown(
            """1. Go to https://console.groq.com  
2. Sign up or log in  
3. Open the API Keys section in the left menu  
4. Click “Create API Key” and copy the key starting with `gsk_`  
5. Paste it into the Groq field above"""
        )
        st.markdown("**SerpAPI Key – detailed steps**")
        st.markdown(
            """1. Go to https://serpapi.com and create a free account  
2. After login, go to your dashboard  
3. Find the “API Key” box at the top of the page  
4. Click to copy the key  
5. Paste it into the SerpAPI field above"""
        )
        st.markdown("**Gmail App Password – detailed steps**")
        st.markdown(
            """1. Go to https://myaccount.google.com and open “Security”  
2. Turn on 2‑Step Verification if it is not enabled  
3. In the Security page, search for “App passwords”  
4. Choose “Mail” as the app and your device (or “Other”)  
5. Generate the 16‑character password and copy it  
6. Paste that password (without spaces) into the Gmail App Password field"""
        )
        st.markdown("**Gemini API Key – detailed steps**")
        st.markdown(
            """1. Go to https://aistudio.google.com  
2. Sign in with your Google account  
3. Open the “API Keys” section in the left menu  
4. Click “Create API key” and confirm  
5. Copy the key starting with `AIza` and paste it into the Gemini field"""
        )
    cb, cn = st.columns(2)
    with cb:
        if st.button("← Back"):
            st.session_state.setup_step = 2
            st.rerun()
    with cn:
        if st.button("🚀 Complete Setup"):
            if groq_key and serpapi_key:
                st.session_state.groq_key = groq_key
                st.session_state.serpapi_key = serpapi_key
                st.session_state.gmail_address = gmail
                st.session_state.gmail_password = gmail_pass
                st.session_state.gemini_key = gemini_key
                try:
                    from engines.auth import save_api_keys

                    email = st.session_state.get("user_email", "")
                    if email:
                        save_api_keys(
                            email, groq_key, serpapi_key, gmail, gmail_pass, gemini_key
                        )
                except Exception:
                    pass
                st.session_state.setup_complete = True
                try:
                    from engines.auth import save_user_data
                    from engines.tracker import track_signup

                    email = st.session_state.get("user_email", "")
                    if email:
                        save_user_data(
                            email,
                            "api_keys",
                            {
                                "groq": groq_key,
                                "serpapi": serpapi_key,
                                "gmail": gmail,
                                "gmail_pass": gmail_pass,
                                "gemini": gemini_key,
                            },
                        )
                        track_signup(st.session_state.user_profile)
                except Exception:
                    pass
                st.session_state.setup_step = 4
                try:
                    from engines.tracker import track_signup

                    track_signup(st.session_state.user_profile)
                except Exception:
                    pass
                st.rerun()
            else:
                st.warning("Groq and SerpAPI keys are required")

elif st.session_state.setup_step == 4:
    st.balloons()
    profile = st.session_state.get("user_profile", {})
    st.success(f"🎉 Welcome, {profile.get('name','there')}! You're all set up.")
    st.markdown(
        """
    **What you can do now:**
    - 🔍 Search jobs across the internet
    - 🧠 AI scoring against your profile
    - 📄 Tailored CV per application
    - 📧 Email applications with one click
    - 🎤 Interview prep packs
    """
    )
    if st.button("🚀 Go to Dashboard"):
        st.switch_page("pages/1_Home.py")
