import streamlit as st
import json
from docx import Document
import io

try:
    import geonamescache
except ImportError:
    geonamescache = None


@st.cache_resource
def get_city_options():
    if geonamescache is None:
        return [
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
            "Copenhagen, Denmark",
            "Oslo, Norway",
            "Helsinki, Finland",
            "Prague, Czech Republic",
            "Warsaw, Poland",
            "Budapest, Hungary",
            "Bucharest, Romania",
            "Athens, Greece",
            "Bangalore, India",
            "Chennai, India",
            "Delhi, India",
            "Gurgaon, India",
            "Hyderabad, India",
            "Mumbai, India",
            "Pune, India",
            "Noida, India",
            "Ghaziabad, India",
            "Kolkata, India",
            "Jaipur, India",
            "Chandigarh, India",
            "Mohali, India",
            "Indore, India",
            "Ahmedabad, India",
            "Kochi, India",
            "Trivandrum, India",
            "Nagpur, India",
            "Surat, India",
            "Lucknow, India",
            "Coimbatore, India",
            "Singapore",
            "Dubai, UAE",
            "Abu Dhabi, UAE",
            "Doha, Qatar",
            "Riyadh, Saudi Arabia",
            "Jeddah, Saudi Arabia",
            "New York, USA",
            "Boston, USA",
            "Chicago, USA",
            "San Francisco, USA",
            "Seattle, USA",
            "Los Angeles, USA",
            "Austin, USA",
            "Dallas, USA",
            "Toronto, Canada",
            "Vancouver, Canada",
            "Montreal, Canada",
            "Sydney, Australia",
            "Melbourne, Australia",
            "Brisbane, Australia",
            "Auckland, New Zealand",
            "Remote",
            "Hybrid",
        ]
    gc = geonamescache.GeonamesCache()
    countries = gc.get_countries()
    raw_cities = gc.get_cities().values()
    names = set()
    for c in raw_cities:
        code = c.get("countrycode")
        country = countries.get(code, {}).get("name", "")
        if country:
            names.add(f"{c.get('name')}, {country}")
        else:
            names.add(c.get("name"))
    names.update(["Remote", "Hybrid"])
    return sorted(names)


CITY_OPTIONS = get_city_options()

st.set_page_config(
    page_title="🛠 Setup - Job Hunt Assistant",
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
div[data-testid="stSidebarNav"] a{padding:8px 16px;margin:2px 8px;border-radius:8px;font-weight:500}
div[data-testid="stSidebarNav"] a[aria-current="page"]{background:#1f2937!important;font-weight:600}
div[data-testid="stSidebarNav"] a[href*='landing']{display:none!important}
div[data-testid="stSidebarNav"] a[href*='login']{display:none!important}
</style>""",
    unsafe_allow_html=True,
)


if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

if "setup_step" not in st.session_state:
    if st.session_state.get("setup_complete"):
        st.session_state.setup_step = 4
    else:
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
st.caption("Your personal AI-powered job search")
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
    existing_profile = st.session_state.get("user_profile", {})
    cv_profile_defaults = st.session_state.get("cv_profile_defaults", {})
    if not cv_profile_defaults:
        try:
            cv_bytes_state = st.session_state.get("cv_bytes")
            if cv_bytes_state:
                from engines.cv_public import extract_basic_profile_from_cv

                cv_profile_defaults = extract_basic_profile_from_cv(cv_bytes_state)
                st.session_state.cv_profile_defaults = cv_profile_defaults
        except Exception:
            cv_profile_defaults = {}
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input(
            "Full Name *",
            placeholder="Your Name",
            value=existing_profile.get("name", "") or cv_profile_defaults.get("name", ""),
        )
        email = st.text_input(
            "Email *",
            placeholder="you@gmail.com",
            value=existing_profile.get("email", "") or cv_profile_defaults.get("email", ""),
        )
        phone = st.text_input(
            "Phone",
            placeholder="+91 9999999999",
            value=existing_profile.get("phone", "") or cv_profile_defaults.get("phone", ""),
        )
        experience = st.number_input(
            "Years Experience",
            0,
            40,
            int(
                existing_profile.get(
                    "years_experience", cv_profile_defaults.get("years_experience", 5)
                )
            ),
        )
    with c2:
        existing_location = existing_profile.get("location", "") or cv_profile_defaults.get(
            "location", ""
        )
        city_options = ["Custom / Other"] + CITY_OPTIONS
        if existing_location and existing_location in CITY_OPTIONS:
            default_index = city_options.index(existing_location)
        else:
            default_index = 0
        city_choice = st.selectbox(
            "Current Location (city)",
            city_options,
            index=default_index,
        )
        custom_current_location = ""
        if city_choice == "Custom / Other":
            custom_current_location = st.text_input(
                "Current location (free text)",
                placeholder="City, Country",
                value=existing_location if existing_location not in CITY_OPTIONS else "",
            )
        location = (
            custom_current_location
            or (city_choice if city_choice != "Custom / Other" else "")
        )
        preferred_saved = existing_profile.get("preferred_locations", [])
        preferred_locations = st.multiselect(
            "Preferred Locations",
            CITY_OPTIONS,
            default=[p for p in preferred_saved if p in CITY_OPTIONS],
            placeholder="Type to search and select multiple locations",
        )
        relocate_default = "Yes" if existing_profile.get("relocate", True) else "No"
        relocate = st.selectbox(
            "Open to Relocate?",
            ["Yes", "No"],
            index=["Yes", "No"].index(relocate_default),
        )
        notice_options = ["Immediate", "2 weeks", "1 month", "2 months", "3 months"]
        existing_notice = existing_profile.get("notice_period")
        notice_index = (
            notice_options.index(existing_notice)
            if existing_notice in notice_options
            else 0
        )
        notice = st.selectbox("Notice Period", notice_options, index=notice_index)
        sc1, sc2 = st.columns([2, 1])
        with sc1:
            min_salary = st.text_input(
                "Min Salary (Annual)",
                placeholder="60000 (annual)",
                value=str(existing_profile.get("min_salary", "")),
            )
        with sc2:
            currency_options = ["EUR", "GBP", "USD", "INR", "AED", "CAD", "AUD", "SGD"]
            existing_currency = existing_profile.get("salary_currency", "EUR")
            currency_index = (
                currency_options.index(existing_currency)
                if existing_currency in currency_options
                else 0
            )
            salary_currency = st.selectbox(
                "Currency",
                currency_options,
                index=currency_index,
            )
    suggested_roles = []
    cv_roles = []
    cv_markets = []
    cv_industries = []
    try:
        cv_bytes_state = st.session_state.get("cv_bytes")
        if cv_bytes_state:
            from engines.cv_public import (
                infer_target_roles_from_cv,
                infer_markets_from_cv,
                infer_industries_from_cv,
            )

            groq_key = st.session_state.get("groq_key", "")
            cv_roles = infer_target_roles_from_cv(cv_bytes_state, groq_key)
            cv_markets = infer_markets_from_cv(cv_bytes_state)
            cv_industries = infer_industries_from_cv(cv_bytes_state)
    except Exception:
        cv_roles = []
        cv_markets = []
        cv_industries = []

    for r in cv_roles:
        if r and r not in suggested_roles:
            suggested_roles.append(r)

    saved_roles = existing_profile.get("target_roles", [])
    role_options = []
    for r in suggested_roles + saved_roles:
        if r and r not in role_options:
            role_options.append(r)
    default_roles = (
        [r for r in saved_roles if r in role_options]
        or suggested_roles
        or []
    )
    target_roles = st.multiselect(
        "Target Roles *",
        role_options,
        default=default_roles,
    )
    existing_extra_roles = [r for r in saved_roles if r not in default_roles]
    other_roles = st.text_input(
        "Other roles (comma-separated, optional)",
        value=", ".join(existing_extra_roles),
        key="other_target_roles",
    )
    markets_suggested = cv_markets
    saved_markets = existing_profile.get("target_markets", [])
    market_options = []
    for m in markets_suggested + saved_markets:
        if m and m not in market_options:
            market_options.append(m)
    default_markets = (
        [m for m in saved_markets if m in market_options]
        or markets_suggested
        or []
    )
    target_markets = st.multiselect(
        "Target Markets *",
        market_options,
        default=default_markets,
    )
    existing_extra_markets = [m for m in saved_markets if m not in default_markets]
    other_markets = st.text_input(
        "Other markets (comma-separated, optional)",
        value=", ".join(existing_extra_markets),
        key="other_target_markets",
    )
    cv_industries_local = cv_industries
    saved_industries = existing_profile.get("industries", [])
    industry_options = []
    for i in cv_industries_local + saved_industries:
        if i and i not in industry_options:
            industry_options.append(i)
    default_industries = (
        [i for i in saved_industries if i in industry_options]
        or cv_industries
        or []
    )
    industries = st.multiselect(
        "Preferred Industries",
        industry_options,
        default=default_industries,
    )
    existing_extra_industries = [i for i in saved_industries if i not in default_industries]
    other_industries = st.text_input(
        "Other industries (comma-separated, optional)",
        value=", ".join(existing_extra_industries),
        key="other_preferred_industries",
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
            extra_roles = [r.strip() for r in other_roles.split(",") if r.strip()]
            all_roles = target_roles + extra_roles
            if not all_roles:
                missing.append("Target Roles")
            extra_markets = [m.strip() for m in other_markets.split(",") if m.strip()]
            all_markets = target_markets + extra_markets
            if not all_markets:
                missing.append("Target Markets")
            if not missing:
                extra_industries = [
                    i.strip() for i in other_industries.split(",") if i.strip()
                ]
                all_industries = industries + extra_industries
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
                    "target_markets": all_markets,
                    "industries": all_industries,
                    "preferred_locations": preferred_locations,
                    "experience_markets": all_markets or ([location] if location else []),
                    "skills": [],
                }
                try:
                    from engines.auth import save_user_data

                    email_val = st.session_state.get("user_email", "")
                    if email_val:
                        save_user_data(
                            email_val, "profile", st.session_state.user_profile
                        )
                except Exception:
                    pass
                st.session_state.setup_step = 3
                st.rerun()
            else:
                st.warning("Please fill required fields (*): " + ", ".join(missing))

elif st.session_state.setup_step == 3:
    st.subheader("🔑 Step 3: API Keys")
    st.caption("Keys are not stored permanently — they stay in your browser session only.")
    existing_groq = st.session_state.get("groq_key", "")
    existing_serp = st.session_state.get("serpapi_key", "")
    existing_gmail = st.session_state.get("gmail_address", "")
    existing_gmail_pass = st.session_state.get("gmail_password", "")
    existing_gemini = st.session_state.get("gemini_key", "")
    if (not existing_groq or not existing_serp) and st.session_state.get("user_email", ""):
        try:
            from engines.auth import load_session_data

            email = st.session_state.get("user_email", "")
            keys, _, _, _ = load_session_data(email)
            if keys:
                if not existing_groq:
                    existing_groq = keys.get("groq", "")
                    st.session_state.groq_key = existing_groq
                if not existing_serp:
                    existing_serp = keys.get("serpapi", "")
                    st.session_state.serpapi_key = existing_serp
                if not existing_gmail:
                    existing_gmail = keys.get("gmail", "")
                    st.session_state.gmail_address = existing_gmail
                if not existing_gmail_pass:
                    existing_gmail_pass = keys.get("gmail_pass", "")
                    st.session_state.gmail_password = existing_gmail_pass
                if not existing_gemini:
                    existing_gemini = keys.get("gemini", "")
                    st.session_state.gemini_key = existing_gemini
        except Exception:
            pass
    st.markdown("**🤖 Groq API Key** (Required)")
    st.markdown(" `https://console.groq.com` ")
    st.caption(
        "Create a Groq account, go to API Keys in the console, generate a key starting "
        "with `gsk_` and paste it here."
    )
    groq_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        value=existing_groq,
    )
    st.markdown("**🔍 SerpAPI Key** (Required)")
    st.markdown(" `https://serpapi.com` ")
    st.caption(
        "Sign up on SerpAPI, open your dashboard, copy the API key from the top "
        "of the page and paste it here."
    )
    serpapi_key = st.text_input(
        "SerpAPI Key",
        type="password",
        placeholder="...",
        value=existing_serp,
    )
    st.markdown("**📧 Gmail** (Optional — for email applications)")
    st.markdown(" `https://support.google.com/accounts/answer/185833` ")
    st.caption(
        "Use a Gmail App Password, not your normal password. Turn on 2‑Step "
        "Verification in your Google Account, create an App Password for Mail, "
        "then paste the 16‑character password here."
    )
    gmail = st.text_input(
        "Gmail Address",
        placeholder="you@gmail.com",
        value=existing_gmail,
    )
    gmail_pass = st.text_input(
        "Gmail App Password",
        type="password",
        placeholder="xxxx xxxx xxxx xxxx",
        value=existing_gmail_pass,
    )
    st.markdown("**✨ Gemini API Key** (Optional — better CV tailoring)")
    st.markdown(" `https://aistudio.google.com` ")
    st.caption(
        "Create a key in Google AI Studio, copy the `AIza...` key from the API Keys "
        "page and paste it here."
    )
    gemini_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="AIza...",
        value=existing_gemini,
    )
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
            """1. Go to https://serpapi.com and create an account  
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
    c_edit, c_dash = st.columns(2)
    with c_edit:
        if st.button("✏️ Edit Setup (CV, Profile, API Keys)"):
            st.session_state.setup_step = 1
            st.rerun()
    with c_dash:
        if st.button("🚀 Go to Dashboard"):
            st.switch_page("pages/1_Home.py")
