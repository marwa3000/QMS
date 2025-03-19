import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ✅ Load Google Cloud Credentials
google_creds = st.secrets["GOOGLE_CREDENTIALS"]
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(google_creds, scopes=scopes)
client = gspread.authorize(creds)

# ✅ Google Sheets IDs
SPREADSHEET_IDS = {
    "Complaints": st.secrets["GOOGLE_SHEETS_ID_COMPLAINTS"],
    "Deviation": st.secrets["GOOGLE_SHEETS_ID_DEVIATION"],
    "Change Control": st.secrets["GOOGLE_SHEETS_ID_CHANGE_CONTROL"]
}

# ✅ Column Headers
HEADERS = {
    "Complaints": ["Date Submitted", "ID", "Product Name", "Severity", "Contact Number", "Details", "Submitted By"],
    "Deviation": ["Date Submitted", "ID", "Department", "Deviation Type", "Details", "Reported By"],
    "Change Control": ["Date Submitted", "ID", "Change Type", "Justification", "Impact Analysis", "Requested By"]
}

# ✅ Load Google Sheets
sheets = {name: client.open_by_key(SPREADSHEET_IDS[name]).sheet1 for name in SPREADSHEET_IDS}

# ✅ Ensure Headers Exist in Google Sheets
def ensure_headers(sheet, headers):
    existing_data = sheet.get_all_values()
    if not existing_data or existing_data[0] != headers:
        sheet.insert_row(headers, 1)

for name in sheets:
    ensure_headers(sheets[name], HEADERS[name])

# ✅ Function to Generate Unique Record ID (Starts from 001 each month)
def generate_record_id(sheet, prefix):
    today = datetime.now()
    month = today.strftime("%m")
    year = today.strftime("%y")

    records = sheet.get_all_records()

    # Filter records only for the current month & year
    serial_numbers = [
        int(row["ID"].split("-")[-1]) for row in records 
        if "ID" in row and row["ID"].startswith(f"{prefix}-{month}{year}")
    ]

    # Start from 001 each month
    next_serial = max(serial_numbers, default=0) + 1
    return f"{prefix}-{month}{year}-{next_serial:03d}"

# ✅ Streamlit App UI
st.title("🔬 Pharmaceutical QMS (Quality Management System)")
tab1, tab2, tab3, admin_tab = st.tabs(["📋 Complaints", "❌ Deviation", "🔄 Change Control", "🔐 Admin View"])

# ✅ Complaints Section
with tab1:
    st.subheader("📋 Register a New Complaint")
    complaint_id = generate_record_id(sheets["Complaints"], "C")
    product = st.text_input("Product Name")
    severity = st.selectbox("Severity Level", ["High", "Medium", "Low"])
    contact_number = st.text_input("📞 Contact Number")
    details = st.text_area("Complaint Details")
    submitted_by = st.text_input("✍ Submitted By (Optional)")

    if st.button("Submit Complaint"):
        if product and details and contact_number:
            new_data = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), complaint_id, product, severity, contact_number, details, submitted_by or ""]
            sheets["Complaints"].append_row(new_data)
            st.success(f"✅ Complaint registered successfully with ID {complaint_id}!")
        else:
            st.error("❌ Please fill in all required fields!")

# ✅ Deviation Section
with tab2:
    st.subheader("❌ Register a New Deviation")
    deviation_id = generate_record_id(sheets["Deviation"], "D")
    department = st.text_input("Responsible Department")
    deviation_type = st.selectbox("Deviation Type", ["Minor", "Major", "Critical"])
    deviation_description = st.text_area("Deviation Details")
    reported_by = st.text_input("📛 Reported By")

    if st.button("Submit Deviation"):
        if department and deviation_description and reported_by:
            new_data = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), deviation_id, department, deviation_type, deviation_description, reported_by]
            sheets["Deviation"].append_row(new_data)
            st.success(f"✅ Deviation registered successfully with ID {deviation_id}!")
        else:
            st.error("❌ Please fill in all required fields!")

# ✅ Change Control Section
with tab3:
    st.subheader("🔄 Register a Change Request")
    change_id = generate_record_id(sheets["Change Control"], "CC")
    change_type = st.selectbox("Change Type", ["Equipment", "Process", "Document", "Other"])
    justification = st.text_area("Justification for Change")
    impact_analysis = st.text_area("Impact Analysis")
    requested_by = st.text_input("👤 Requested By")

    if st.button("Submit Change Request"):
        if change_type and justification and impact_analysis and requested_by:
            new_data = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), change_id, change_type, justification, impact_analysis, requested_by]
            sheets["Change Control"].append_row(new_data)
            st.success(f"✅ Change request registered successfully with ID {change_id}!")
        else:
            st.error("❌ Please fill in all required fields!")

# ✅ Admin View (Protected)
with admin_tab:
    st.subheader("🔐 Admin Panel - View All Records")
    admin_password = st.text_input("Enter Admin Password", type="password")

    if st.button("Access Admin Panel"):
        if admin_password == "admin123":
            st.success("✅ Access Granted! Viewing all records.")

            # Display Complaints
            st.subheader("📋 Complaints List")
            complaints_data = sheets["Complaints"].get_all_values()
            if len(complaints_data) > 1:
                st.table(complaints_data)
            else:
                st.info("No complaints registered yet.")

            # Display Deviations
            st.subheader("❌ Deviation List")
            deviation_data = sheets["Deviation"].get_all_values()
            if len(deviation_data) > 1:
                st.table(deviation_data)
            else:
                st.info("No deviations registered yet.")

            # Display Change Controls
            st.subheader("🔄 Change Control List")
            change_control_data = sheets["Change Control"].get_all_values()
            if len(change_control_data) > 1:
                st.table(change_control_data)
            else:
                st.info("No change control requests registered yet.")

        else:
            st.error("❌ Incorrect password! Access Denied.")
