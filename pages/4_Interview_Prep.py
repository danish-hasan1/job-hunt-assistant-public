import streamlit as st


if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

if "setup_complete" not in st.session_state or not st.session_state.setup_complete:
    st.switch_page("pages/0_Setup.py")


st.set_page_config(
    page_title="Interview Prep - Job Hunt Assistant",
    page_icon="🎤",
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


st.title("🎤 Interview Prep")
st.markdown("---")


applications = st.session_state.get("applications", [])
jobs = st.session_state.get("jobs", [])
all_roles = applications + [j for j in jobs if j.get("status") == "approved"]


if not all_roles:
    st.info("No applications yet. Apply to some jobs first!")
    st.stop()


options = {
    f"{a.get('role', a.get('title'))} at {a.get('company')}": a for a in all_roles
}
selected = st.selectbox("Select a role to prepare for:", list(options.keys()))
job = options[selected]


c1, c2 = st.columns(2)
with c1:
    st.markdown(f"**Company:** {job.get('company')}")
    st.markdown(f"**Role:** {job.get('role', job.get('title'))}")
with c2:
    st.markdown(f"**Location:** {job.get('location','')}")
    st.markdown(f"**Score:** {job.get('score',0)}/100")


st.markdown("---")


if st.button("🎯 Generate Interview Prep Pack"):
    with st.spinner("Generating your personalised prep pack..."):
        groq_key = st.session_state.get("groq_key")
        profile = st.session_state.get("user_profile", {})
        cv_text = st.session_state.get("cv_text", "")
        company = job.get("company")
        role = job.get("role", job.get("title"))
        jd = job.get("description", "")

        if groq_key == "test_mode":
            prep = {
                "company_brief": f"{company} is a leading organisation in their sector. They are known for innovation and strong talent practices.",
                "key_themes": [
                    "Leadership & Strategy",
                    "European Market Expertise",
                    "RPO Delivery",
                ],
                "questions": [
                    {
                        "question": "Tell me about your experience leading talent acquisition at scale.",
                        "suggested_answer": "In my current role I manage a €5M portfolio with 135 consultants across Europe, APAC and LATAM...",
                    },
                    {
                        "question": "How do you handle difficult stakeholders?",
                        "suggested_answer": "I use a structured QBR approach with clear KPIs and regular touchpoints...",
                    },
                    {
                        "question": "What's your approach to building talent pipelines?",
                        "suggested_answer": "I combine Boolean search, market mapping and proactive outreach...",
                    },
                    {
                        "question": "How do you measure recruitment success?",
                        "suggested_answer": "Key metrics I track include time-to-fill, offer-to-join ratio (93% in my current role) and SLA performance...",
                    },
                    {
                        "question": f"Why do you want to work at {company}?",
                        "suggested_answer": f"I've followed {company}'s growth and believe my European market expertise aligns perfectly...",
                    },
                ],
                "questions_to_ask": [
                    "What does success look like in the first 90 days?",
                    "How is the talent function structured across regions?",
                    "What are the biggest hiring challenges you're currently facing?",
                ],
                "red_flags_to_address": [
                    "Being based in India — address proactively with relocation commitment and European client experience"
                ],
            }
        else:
            from groq import Groq
            import json

            client = Groq(api_key=groq_key)
            prompt = f"""Create interview prep for {profile.get('name')} applying for {role} at {company}. 
 Profile: {profile.get('years_experience')} years, markets: {profile.get('experience_markets')}, achievements: 135 consultants, €5M portfolio, 100% retention. 
 JD: {jd[:800]} 
 Return JSON only: {{"company_brief":"...","key_themes":["..."],"questions":[{{"question":"...","suggested_answer":"..."}}],"questions_to_ask":["..."],"red_flags_to_address":["..."]}}"""
            r = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            text = r.choices[0].message.content.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            prep = json.loads(text.strip())

        st.session_state[f"prep_{selected}"] = prep
        st.success("✅ Prep pack ready!")


if st.session_state.get(f"prep_{selected}"):
    prep = st.session_state[f"prep_{selected}"]
    st.markdown("---")
    st.subheader("🏢 Company Brief")
    st.write(prep.get("company_brief", ""))
    st.subheader("🎯 Key Themes")
    for t in prep.get("key_themes", []):
        st.markdown(f"• {t}")
    st.markdown("---")
    st.subheader("❓ Interview Questions")
    for i, q in enumerate(prep.get("questions", [])):
        with st.expander(f"Q{i+1}: {q['question']}"):
            st.markdown("**💡 Suggested Answer:**")
            st.write(q["suggested_answer"])
    st.markdown("---")
    st.subheader("💬 Questions to Ask Them")
    for q in prep.get("questions_to_ask", []):
        st.markdown(f"• {q}")
    if prep.get("red_flags_to_address"):
        st.markdown("---")
        st.subheader("⚠️ Address These Proactively")
        for f in prep.get("red_flags_to_address", []):
            st.markdown(f"• {f}")
