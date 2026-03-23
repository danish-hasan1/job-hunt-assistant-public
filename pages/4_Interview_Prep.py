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
                "company_brief": f"{company} is a leading organisation in their sector.",
                "key_themes": [
                    "Role expectations and success criteria",
                    "Technical and functional expertise",
                    "Stakeholder management and communication",
                ],
                "questions": [
                    {
                        "question": "Tell me about your most relevant experience for this role.",
                        "suggested_answer": "Start with a short overview of your background, then give one or two concrete examples with metrics that show impact.",
                    },
                    {
                        "question": "Describe a time you handled a difficult stakeholder or situation.",
                        "suggested_answer": "Use a simple situation–task–action–result structure and highlight how you stayed calm, listened, and moved things forward.",
                    },
                    {
                        "question": "What are your biggest strengths for this position?",
                        "suggested_answer": "Pick 2–3 strengths that match the job description and back each one with a short example.",
                    },
                    {
                        "question": "Tell me about a mistake you made and what you learned.",
                        "suggested_answer": "Choose a real but low-risk example, focus on what you changed afterwards and what you learned.",
                    },
                    {
                        "question": f"Why do you want to work at {company}?",
                        "suggested_answer": f"Connect your motivations to {company}'s mission, the team, and the responsibilities in this role.",
                    },
                ],
                "questions_to_ask": [
                    "What does success look like in the first 90 days?",
                    "How is the team structured and how does this role collaborate with others?",
                    "What are the biggest priorities for this role over the next 6–12 months?",
                ],
                "red_flags_to_address": [
                    "Any gaps between your experience and the job description",
                    "Any career breaks or short tenures that may raise questions",
                ],
            }
        else:
            from groq import Groq
            import json

            client = Groq(api_key=groq_key)
            prompt = f"""Create interview prep for {profile.get('name')} applying for {role} at {company}. 
 Profile: {profile.get('years_experience')} years experience, markets: {profile.get('experience_markets')}, skills: {profile.get('skills')}. 
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
