import streamlit as st
import pandas as pd
import re
from collections import Counter

st.set_page_config(page_title="Elective Selection", layout="centered")

# Read from public Google Sheet (read-only CSV)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSYZSMYUGqFLiPNW8q4pkUnqDMAln0GcMw0JOQEyr2Dl9-wdfBOIr_twyR5GEMSUir1GqeeHRnHgGUo/pub?output=csv"
try:
    df = pd.read_csv(CSV_URL)
except Exception as e:
    st.error("Error reading data from the online sheet.")
    st.stop()

MAX_CAPACITY = 60

# List of electives
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

# Count how many students have chosen each elective
count_list = df[["Elective 1", "Elective 2"]].stack().dropna().tolist()
counts = Counter(count_list)

# Filter electives with available seats
elective_display = []
elective_map = {}

for e in electives:
    remaining = MAX_CAPACITY - counts.get(e, 0)
    if remaining > 0:
        label = f"{e} (Seats Left: {remaining}/60)"
        elective_display.append(label)
        elective_map[label] = e

# Streamlit Form UI
st.title("🎓 Elective Selection Form")
st.write("Please choose **exactly 2 electives**. Each elective has a cap of **60 students**.")

with st.form(key="elective_form"):
    name = st.text_input("Enter your full name:")
    prn = st.text_input("Enter your PRN number:")
    email = st.text_input("Enter your Email ID:")
    selected_display = st.multiselect("Select exactly 2 electives:", options=elective_display)
    submit = st.form_submit_button(label="Submit")

    # Regex for validations
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
            st.info("However, since this sheet is read-only, your submission is not being stored.")
            st.write("📩 Please contact the admin to enable full submission functionality.")
