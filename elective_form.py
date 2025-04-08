import streamlit as st
import re
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------- Streamlit Setup -------------------
st.set_page_config(page_title="Elective Selection Form", layout="centered")
st.title("🎓 Elective Selection Form")
st.write("Please choose exactly 2 electives. Each elective has a cap of 60 students.")

# ------------------- Google Sheets Setup -------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Student_Responses").sheet1  # Replace with your actual sheet name

# ------------------- Elective Configuration -------------------
MAX_CAPACITY = 60
elective_remaining_seats = {
    "Theory of Constraints": 37,
    "International Marketing": 19,
    "Financial Modeling": 5,
    "Entrepreneurship": 28,
    "Venture and Private Equity Funding": 44,
    "Mergers and Acquisitions": 25
}

# ------------------- Read Data from Sheet -------------------
records = sheet.get_all_records()
df = pd.DataFrame(records)

# ------------------- Ensure Required Columns Exist -------------------
required_columns = ["Elective 1", "Elective 2", "PRN"]
for col in required_columns:
    if col not in df.columns:
        df[col] = ""  # Add missing column if not present

# ------------------- Count Current Elective Selections -------------------
counts_from_submissions = df[["Elective 1", "Elective 2"]].stack().value_counts().to_dict()

# ------------------- Prepare Display Electives -------------------
elective_display = []
elective_map = {}

for elective, total in elective_remaining_seats.items():
    used = counts_from_submissions.get(elective, 0)
    remaining = total - used
    if remaining > 0:
        label = f"{elective} (Seats Left: {remaining}/{MAX_CAPACITY})"
        elective_display.append(label)
        elective_map[label] = elective

# ------------------- Form UI -------------------
with st.form("elective_form"):
    name = st.text_input("Full Name *")
    prn = st.text_input("PRN Number *")
    email = st.text_input("Email ID *")
    selected_display = st.multiselect("Select exactly 2 electives:", options=elective_display)
    submit = st.form_submit_button("Submit")

    # ------------------- Validations -------------------
    name_valid = re.fullmatch(r"[A-Za-z\s]+", name.strip())
    prn_valid = re.fullmatch(r"\d{9,10}", prn.strip())
    email_valid = re.fullmatch(r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+", email.strip())

    if submit:
        if not name.strip() or not prn.strip() or not email.strip():
            st.error("❌ Please fill in all the required fields.")
        elif not name_valid:
            st.error("❌ Name should contain only alphabets and spaces.")
        elif not prn_valid:
            st.error("❌ PRN should be a 9 or 10-digit number.")
        elif not email_valid:
            st.error("❌ Please enter a valid email address.")
        elif len(selected_display) != 2:
            st.error("❌ Please select exactly 2 electives.")
        elif prn.strip() in df["PRN"].astype(str).values:
            st.warning("⚠️ This PRN has already submitted a response.")
        else:
            selected_actual = [elective_map[s] for s in selected_display]

            # Final overbooking check
            latest_counts = df[["Elective 1", "Elective 2"]].stack().value_counts().to_dict()
            overbooked = False
            for elective in selected_actual:
                if latest_counts.get(elective, 0) >= elective_remaining_seats[elective]:
                    st.error(f"❌ '{elective}' is now full. Please refresh and choose another elective.")
                    overbooked = True
                    break

            if not overbooked:
                sheet.append_row([
                    name.strip(),
                    prn.strip(),
                    email.strip(),
                    selected_actual[0],
                    selected_actual[1]
                ])
                st.success("✅ Your response has been recorded successfully!")
