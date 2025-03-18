import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ✅ تحميل بيانات Google Cloud من secrets.toml
google_creds = st.secrets["GOOGLE_CREDENTIALS"]
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(google_creds, scopes=scopes)
client = gspread.authorize(creds)

# ✅ تحميل معرف Google Sheets لكل قسم
SPREADSHEET_IDS = {
    "Complaints": st.secrets["GOOGLE_SHEETS_ID_COMPLAINTS"],
    "Deviation": st.secrets["GOOGLE_SHEETS_ID_DEVIATION"],
    "Change Control": st.secrets["GOOGLE_SHEETS_ID_CHANGE_CONTROL"]
}

# ✅ تحميل البيانات لكل قسم
sheets = {name: client.open_by_key(SPREADSHEET_IDS[name]).sheet1 for name in SPREADSHEET_IDS}

# ✅ إنشاء واجهة التطبيق مع تبويبات
st.title("🔬 نظام إدارة الجودة الدوائية (Pharmaceutical QMS)")

# ✅ إنشاء تبويبات (`Complaints`, `Deviation`, `Change Control`)
tab1, tab2, tab3 = st.tabs(["📋 Complaints", "❌ Deviation", "🔄 Change Control"])

# ✅ توليد رقم تلقائي لكل نوع من التقارير
def generate_record_id(prefix):
    today = datetime.now()
    month = today.strftime("%m")
    year = today.strftime("%y")
    serial = today.strftime("%H%M%S")
    return f"{prefix}{month}{year}-{serial}"

# ✅ نموذج إدخال بيانات الشكاوى (`Complaints`)
with tab1:
    st.subheader("📋 تسجيل شكوى جديدة")
    complaint_id = generate_record_id("C-")
    product = st.text_input("اسم المنتج")
    severity = st.selectbox("مستوى الخطورة", ["High", "Medium", "Low"])
    contact_number = st.text_input("📞 رقم التواصل")
    details = st.text_area("تفاصيل الشكوى")
    submitted_by = st.text_input("✍ اسم المقدم (اختياري)")

    if st.button("إرسال الشكوى"):
        if product and details and contact_number:
            new_data = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), complaint_id, product, severity, contact_number, details, submitted_by or ""]
            sheets["Complaints"].append_row(new_data)
            st.success(f"✅ تم تسجيل الشكوى بنجاح برقم {complaint_id}!")
        else:
            st.error("❌ يرجى ملء جميع الحقول الإلزامية!")

# ✅ نموذج إدخال بيانات الانحرافات (`Deviation`)
with tab2:
    st.subheader("❌ تسجيل انحراف جديد")
    deviation_id = generate_record_id("D-")
    department = st.text_input("القسم المسؤول")
    deviation_type = st.selectbox("نوع الانحراف", ["Minor", "Major", "Critical"])
    deviation_description = st.text_area("تفاصيل الانحراف")
    reported_by = st.text_input("📛 اسم المقدم")

    if st.button("إرسال الانحراف"):
        if department and deviation_description and reported_by:
            new_data = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), deviation_id, department, deviation_type, deviation_description, reported_by]
            sheets["Deviation"].append_row(new_data)
            st.success(f"✅ تم تسجيل الانحراف بنجاح برقم {deviation_id}!")
        else:
            st.error("❌ يرجى ملء جميع الحقول الإلزامية!")

# ✅ نموذج إدخال بيانات تغيير التحكم (`Change Control`)
with tab3:
    st.subheader("🔄 تسجيل طلب تغيير")
    change_id = generate_record_id("CC-")
    change_type = st.selectbox("نوع التغيير", ["Equipment", "Process", "Document", "Other"])
    justification = st.text_area("مبررات التغيير")
    impact_analysis = st.text_area("تحليل الأثر")
    requested_by = st.text_input("👤 اسم المقدم")

    if st.button("إرسال طلب التغيير"):
        if change_type and justification and impact_analysis and requested_by:
            new_data = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), change_id, change_type, justification, impact_analysis, requested_by]
            sheets["Change Control"].append_row(new_data)
            st.success(f"✅ تم تسجيل طلب التغيير بنجاح برقم {change_id}!")
        else:
            st.error("❌ يرجى ملء جميع الحقول الإلزامية!")
 
