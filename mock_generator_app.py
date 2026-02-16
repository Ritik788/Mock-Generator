import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Mock Centre Generator", layout="wide")

st.title("📊 Mock Centre Data Generator (Streamlit)")

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
# FILE PATHS
# =============================

mock_centre_file = r"C:\Users\ritik.chaudhary\Desktop\Mock Centre python.xlsx"
desktop_path = r"C:\Users\ritik.chaudhary\Desktop"

output_name = st.text_input(
    "Enter output Excel file name",
    value="FinalMock_Updated.xlsx"
)

if not output_name.lower().endswith(".xlsx"):
    output_name += ".xlsx"

final_mock_file = os.path.join(desktop_path, output_name)

# =============================
# MAIN PROCESS
# =============================

if st.button("🚀 Generate Mock Data"):

    if not shifts:
        st.error("❌ Please enter at least one shift")
        st.stop()

    if not os.path.exists(mock_centre_file):
        st.error(f"❌ Mock Centre file not found:\n{mock_centre_file}")
        st.stop()

    # Load Mock Centre
    mock_df = pd.read_excel(mock_centre_file)

    # Load existing FinalMock if exists
    if os.path.exists(final_mock_file):
        final_df = pd.read_excel(final_mock_file)
        st.info("ℹ️ Existing FinalMock file found. Data will be appended.")
    else:
        st.warning("⚠️ FinalMock file not found. A new one will be created.")
        final_df = pd.DataFrame(columns=[
            "roll_no", "name", "centre_code", "centre_name",
            "city", "device_allotted", "date", "shift"
        ])

    # Demo Names
    demo_names = [f"Demo Name{i}" for i in range(1, 6)]

    # Fixed Roll Numbers
    demo_roll_numbers = {
        name: str(i).zfill(roll_length)
        for i, name in enumerate(demo_names, start=1)
    }

    # Generate Records
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

    new_entries_df = pd.DataFrame(new_rows)
    updated_df = pd.concat([final_df, new_entries_df], ignore_index=True)

    updated_df.to_excel(final_mock_file, index=False)

    # =============================
    # OUTPUT
    # =============================

    st.success("✅ File generated successfully!")
    st.write("📁 **Saved at:**", final_mock_file)

    st.subheader("📌 Fixed Roll Numbers Assigned")
    roll_df = pd.DataFrame(
        list(demo_roll_numbers.items()),
        columns=["Name", "Roll Number"]
    )
    st.table(roll_df)

    st.subheader("👀 Preview of Generated Data")
    st.dataframe(updated_df.tail(20), use_container_width=True)
