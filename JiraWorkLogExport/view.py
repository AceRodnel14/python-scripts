import streamlit as st
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt
import json

# === Load config ===
with open("config.json") as f:
    config = json.load(f)

csv_file = config.get("csv_file", "generated_2025-05-01_2025-05-31.csv")

# === Load CSV ===
df = pd.read_csv(csv_file)
df["Date"] = pd.to_datetime(df["Date"])

# === Set Date Range ===
min_date = df["Date"].min()
max_date = df["Date"].max()

# === Initialize week navigation state ===
if "current_week_start" not in st.session_state:
    st.session_state.current_week_start = min_date - timedelta(days=min_date.weekday())

# === Navigation buttons ===
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("⬅️ Previous Week"):
        st.session_state.current_week_start -= timedelta(weeks=1)
with col2:
    if st.button("Next Week ➡️"):
        st.session_state.current_week_start += timedelta(weeks=1)

week_start = st.session_state.current_week_start
week_end = week_start + timedelta(days=6)

st.markdown(f"## 📆 Week: {week_start.date()} to {week_end.date()}")

# === Filter data for the selected week ===
week_df = df[(df["Date"] >= week_start) & (df["Date"] <= week_end)]

# === Pivot table: total hours per day of week (Monday to Sunday order) ===
pivot = (
    week_df.groupby(week_df["Date"].dt.strftime("%A"))["Hours"]
    .sum()
    .reindex(
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    )
    .fillna(0)
)

# === Bar chart of daily hours with day abbrev + date labels ===
st.markdown("### 📊 Bar Chart of Hours Logged This Week")

dates_in_week = [week_start + timedelta(days=i) for i in range(7)]
labels = [f"{date.strftime('%a')} {date.strftime('%m-%d')}" for date in dates_in_week]

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(labels, pivot.values, color="lightgreen")
ax.set_ylabel("Hours")
ax.set_xlabel("Day")
ax.set_title(f"Work Hours: {week_start.date()} to {week_end.date()}")
ax.set_ylim(0, max(pivot.values.max(), 8) + 2)
plt.xticks(rotation=45)

st.pyplot(fig)

# === Show the table ===
st.table(pivot.reset_index().rename(columns={"index": "Day", "Hours": "Total Hours"}))
