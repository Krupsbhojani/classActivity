# Analytical dashboard — helps ED managers discover patterns in wait times,
# crowding, and patient outcomes across time; not real-time ops, not exec KPIs.

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="ED Analytics", layout="wide")

@st.cache_data
def load():
    df = pd.read_csv("hospital_ed_data.csv", parse_dates=["date"])
    return df

df = load()

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🏥 ED Dashboard")
    st.caption("Hospital Emergency Department · 2023–2024")

    years = st.multiselect("Year", sorted(df["year"].unique()), default=sorted(df["year"].unique()))
    shifts = st.multiselect("Shift", df["shift"].unique(), default=list(df["shift"].unique()))
    metric = st.selectbox("Primary metric", ["avg_wait_min", "total_arrivals", "crowding_ratio", "patient_satisfaction"])

filtered = df[df["year"].isin(years) & df["shift"].isin(shifts)]

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("Emergency Department Analytics")
st.caption("For ED managers and analysts — answers: *when do we get overwhelmed, and does it affect outcomes?*")

# ── KPI row ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Avg Daily Arrivals", f"{filtered['total_arrivals'].mean():.0f}")
k2.metric("Avg Wait (min)", f"{filtered['avg_wait_min'].mean():.1f}")
k3.metric("Avg Satisfaction", f"{filtered['patient_satisfaction'].mean():.1f} / 10")
k4.metric("Left Without Seen", f"{filtered['left_without_seen'].sum():,}")

st.divider()

# ── Row 1 ──────────────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.subheader("Daily trend")
    daily = filtered.groupby("date")[metric].mean().reset_index()
    fig = px.line(daily, x="date", y=metric, color_discrete_sequence=["#4C9BE8"])
    fig.update_layout(margin=dict(t=10, b=10), height=300)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Avg wait by day of week")
    order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dow = filtered.groupby("day_of_week")["avg_wait_min"].mean().reindex(order).reset_index()
    fig2 = px.bar(dow, x="day_of_week", y="avg_wait_min",
                  color="avg_wait_min", color_continuous_scale="Reds")
    fig2.update_layout(margin=dict(t=10, b=10), height=300, coloraxis_showscale=False)
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2 ──────────────────────────────────────────────────────────────────────
c3, c4 = st.columns(2)

with c3:
    st.subheader("Crowding ratio vs. patient satisfaction")
    fig3 = px.scatter(filtered, x="crowding_ratio", y="patient_satisfaction",
                      color="shift", opacity=0.5, trendline="ols",
                      color_discrete_map={"Day":"#4C9BE8","Evening":"#F4A261","Night":"#6A0572"})
    fig3.update_layout(margin=dict(t=10, b=10), height=320)
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.subheader("Monthly triage breakdown")
    triage_cols = ["triage_critical","triage_urgent","triage_semi_urgent","triage_non_urgent"]
    monthly = filtered.groupby("month")[triage_cols].mean().reset_index()
    month_order = ["January","February","March","April","May","June",
                   "July","August","September","October","November","December"]
    monthly["month"] = pd.Categorical(monthly["month"], categories=month_order, ordered=True)
    monthly = monthly.sort_values("month")
    fig4 = go.Figure()
    colors = ["#E63946","#F4A261","#457B9D","#A8DADC"]
    for col, color in zip(triage_cols, colors):
        fig4.add_trace(go.Bar(name=col.replace("triage_","").title(), x=monthly["month"], y=monthly[col], marker_color=color))
    fig4.update_layout(barmode="stack", margin=dict(t=10, b=10), height=320, legend=dict(orientation="h"))
    st.plotly_chart(fig4, use_container_width=True)

# ── Anomaly callout ────────────────────────────────────────────────────────────
st.divider()
st.subheader("⚠️ Anomaly spotlight — March 2023 staffing shortage")
anomaly = df[(df["date"] >= "2023-03-05") & (df["date"] <= "2023-03-11")]
normal = df[(df["date"] >= "2023-03-12") & (df["date"] <= "2023-03-18")]
a1, a2, a3 = st.columns(3)
a1.metric("Arrivals (shortage week)", f"{anomaly['total_arrivals'].mean():.0f}",
          delta=f"+{anomaly['total_arrivals'].mean()-normal['total_arrivals'].mean():.0f} vs next week")
a2.metric("Avg Wait (shortage week)", f"{anomaly['avg_wait_min'].mean():.1f} min",
          delta=f"+{anomaly['avg_wait_min'].mean()-normal['avg_wait_min'].mean():.1f} min")
a3.metric("Satisfaction (shortage week)", f"{anomaly['patient_satisfaction'].mean():.1f}",
          delta=f"{anomaly['patient_satisfaction'].mean()-normal['patient_satisfaction'].mean():.1f}")
