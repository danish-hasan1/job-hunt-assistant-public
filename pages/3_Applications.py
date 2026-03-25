import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime


if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

if "setup_complete" not in st.session_state or not st.session_state.setup_complete:
    st.switch_page("pages/0_Setup.py")


st.set_page_config(
    page_title="📋 Applications - Job Hunt Assistant",
    page_icon="📋",
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


st.title("📋 Applications Tracker")
st.markdown("---")


applications = st.session_state.get("applications", [])


if not applications:
    st.info("No applications yet. Go to 💼 Jobs, approve a job and click 'Mark Applied'.")
    st.stop()


st.markdown("**Filters**")
fc1, fc2, fc3, fc4 = st.columns(4)
with fc1:
    status_filter = st.selectbox(
        "Status",
        ["All", "applied", "interview", "offer", "rejected"],
        index=0,
        key="apps_status_filter",
    )
with fc2:
    priority_filter = st.selectbox(
        "Priority",
        ["All", "High", "Medium", "Low"],
        index=0,
        key="apps_priority_filter",
    )
with fc3:
    date_filter = st.selectbox(
        "Date range",
        ["All time", "Last 7 days", "Last 30 days", "This month"],
        index=0,
        key="apps_date_filter",
    )
with fc4:
    follow_filter = st.selectbox(
        "Follow-up",
        ["All", "Due today", "Overdue", "Upcoming", "No follow-up"],
        index=0,
        key="apps_follow_filter",
    )


filtered_apps = list(applications)


if status_filter != "All":
    filtered_apps = [a for a in filtered_apps if a.get("status") == status_filter]


if priority_filter != "All":
    filtered_apps = [
        a for a in filtered_apps if a.get("priority", "Medium") == priority_filter
    ]


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except Exception:
        return None


if date_filter != "All time":
    today = date.today()
    if date_filter == "Last 7 days":
        start = today - timedelta(days=7)
    elif date_filter == "Last 30 days":
        start = today - timedelta(days=30)
    else:
        start = today.replace(day=1)
    filtered_apps = [
        a
        for a in filtered_apps
        if _parse_date(a.get("date_applied")) is not None
        and _parse_date(a.get("date_applied")) >= start
    ]


if follow_filter != "All":
    today = date.today()
    if follow_filter == "Due today":
        filtered_apps = [
            a
            for a in filtered_apps
            if _parse_date(a.get("follow_up_date")) == today
        ]
    elif follow_filter == "Overdue":
        filtered_apps = [
            a
            for a in filtered_apps
            if _parse_date(a.get("follow_up_date")) is not None
            and _parse_date(a.get("follow_up_date")) < today
        ]
    elif follow_filter == "Upcoming":
        filtered_apps = [
            a
            for a in filtered_apps
            if _parse_date(a.get("follow_up_date")) is not None
            and _parse_date(a.get("follow_up_date")) > today
        ]
    elif follow_filter == "No follow-up":
        filtered_apps = [
            a
            for a in filtered_apps
            if _parse_date(a.get("follow_up_date")) is None
        ]


c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Applied", len(filtered_apps))
with c2:
    interviews = len([a for a in filtered_apps if a.get("status") == "interview"])
    st.metric("Interviews", interviews)
with c3:
    offers = len([a for a in filtered_apps if a.get("status") == "offer"])
    st.metric("Offers", offers)
with c4:
    today = date.today()
    due_today = len(
        [
            a
            for a in filtered_apps
            if _parse_date(a.get("follow_up_date")) == today
        ]
    )
    overdue = len(
        [
            a
            for a in filtered_apps
            if _parse_date(a.get("follow_up_date")) is not None
            and _parse_date(a.get("follow_up_date")) < today
        ]
    )
    st.metric("Follow-ups (due / overdue)", f"{due_today} / {overdue}")


st.markdown("---")


df = pd.DataFrame(filtered_apps)
cols = [
    "company",
    "role",
    "location",
    "track",
    "status",
    "date_applied",
    "score",
]
if "priority" in df.columns:
    cols.append("priority")
if "follow_up_date" in df.columns:
    cols.append("follow_up_date")
df = df[cols]
col_labels = [
    "Company",
    "Role",
    "Location",
    "Track",
    "Status",
    "Date Applied",
    "Score",
]
if "priority" in df.columns:
    col_labels.append("Priority")
if "follow_up_date" in df.columns:
    col_labels.append("Follow-up Date")
df.columns = col_labels
st.dataframe(df, use_container_width=True, hide_index=True)


st.markdown("---")


st.subheader("📝 Update Status")
for app in filtered_apps:
    with st.expander(
        f"{'✅' if app['status']=='applied' else '🎤' if app['status']=='interview' else '🎉'} {app['role']} at {app['company']}"
    ):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Applied:** {app['date_applied']}")
            st.markdown(f"**Location:** {app['location']}")
            st.markdown(f"**Score:** {app['score']}/100")
        with c2:
            track_value = app.get("track")
            if track_value == "A":
                track_label = "🌍 Cross-border (Track A)"
            elif track_value == "B":
                track_label = "🏙 Local / Regional (Track B)"
            else:
                track_label = "Track not set"
            st.markdown(f"**Track:** {track_label}")
            st.markdown(f"**Status:** {app['status'].upper()}")
        if app.get("cv_summary"):
            st.markdown(f"**CV Summary used:** {app['cv_summary'][:200]}...")
        if app.get("priority"):
            st.markdown(f"**Priority:** {app.get('priority')}")
        if app.get("notes"):
            st.markdown("**Notes:**")
            st.write(app.get("notes"))
        fu_raw = app.get("follow_up_date", "")
        fu_date = _parse_date(fu_raw)
        if fu_date:
            today = date.today()
            if fu_date < today:
                days = (today - fu_date).days
                fu_label = f"Overdue by {days} day{'s' if days != 1 else ''}"
            elif fu_date == today:
                fu_label = "Due today"
            else:
                days = (fu_date - today).days
                fu_label = f"In {days} day{'s' if days != 1 else ''}"
            st.markdown(f"**Follow-up:** {fu_date.isoformat()} — {fu_label}")
        else:
            st.markdown("**Follow-up:** Not set")
        fu_col1, fu_col2 = st.columns(2)
        with fu_col1:
            default_fu = fu_date or date.today()
            new_fu = st.date_input(
                "Follow-up date (optional)",
                value=default_fu,
                key=f"fu_date_{app['id']}",
            )
            if st.button("💾 Save follow-up", key=f"save_fu_{app['id']}"):
                app["follow_up_date"] = new_fu.isoformat()
                try:
                    from engines.auth import save_user_data

                    email = st.session_state.get("user_email", "")
                    if email:
                        save_user_data(
                            email,
                            "applications",
                            st.session_state.get("applications", []),
                        )
                except Exception:
                    pass
                st.success("Follow-up saved")
                st.rerun()
        with fu_col2:
            if st.button("🧹 Clear follow-up", key=f"clear_fu_{app['id']}"):
                app["follow_up_date"] = ""
                try:
                    from engines.auth import save_user_data

                    email = st.session_state.get("user_email", "")
                    if email:
                        save_user_data(
                            email,
                            "applications",
                            st.session_state.get("applications", []),
                        )
                except Exception:
                    pass
                st.success("Follow-up cleared")
                st.rerun()
        ca, cb, cc = st.columns(3)
        with ca:
            if st.button("🎤 Interview Scheduled", key=f"int_{app['id']}"):
                app["status"] = "interview"
                try:
                    from engines.auth import save_user_data

                    email = st.session_state.get("user_email", "")
                    if email:
                        save_user_data(
                            email,
                            "applications",
                            st.session_state.get("applications", []),
                        )
                except Exception:
                    pass
                st.rerun()
        with cb:
            if st.button("🎉 Offer Received", key=f"off_{app['id']}"):
                app["status"] = "offer"
                try:
                    from engines.auth import save_user_data

                    email = st.session_state.get("user_email", "")
                    if email:
                        save_user_data(
                            email,
                            "applications",
                            st.session_state.get("applications", []),
                        )
                except Exception:
                    pass
                st.rerun()
        with cc:
            if st.button("❌ Rejected", key=f"rej_{app['id']}"):
                app["status"] = "rejected"
                try:
                    from engines.auth import save_user_data

                    email = st.session_state.get("user_email", "")
                    if email:
                        save_user_data(
                            email,
                            "applications",
                            st.session_state.get("applications", []),
                        )
                except Exception:
                    pass
                st.rerun()
