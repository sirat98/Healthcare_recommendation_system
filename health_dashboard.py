# health_dashboard.py

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import date
from collections import Counter

# DB setup
def create_db():
    conn = sqlite3.connect("health.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS health_log (
            date TEXT,
            symptoms TEXT,
            medications TEXT,
            sleep_hours REAL,
            exercise_minutes REAL,
            food_notes TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_log(date, symptoms, medications, sleep, exercise, food):
    conn = sqlite3.connect("health.db")
    c = conn.cursor()
    c.execute("INSERT INTO health_log VALUES (?, ?, ?, ?, ?, ?)",
              (date, symptoms, medications, sleep, exercise, food))
    conn.commit()
    conn.close()

def fetch_logs():
    conn = sqlite3.connect("health.db")
    df = pd.read_sql_query("SELECT * FROM health_log", conn)
    conn.close()
    return df

# Streamlit UI
st.set_page_config(page_title="📊 Health Dashboard")
st.title("🧑‍⚕️ Personal Health Tracker")

create_db()

# Form to enter daily log
with st.form("health_form"):
    st.subheader("📅 Log Your Daily Health")
    log_date = st.date_input("Date", date.today())
    symptoms = st.text_input("Symptoms")
    meds = st.text_input("Medications")
    sleep = st.slider("Sleep Hours", 0.0, 12.0, 6.0, 0.5)
    exercise = st.slider("Exercise (minutes)", 0, 120, 30)
    food = st.text_area("Food Notes")

    if st.form_submit_button("Submit"):
        insert_log(str(log_date), symptoms, meds, sleep, exercise, food)
        st.success("Entry saved!")

# Show log history and analytics
st.markdown("### 📈 Health History")
df = fetch_logs()

if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    st.dataframe(df.sort_values("date", ascending=False))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 💤 Sleep Trend")
        st.plotly_chart(px.line(df, x="date", y="sleep_hours"))
    with col2:
        st.markdown("### 🏃‍♂️ Exercise Trend")
        st.plotly_chart(px.bar(df, x="date", y="exercise_minutes"))

    # Symptom frequency
    st.markdown("### 🔁 Symptom Frequency")
    all_symptoms = ",".join(df["symptoms"].fillna("")).split(",")
    symptom_counts = Counter([s.strip().lower() for s in all_symptoms if s.strip()])
    if symptom_counts:
        freq_df = pd.DataFrame(symptom_counts.items(), columns=["Symptom", "Count"])
        st.plotly_chart(px.bar(freq_df.sort_values("Count", ascending=False), x="Symptom", y="Count"))
else:
    st.info("No health records found yet.")
