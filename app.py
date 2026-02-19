# Analytical dashboard for ED managers — simulates real-time patient intake
# and updates every 5 seconds with new synthetic records.

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import time

st.set_page_config(page_title="ED Dashboard", layout="wide")

def generate_record():
    now = datetime.now()
    arrivals = int(np.random.normal(120, 20))
    staff = max(8, int(np.random.normal(18, 3)))
    crowding = round(arrivals / (staff * 6.5), 2)
    wait = round(np.clip(20 + crowding * 45 + np.random.normal(0, 8), 8, 220), 1)
    satisfaction = round(np.clip(9.5 - wait / 26 + np.random.normal(0, 0.6), 1, 10), 1)
    return {
        "time": now.strftime("%H:%M:%S"),
        "timestamp": now,
        "total_arrivals": arrivals,
        "staff_on_duty": staff,
        "crowding_ratio": crowding,
        "avg_wait_min": wait,
        "patient_satisfaction": satisfaction,
        "left_without_seen": int(arrivals * np.clip(crowding * 0.06, 0.005, 0.15)),
        "admitted": int(arrivals * np.random.uniform(0.18, 0.30)),
        "shift": np.random.choice(["Day", "Evening", "Night"], p=[0.4, 0.35, 0.25]),
        "primary_diagnosis": np.random.choice(
            ["Respiratory","Cardiac","Trauma","Abdominal","Neurological","Psychiatric","Other"],
            p=[0.22, 0.15, 0.18, 0.14, 0.10, 0.08, 0.13]
        ),
    }

# init session state
if "records" not in st.session_state:
    st.session_state.records = [generate_record() for _ in range(30)]
if "running" not in st.session_state:
    st.session_state.running = True

# sidebar
st.sidebar.title("Controls")
refresh_rate = st.sidebar.slider("Refresh every (seconds)", 2, 10, 5)
max_records = st.sidebar.slider("Records to show", 20, 200, 60)

if st.sidebar.button("Pause" if st.session_state.running else "Resume"):
    st.session_state.running = not st.session_state.running

if st.sidebar.button("Reset data"):
    st.session_state.records = [generate_record() for _ in range(30)]

# add new record if running
if st.session_state.running:
    st.session_state.records.append(generate_record())

df = pd.DataFrame(st.session_state.records[-max_records:])

# header
st.title("Emergency Department — Live Monitor")
st.caption(f"Auto-refreshing every {refresh_rate}s  |  Last update: {df['time'].iloc[-1]}  |  {'Live' if st.session_state.running else 'Paused'}")

st.divider()

# KPIs from latest record
latest = df.iloc[-1]
prev = df.iloc[-2] if len(df) > 1 else latest

c1, c2, c3, c4 = st.columns(4)
c1.metric("Arrivals", int(latest["total_arrivals"]), int(latest["total_arrivals"] - prev["total_arrivals"]))
c2.metric("Avg Wait (min)", latest["avg_wait_min"], round(latest["avg_wait_min"] - prev["avg_wait_min"], 1))
c3.metric("Crowding Ratio", latest["crowding_ratio"], round(latest["crowding_ratio"] - prev["crowding_ratio"], 2))
c4.metric("Satisfaction", latest["patient_satisfaction"], round(latest["patient_satisfaction"] - prev["patient_satisfaction"], 1))

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Live Arrivals")
    fig = px.line(df, x="time", y="total_arrivals", color_discrete_sequence=["#4C9BE8"])
    fig.update_layout(height=300, margin=dict(t=10,b=10), xaxis=dict(tickangle=45))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Wait Time Trend")
    fig2 = px.line(df, x="time", y="avg_wait_min", color_discrete_sequence=["#E63946"])
    fig2.update_layout(height=300, margin=dict(t=10,b=10), xaxis=dict(tickangle=45))
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Crowding vs Satisfaction")
    fig3 = px.scatter(df, x="crowding_ratio", y="patient_satisfaction",
                      color="shift", opacity=0.6, trendline="ols")
    fig3.update_layout(height=320, margin=dict(t=10,b=10))
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Diagnosis Mix")
    diag = df["primary_diagnosis"].value_counts().reset_index()
    diag.columns = ["diagnosis", "count"]
    fig4 = px.pie(diag, names="diagnosis", values="count", hole=0.4)
    fig4.update_layout(height=320, margin=dict(t=10,b=10))
    st.plotly_chart(fig4, use_container_width=True)

# auto rerun
if st.session_state.running:
    time.sleep(refresh_rate)
    st.rerun()
