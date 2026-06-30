import streamlit as st
import requests
import pandas as pd

# ==========================
# CONFIG
# ==========================

API_URL = "http://localhost:8000/ask"

st.set_page_config(
    page_title="MediAssistAI",
    page_icon="🏥",
    layout="wide"
)

# ==========================
# TITLE
# ==========================

st.title("🏥 MediAssistAI")
st.caption("Hospital Database Assistant using MCP + PostgreSQL")

# ==========================
# CHAT HISTORY
# ==========================

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================
# DISPLAY OLD CHATS
# ==========================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================
# RESPONSE FORMATTER
# ==========================

def format_response(data):

    output = ""

    # --------------------------------
    # Complete History
    # --------------------------------

    if isinstance(data, dict):

        if "patient_details" in data:

            patient = data["patient_details"][0]

            output += "## 👤 Patient Details\n\n"

            output += f"**Patient ID:** {patient.get('patient_id')}\n\n"
            output += f"**Patient Code:** {patient.get('patient_code')}\n\n"
            output += f"**Patient Name:** {patient.get('patient_name')}\n\n"
            output += f"**Gender:** {patient.get('gender')}\n\n"
            output += f"**Age:** {patient.get('age')}\n\n"
            output += f"**Blood Group:** {patient.get('blood_group')}\n\n"
            output += f"**Diagnosis:** {patient.get('diagnosis')}\n\n"
            output += f"**City:** {patient.get('city')}\n\n"
            output += f"**Phone:** {patient.get('phone')}\n\n"

            output += "---\n"

            output += f"### 📄 Prescriptions : {len(data['prescriptions'])}\n"
            output += f"### 🧪 Lab Reports : {len(data['lab_results'])}\n"
            output += f"### 🏥 Admissions : {len(data['admissions'])}\n"
            output += f"### 📅 Appointments : {len(data['appointments'])}\n"
            output += f"### 💰 Billing Records : {len(data['billing'])}\n"

            return output

        elif "message" in data:

            return data["message"]

    # --------------------------------
    # LIST DATA
    # --------------------------------

    if isinstance(data, list):

        if len(data) == 0:
            return "No records found."

        first = data[0]

        # Patient Search

        if "patient_name" in first:

            output += "## 👤 Patient Results\n\n"

            for row in data:

                output += (
                    f"**Patient ID:** {row['patient_id']}\n\n"
                    f"**Patient Code:** {row['patient_code']}\n\n"
                    f"**Patient Name:** {row['patient_name']}\n\n"
                    f"**Diagnosis:** {row['diagnosis']}\n\n"
                    f"---\n"
                )

            return output

        # Prescriptions

        if "medication_name" in first:

            output += "## 💊 Prescriptions\n\n"

            for row in data:

                output += (
                    f"**Medicine:** {row['medication_name']}\n\n"
                    f"**Dosage:** {row['dosage']}\n\n"
                    f"**Date:** {row['prescription_date']}\n\n"
                    f"---\n"
                )

            return output

        # Lab Reports

        if "test_name" in first:

            output += "## 🧪 Lab Results\n\n"

            for row in data:

                output += (
                    f"**Test:** {row['test_name']}\n\n"
                    f"**Result:** {row['result']}\n\n"
                    f"**Date:** {row['report_date']}\n\n"
                    f"---\n"
                )

            return output

        # Appointments

        if "appointment_date" in first:

            output += "## 📅 Appointments\n\n"

            for row in data:

                output += (
                    f"**Appointment ID:** {row['appointment_id']}\n\n"
                    f"**Doctor ID:** {row['doctor_id']}\n\n"
                    f"**Date:** {row['appointment_date']}\n\n"
                    f"**Status:** {row['status']}\n\n"
                    f"---\n"
                )

            return output

        # Admissions

        if "admission_reason" in first:

            output += "## 🏥 Admissions\n\n"

            for row in data:

                output += (
                    f"**Reason:** {row['admission_reason']}\n\n"
                    f"**Ward:** {row['ward']}\n\n"
                    f"**Admitted:** {row['admitted_on']}\n\n"
                    f"**Discharged:** {row['discharged_on']}\n\n"
                    f"---\n"
                )

            return output

        # Billing

        if "amount" in first:

            output += "## 💰 Billing\n\n"

            for row in data:

                output += (
                    f"**Bill ID:** {row['bill_id']}\n\n"
                    f"**Amount:** ₹{row['amount']}\n\n"
                    f"**Insurance:** {row['insurance_provider']}\n\n"
                    f"**Status:** {row['payment_status']}\n\n"
                    f"---\n"
                )

            return output

        return str(data)

    return str(data)

# ==========================
# USER INPUT
# ==========================

query = st.chat_input(
    "Ask about patients, history, prescriptions, labs..."
)

if query:

    # Show User Message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    with st.chat_message("user"):
        st.markdown(query)

    # Backend Call

    with st.chat_message("assistant"):

        with st.spinner("Searching database..."):

            try:

                response = requests.get(
                    API_URL,
                    params={
                        "query": query
                    },
                    timeout=60
                )

                result = response.json()

                formatted_response = format_response(
                    result
                )

                st.markdown(formatted_response)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": formatted_response
                    }
                )

            except Exception as e:

                error_msg = f"❌ Error: {str(e)}"

                st.error(error_msg)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_msg
                    }
                )

# ==========================
# SIDEBAR
# ==========================

with st.sidebar:

    st.header("Example Queries")

    st.info(
        """
Show patient PC00001Q

Give history of Patient 1 ML

Show prescriptions of Patient 1 ML

Show lab reports of Patient 1 ML

Show billing of Patient 1 ML

Show appointments of Patient 1 ML
"""
    )