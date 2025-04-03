import streamlit as st
import pandas as pd
import re
from collections import Counter

st.set_page_config(page_title="Elective Selection", layout="centered")

# --- USE YOUR SHARED GOOGLE SHEET (READ-ONLY MODE) ---
CSV_URL = "https://docs.google.com/spreadsheets/d/1DsHjWx6W9v7IbTYoBECKqymUeQOhK3QsCD3wEYnPA4w/export?format=csv"
MAX_CAPACITY = 60

# --- READ FROM GOOGLE SHEET ---
try:
    df = pd.read_csv(CSV_URL)
    if df.empty:
        st.warning("✅ Connected to Google Sheet, but no data found.")
    else:
        st.success("✅ Data successfully read from Google Sheet!")
        st.dataframe(df.head())  # Preview
except Exception as e:
    st.error("❌ Error reading data from the online sheet.")
    st.exception(e)
    st.stop()

# --- ELECTIVES LIST ---
electives = [
    "Theory of Constraints",
    "Essentials of Internet and Web Technologies",
    "Behavioral Finance",
    "Pricing",
    "Conflict and Negotiation",
    "Integrated Marketing Communication",
    "Indian Kaleidoscope-Culture and Communication",
    "Marketing of Financial Services",
    "International Marketing",
    "Financial Modeling",
    "Machine learning",
    "Mergers and Acquisitions",
    "Entrepreneurship",
    "Venture and Private Equity Funding",
    "Sustainable Finance and Responsible Investment"
]

# --- ELECTIVE COUNT FROM SHEET ---
count_list = df[["Elective 1", "Elective 2"]].stack().dropna().tolist()
counts = Counter(count_list)

# --- DISPLAY ELECTIVES WITH SEATS LEFT ---
elective_display = []
elective_map = {}

for e in electives:
    remaining = MAX_CAPACITY - counts.get(e, 0)
    if remaining > 0:
        label = f"{e} (Seats Left: {remaining}/60)"
        elective_display.append(label)
        elective_map[label] = e

# --- UI FORM ---
st.title("🎓 Elective Selection Form")
st.write("Please choose **exactly 2 electives**. Each elective has a cap of **60 students**.")

with st.form(key="elective_form"):
    name = st.text_input("Enter your full name:")
    prn = st.text_input("Enter your PRN number:")
    email = st.text_input("Enter your Email ID:")
    selected_display = st.multiselect("Select exactly 2 electives:", options=elective_display)
    submit = st.form_submit_button(label="Submit")

    # --- VALIDATION ---
    name_valid = re.fullmatch(r"[A-Za-z\s]+", name.strip())
    prn_valid = re.fullmatch(r"\d{9,10}", prn.strip())
    email_valid = re.fullmatch(r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+", email.strip())
    existing_prns = df["PRN"].astype(str).values

    if submit:
        if not name.strip() or not prn.strip() or not email.strip():
            st.error("❌ Please fill in all the fields.")
        elif not name_valid:
            st.error("❌ Name should contain only alphabets and spaces.")
        elif not prn_valid:
            st.error("❌ PRN should be a 9 or 10-digit number.")
        elif not email_valid:
            st.error("❌ Enter a valid email address.")
        elif len(selected_display) != 2:
            st.error("❌ Please select exactly 2 electives.")
        elif prn.strip() in existing_prns:
            st.warning("⚠️ This PRN has already submitted a response.")
        else:
            st.success("✅ Your electives have been recorded successfully!")
            st.info("ℹ️ However, this is a read-only version. Your submission has not been saved.")
            st.markdown("📩 Please contact the admin to enable write access to the sheet.")
