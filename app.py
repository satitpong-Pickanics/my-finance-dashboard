import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="ระบบบันทึกงบรายรับ-รายจ่าย ค.จ.", layout="wide")

st.title("📊 ระบบงบรายรับ-รายจ่าย (ค.จ. แสงชีวิต)")
st.subheader("ประจำเดือน เมษายน 2026") # ตามข้อมูลในเอกสาร [cite: 3, 5]

# --- ส่วนของการจัดการข้อมูล (จำลองฐานข้อมูล) ---
if 'data' not in st.session_state:
    # ข้อมูลเริ่มต้นจากเอกสารสรุป [cite: 8, 9, 11]
    initial_data = [
        {"วันที่": "2026-04-01", "รายการ": "เงินยกมาจากเดือนที่แล้ว", "ประเภท": "รายรับ", "หมวดหมู่": "เงินยกมา", "จำนวนเงิน": 147000.00},
        {"วันที่": "2026-04-05", "รายการ": "ถวายโอนจาก USA", "ประเภท": "รายรับ", "หมวดหมู่": "ถวาย", "จำนวนเงิน": 364155.85},
    ]
    st.session_state.data = pd.DataFrame(initial_data)

# --- ส่วนบันทึกข้อมูล (Sidebar) ---
st.sidebar.header("📝 บันทึกรายการใหม่")
with st.sidebar.form("input_form"):
    date = st.date_input("วันที่", datetime.now())
    desc = st.text_input("รายการโอน/จ่าย")
    t_type = st.selectbox("ประเภท", ["รายรับ", "รายจ่าย"])
    
    # หมวดหมู่ตามเอกสาร 
    if t_type == "รายรับ":
        cat = st.selectbox("หมวดหมู่", ["ถวาย", "ถวายโอนจาก USA", "เงินยกมา", "อื่นๆ"])
    else:
        cat = st.selectbox("หมวดหมู่", ["สนับสนุนผู้รับ EM", "อาหารและเครื่องดื่ม", "หนังสือใบปลิว", "นิทรรศการ/เครื่องเขียน", "ร่วมกิจกรรม", "โรงแรม", "อื่นๆ"])
        
    amount = st.number_input("จำนวนเงิน (บาท)", min_value=0.0, step=100.0)
    submit = st.form_submit_button("บันทึกข้อมูล")

    if submit:
        new_row = {"วันที่": str(date), "รายการ": desc, "ประเภท": t_type, "หมวดหมู่": cat, "จำนวนเงิน": amount}
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
        st.success("บันทึกสำเร็จ!")

# --- ส่วน Dashboard ---
df = st.session_state.data

# คำนวณยอด [cite: 11]
total_income = df[df['ประเภท'] == 'รายรับ']['จำนวนเงิน'].sum()
total_expense = df[df['ประเภท'] == 'รายจ่าย']['จำนวนเงิน'].sum()
balance = total_income - total_expense

col1, col2, col3 = st.columns(3)
col1.metric("ยอดรายรับสะสม", f"{total_income:,.2f} บาท")
col2.metric("ยอดรายจ่ายสะสม", f"{total_expense:,.2f} บาท", delta_color="inverse")
col3.metric("ยอดเงินคงเหลือ", f"{balance:,.2f} บาท")

st.divider()

# กราฟแสดงสัดส่วนรายจ่ายแยกตามหมวดหมู่ 
st.subheader("분석 - วิเคราะห์รายจ่ายแยกตามหมวดหมู่")
expense_df = df[df['ประเภท'] == 'รายจ่าย']
if not expense_df.empty:
    fig = px.pie(expense_df, values='จำนวนเงิน', names='หมวดหมู่', hole=0.4, title="สัดส่วนรายจ่าย")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("ยังไม่มีข้อมูลรายจ่ายเพื่อแสดงกราฟ")

# ตารางแสดงข้อมูลทั้งหมด
st.subheader("📋 รายละเอียดรายการทั้งหมด")
st.dataframe(df, use_container_width=True)

# ปุ่ม Download ข้อมูลเป็น CSV
csv = df.to_csv(index=False).encode('utf-8-sig')
st.download_button("📥 ดาวน์โหลดข้อมูลเป็นไฟล์ Excel (CSV)", csv, "finance_data.csv", "text/csv")
