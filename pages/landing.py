import streamlit as st


st.set_page_config(page_title="Job Hunt Assistant", page_icon="🎯", layout="wide")

st.markdown(
    """<style> 
[data-testid="stAppViewContainer"]{background:#0f0f23} 
[data-testid="stHeader"]{background:#0f0f23!important} 
[data-testid="stSidebar"]{display:none} 
h1,h2,h3,p,label,.stMarkdown{color:white!important} 
.stButton>button{background:#e94560!important;color:white!important;border:none;border-radius:8px;font-weight:bold;padding:12px 30px;font-size:16px} 
.feature-card{background:#16213e;border:1px solid #0f3460;border-radius:12px;padding:25px;margin:10px;text-align:center} 
.hero{text-align:center;padding:60px 20px} 
.tag{background:#e94560;color:white;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:bold} 
</style>""",
    unsafe_allow_html=True,
)

st.markdown(
    """ 
<div class="hero"> 
    <div class="tag">FREE FOREVER</div> 
    <br><br> 
    <h1 style="font-size:3.5em;font-weight:900;color:white">🎯 Job Hunt Assistant</h1> 
    <h3 style="color:#aaa;font-weight:300">Your personal AI-powered job search — finds jobs, tailors your CV,<br>and applies for you. Completely free.</h3> 
</div> 
""",
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🚀 Get Started — It's Free", use_container_width=True):
        st.switch_page("pages/login.py")

st.markdown("---")

st.markdown(
    "<h2 style='text-align:center;color:white'>Everything you need to land your next role</h2>",
    unsafe_allow_html=True,
)
st.markdown("")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        """<div class="feature-card"> 
<h2>🔍</h2> 
<h3 style="color:white">Smart Job Search</h3> 
<p style="color:#aaa">Searches Google Jobs, Indeed, Naukri and 100+ sites simultaneously. Filters by seniority, location and salary.</p> 
</div>""",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        """<div class="feature-card"> 
<h2>🧠</h2> 
<h3 style="color:white">AI Scoring</h3> 
<p style="color:#aaa">Every job scored against your profile 0-100. See instantly which roles are worth your time.</p> 
</div>""",
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        """<div class="feature-card"> 
<h2>📄</h2> 
<h3 style="color:white">Tailored CV</h3> 
<p style="color:#aaa">AI rewrites your CV summary for every job. Download a custom CV in seconds, ready to send.</p> 
</div>""",
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        """<div class="feature-card"> 
<h2>🎤</h2> 
<h3 style="color:white">Interview Prep</h3> 
<p style="color:#aaa">Get a personalised prep pack for every interview — questions, answers and company brief.</p> 
</div>""",
        unsafe_allow_html=True,
    )

st.markdown("---")

st.markdown(
    "<h2 style='text-align:center;color:white'>How it works</h2>",
    unsafe_allow_html=True,
)
st.markdown("")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        """<div class="feature-card"> 
<h2 style="color:#e94560">1</h2> 
<h3 style="color:white">Upload your CV</h3> 
<p style="color:#aaa">Upload your existing CV as a Word document.</p> 
</div>""",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        """<div class="feature-card"> 
<h2 style="color:#e94560">2</h2> 
<h3 style="color:white">Search smart</h3> 
<p style="color:#aaa">Search hundreds of sites at once for roles that match you.</p> 
</div>""",
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        """<div class="feature-card"> 
<h2 style="color:#e94560">3</h2> 
<h3 style="color:white">Tailor CV & letters</h3> 
<p style="color:#aaa">AI-tailored CV summary and cover letter for each application.</p> 
</div>""",
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        """<div class="feature-card"> 
<h2 style="color:#e94560">4</h2> 
<h3 style="color:white">Apply & track</h3> 
<p style="color:#aaa">Send applications via email and track every job in one place.</p> 
</div>""",
        unsafe_allow_html=True,
    )

