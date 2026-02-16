import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Mock Centre Generator",
    layout="wide"
)

st.title("📊 Mock Centre Data Generator")

# =============================
# USER INPUTS
# =============================
col1, col2 = st.columns(2)

with col1:
    date_input = st.date_input(
        "Enter the base date to assign",
        format="YYYY-MM-DD"
    )

with col2:
    roll_length = st.number_input(
        "Enter the length of roll numbers",
        min_value=1,
        step=1,
        value=5
    )

shift_input = st.text_input(
    "Enter shifts separated by commas",
    placeholder="Training 1, Mock 1, Mock 2"
)

shifts = [s.strip() for s in shift_input.split(",") if s.strip()]

# =============================
# FILE UPLOAD
# =============================
uploaded_file = st.file_uploader(
    "Upload Mock Centre Excel File",
    type=["xlsx"]
)

# =============================
# OUTPUT FILE NAME
# =============================
output_name = st.text_input(
    "Enter output Excel file name",
    value="FinalMock_Updated.xlsx"
)

if not output_name.lower().endswith(".xlsx"):
    output_name += ".xlsx"

# =============================
# MAIN PROCESS
# =============================
if st.button("🚀 Generate Mock Data"):

    if uploaded_file is None:
        st.error("❌ Please upload the Mock Centre Excel file")
        st.stop()

    if not shifts:
        st.error("❌ Please enter at least one shift")
        st.stop()

    # Load uploaded Mock Centre file
    try:
        mock_df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"❌ Failed to read Excel file: {e}")
        st.stop()

    # Validate required columns
    required_columns = {
        "centre_code", "centre_name", "city", "device_allotted"
    }

    if not required_columns.issubset(mock_df.columns):
        st.error(
            "❌ Uploaded file must contain columns:\n"
            + ", ".join(required_columns)
        )
        st.stop()

    # =============================
    # DEMO DATA
    # =============================
    demo_names = [f"Demo Name{i}" for i in range(1, 6)]

    demo_roll_numbers = {
        name: str(i).zfill(roll_length)
        for i, name in enumerate(demo_names, start=1)
    }

    # =============================
    # GENERATE DATA
    # =============================
    new_rows = []
    base_date = datetime.combine(date_input, datetime.min.time())

    for i, shift in enumerate(shifts):
        shift_date = (base_date + timedelta(days=i)).strftime("%d %b'%y")

        for _, centre in mock_df.iterrows():
            for name in demo_names:
                new_rows.append({
                    "roll_no": demo_roll_numbers[name],
                    "name": name,
                    "centre_code": centre["centre_code"],
                    "centre_name": centre["centre_name"],
                    "city": centre["city"],
                    "device_allotted": centre["device_allotted"],
                    "date": shift_date,
                    "shift": shift
                })

    updated_df = pd.DataFrame(new_rows)

    # =============================
    # CREATE EXCEL IN MEMORY
    # =============================
    output_buffer = BytesIO()
    updated_df.to_excel(
        output_buffer,
        index=False,
        engine="openpyxl"
    )
    output_buffer.seek(0)

    # =============================
    # OUTPUT UI
    # =============================
    st.success("✅ Mock data generated successfully!")

    st.download_button(
        label="⬇️ Download Final Mock Excel",
        data=output_buffer,
        file_name=output_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.subheader("📌 Fixed Roll Numbers Assigned")
    st.table(pd.DataFrame(
        demo_roll_numbers.items(),
        columns=["Name", "Roll Number"]
    ))

    st.subheader("👀 Preview of Generated Data")
    st.dataframe(updated_df.head(50), use_container_width=True)
st.header("📊 Created by Ritik Chaudhary")
