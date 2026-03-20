import streamlit as st
import pandas as pd
from datetime import datetime
import json


st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")


st.markdown(
    """<style>
[data-testid="stAppViewContainer"]{background:#0f0f23}
[data-testid="stHeader"]{background:#0f0f23!important}
h1,h2,h3,p,label{color:white!important}
.metric-card{background:#16213e;border:1px solid #0f3460;border-radius:10px;padding:20px;text-align:center}
.metric-value{font-size:2.5em;font-weight:bold;color:#e94560}
.metric-label{font-size:0.9em;color:#aaa;margin-top:5px}
.stButton>button{background:#e94560!important;color:white!important;border:none;border-radius:8px;font-weight:bold}
</style>""",
    unsafe_allow_html=True,
)


if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False


if not st.session_state.admin_auth:
    st.title("🔐 Admin Access")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if pwd == "danish@admin2026":
            st.session_state.admin_auth = True
            st.rerun()
        else:
            st.error("Wrong password")
    st.stop()


from engines.tracker import get_all_users, get_all_events, get_event_counts


st.title("📊 Job Hunt Assistant — Admin Dashboard")
st.caption(f"Last refreshed: {datetime.now().strftime('%d %b %Y %H:%M')}")


if st.button("🔄 Refresh"):
    st.rerun()


st.markdown("---")


users = get_all_users()
events = get_all_events()
event_counts = get_event_counts()


c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{len(users)}</div><div class="metric-label">👥 Total Users</div></div>',
        unsafe_allow_html=True,
    )
with c2:
    completed = len([u for u in users if u.get("setup_completed")])
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{completed}</div><div class="metric-label">✅ Setup Complete</div></div>',
        unsafe_allow_html=True,
    )
with c3:
    searches = event_counts.get("job_search", 0)
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{searches}</div><div class="metric-label">🔍 Jobs Searched</div></div>',
        unsafe_allow_html=True,
    )
with c4:
    cvs = event_counts.get("cv_generated", 0)
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{cvs}</div><div class="metric-label">📄 CVs Generated</div></div>',
        unsafe_allow_html=True,
    )
with c5:
    dropoff = len(users) - completed
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{dropoff}</div><div class="metric-label">⚠️ Drop-offs</div></div>',
        unsafe_allow_html=True,
    )


st.markdown("---")


tab1, tab2, tab3, tab4 = st.tabs(["👥 Users", "📈 Events", "🌍 Markets", "🎁 Referrals"])


with tab1:
    st.subheader(f"All Users ({len(users)})")
    if users:
        df_users = pd.DataFrame(users)[
            ["name", "email", "location", "years_experience", "setup_completed", "created_at"]
        ]
        df_users.columns = ["Name", "Email", "Location", "Experience", "Setup Done", "Joined"]
        st.dataframe(df_users, use_container_width=True, hide_index=True)
    else:
        st.info("No users yet")


with tab2:
    st.subheader("Feature Usage")
    if event_counts:
        df_events = pd.DataFrame(list(event_counts.items()), columns=["Feature", "Count"])
        df_events = df_events.sort_values("Count", ascending=False)
        st.bar_chart(df_events.set_index("Feature"))
        st.dataframe(df_events, use_container_width=True, hide_index=True)
    else:
        st.info("No events yet")

    st.subheader("Recent Activity")
    if events:
        df_recent = pd.DataFrame(events[:20])[["user_email", "event_type", "created_at"]]
        df_recent.columns = ["User", "Action", "Time"]
        st.dataframe(df_recent, use_container_width=True, hide_index=True)


with tab3:
    st.subheader("Target Markets")
    if users:
        all_markets = []
        for u in users:
            try:
                markets = json.loads(u.get("target_markets", "[]"))
                all_markets.extend(markets)
            except Exception:
                pass
        if all_markets:
            market_counts = {}
            for m in all_markets:
                market_counts[m] = market_counts.get(m, 0) + 1
            df_markets = pd.DataFrame(list(market_counts.items()), columns=["Market", "Users"])
            df_markets = df_markets.sort_values("Users", ascending=False)
            st.bar_chart(df_markets.set_index("Market"))

        st.subheader("Target Roles")
        all_roles = []
        for u in users:
            try:
                roles = json.loads(u.get("target_roles", "[]"))
                all_roles.extend(roles)
            except Exception:
                pass
        if all_roles:
            role_counts = {}
            for r in all_roles:
                role_counts[r] = role_counts.get(r, 0) + 1
            df_roles = pd.DataFrame(list(role_counts.items()), columns=["Role", "Users"])
            df_roles = df_roles.sort_values("Users", ascending=False)
            st.dataframe(df_roles, use_container_width=True, hide_index=True)


with tab4:
    st.subheader("Referral Leaderboard")
    from engines.referral import get_referral_leaderboard

    leaderboard = get_referral_leaderboard()
    if leaderboard:
        df = pd.DataFrame(leaderboard)[["name", "email", "referrals"]]
        df.columns = ["Name", "Email", "Referrals"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No referrals yet")
