# Analytical dashboard for ED managers to explore wait times, crowding, and outcomes.

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ED Dashboard", layout="wide")

df = pd.read_csv("hospital_ed_data.csv", parse_dates=["date"])

st.sidebar.title("Filters")
year = st.sidebar.multiselect("Year", df["year"].unique(), default=list(df["year"].unique()))
shift = st.sidebar.multiselect("Shift", df["shift"].unique(), default=list(df["shift"].unique()))

data = df[df["year"].isin(year) & df["shift"].isin(shift)]

st.title("Emergency Department Analytics")
st.caption("Tracks crowding, wait times, and patient outcomes for ED managers.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Avg Arrivals/Day", f"{data['total_arrivals'].mean():.0f}")
c2.metric("Avg Wait (min)", f"{data['avg_wait_min'].mean():.1f}")
c3.metric("Avg Satisfaction", f"{data['patient_satisfaction'].mean():.1f}/10")
c4.metric("Left Without Seen", f"{data['left_without_seen'].sum():,}")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Daily Arrivals")
    daily = data.groupby("date")["total_arrivals"].mean().reset_index()
    st.plotly_chart(px.line(daily, x="date", y="total_arrivals"), use_container_width=True)

with col2:
    st.subheader("Avg Wait by Day of Week")
    order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dow = data.groupby("day_of_week")["avg_wait_min"].mean().reindex(order).reset_index()
    st.plotly_chart(px.bar(dow, x="day_of_week", y="avg_wait_min", color="avg_wait_min",
                           color_continuous_scale="Reds"), use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Crowding vs Satisfaction")
    st.plotly_chart(px.scatter(data, x="crowding_ratio", y="patient_satisfaction",
                               color="shift", opacity=0.5, trendline="ols"), use_container_width=True)

with col4:
    st.subheader("Monthly Avg Wait")
    months = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]
    monthly = data.groupby("month")["avg_wait_min"].mean().reindex(months).reset_index()
    st.plotly_chart(px.bar(monthly, x="month", y="avg_wait_min", color="avg_wait_min",
                           color_continuous_scale="Blues"), use_container_width=True)
