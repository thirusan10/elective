import streamlit as st
import pandas as pd
import os
import re

st.set_page_config(page_title="Elective Selection", layout="centered")

# CSV file to store responses
CSV_FILE = "elective_responses.csv"
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

# Load or initialize data
if os.path.exists(CSV_FILE):
    try:
        df = pd.read_csv(CSV_FILE)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["Name", "PRN", "Email", "Elective 1", "Elective 2"])
else:
    df = pd.DataFrame(columns=["Name", "PRN", "Email", "Elective 1", "Elective 2"])

# Count how many students have chosen each elective
counts = df[["Elective 1", "Elective 2"]].stack().value_counts().to_dict()

# Filter electives with available seats
elective_display = []
elective_map = {}

for e in electives:
    count = counts.get(e, 0)
    remaining = MAX_CAPACITY - count
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
    prn_valid = re.fullmatch(r"\d{9,10}", prn.strip())  # adjust digit length as needed
    email_valid = re.fullmatch(r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+", email.strip())

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
        elif prn in df["PRN"].astype(str).values:
            st.warning("⚠️ This PRN has already submitted a response.")
        else:
            selected_actual = [elective_map[s] for s in selected_display]
            new_row = pd.DataFrame([[name.strip(), prn.strip(), email.strip(), selected_actual[0], selected_actual[1]]],
                                   columns=["Name", "PRN", "Email", "Elective 1", "Elective 2"])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)
            st.success("✅ Your electives have been recorded successfully!")
