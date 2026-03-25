import sqlite3
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")

if "setup_complete" not in st.session_state or not st.session_state.setup_complete:
    st.switch_page("pages/0_Setup.py")


st.set_page_config(
    page_title="🤝 Outreach - Job Hunt Assistant",
    page_icon="🤝",
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


def load_outreach_rows():
    try:
        conn = sqlite3.connect("data/jobs.db")
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS outreach (id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER, company TEXT, contact_name TEXT, contact_role TEXT, contact_url TEXT, message TEXT, status TEXT DEFAULT 'sent', date_sent TEXT)"
        )
        cur.execute(
            "SELECT id, job_id, company, contact_name, contact_role, contact_url, message, status, date_sent FROM outreach ORDER BY date_sent DESC, id DESC"
        )
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def update_outreach_status(row_id, new_status):
    try:
        conn = sqlite3.connect("data/jobs.db")
        conn.execute(
            "UPDATE outreach SET status = ?, date_sent = COALESCE(date_sent, ?) WHERE id = ?",
            (new_status, date.today().isoformat(), row_id),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


st.title("🤝 Outreach Tracker")
st.markdown("---")


rows = load_outreach_rows()

if not rows:
    st.info(
        "No outreach yet. Use the LinkedIn Outreach buttons on the 💼 Jobs page to contact people, and they will appear here."
    )
    st.stop()


df = pd.DataFrame(
    rows,
    columns=[
        "ID",
        "Job ID",
        "Company",
        "Contact",
        "Role",
        "Profile URL",
        "Message",
        "Status",
        "Date",
    ],
)


status_options = ["All", "sent", "accepted", "replied", "closed"]
status_filter = st.selectbox("Status", status_options, index=0)
company_filter = st.text_input("Company contains", "")
date_options = ["All time", "Last 7 days", "Last 30 days", "This month"]
date_filter = st.selectbox("Date range", date_options, index=0)

filtered_df = df.copy()
if status_filter != "All":
    filtered_df = filtered_df[filtered_df["Status"] == status_filter]
if company_filter:
    filtered_df = filtered_df[
        filtered_df["Company"].str.contains(company_filter, case=False, na=False)
    ]
if date_filter != "All time":
    today = date.today()
    if date_filter == "Last 7 days":
        start = today - timedelta(days=7)
    elif date_filter == "Last 30 days":
        start = today - timedelta(days=30)
    else:
        start = today.replace(day=1)
    def _parse_dt(val):
        try:
            return datetime.strptime(str(val), "%Y-%m-%d").date()
        except Exception:
            return None
    filtered_df = filtered_df[
        filtered_df["Date"].apply(
            lambda v: (_parse_dt(v) is not None and _parse_dt(v) >= start)
        )
    ]


total = len(filtered_df)
sent = len(filtered_df[filtered_df["Status"] == "sent"])
accepted = len(filtered_df[filtered_df["Status"] == "accepted"])
replied = len(filtered_df[filtered_df["Status"] == "replied"])


c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total contacts", total)
with c2:
    st.metric("Pending / Sent", sent)
with c3:
    st.metric("Accepted", accepted)
with c4:
    st.metric("Replied", replied)


st.markdown("---")


table_df = filtered_df[
    ["Company", "Contact", "Role", "Profile URL", "Status", "Date", "Job ID"]
].copy()
st.dataframe(table_df, use_container_width=True, hide_index=True)


st.markdown("---")
st.subheader("Update outreach status and review messages")


for _, row in filtered_df.iterrows():
    with st.expander(
        f"{row['Company']} — {row['Contact']} ({row['Role']}) [{row['Status']}]"
    ):
        st.markdown(f"**Profile:** {row['Profile URL']}")
        st.markdown(f"**Job ID:** {row['Job ID']}")
        st.markdown(f"**Date:** {row['Date'] or 'Not recorded'}")
        st.text_area(
            "Message sent",
            row["Message"],
            height=160,
            key=f"msg_view_{row['ID']}",
        )
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            if st.button(
                "Sent",
                key=f"set_sent_{row['ID']}",
            ):
                update_outreach_status(row["ID"], "sent")
                st.experimental_rerun()
        with col_b:
            if st.button(
                "Accepted",
                key=f"set_acc_{row['ID']}",
            ):
                update_outreach_status(row["ID"], "accepted")
                st.experimental_rerun()
        with col_c:
            if st.button(
                "Replied",
                key=f"set_rep_{row['ID']}",
            ):
                update_outreach_status(row["ID"], "replied")
                st.experimental_rerun()
        with col_d:
            if st.button(
                "No response / Closed",
                key=f"set_closed_{row['ID']}",
            ):
                update_outreach_status(row["ID"], "closed")
                st.experimental_rerun()

        if row["Job ID"]:
            if st.button(
                "👀 View job in Jobs page",
                key=f"view_job_{row['ID']}",
            ):
                try:
                    st.session_state["focus_job_id"] = int(row["Job ID"])
                except Exception:
                    st.session_state["focus_job_id"] = row["Job ID"]
                st.switch_page("pages/2_Jobs.py")
