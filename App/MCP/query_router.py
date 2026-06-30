import re

from App.MCP.tools import *


def ask_database(query: str):

    q = query.lower()

    # =================================
    # PATIENT DETAILS
    # =================================

    code_match = re.search(
        r'pc\d+[a-z]?',
        query,
        re.IGNORECASE
    )

    if code_match:

        patient = get_patient_by_code(
            code_match.group()
        )

        if not patient:
            return "❌ Patient not found."

        patient = patient[0]

        return f"""
### 👤 Patient Information

| Field | Value |
|---------|---------|
| Patient ID | {patient['patient_id']} |
| Patient Code | {patient['patient_code']} |
| Patient Name | {patient['patient_name']} |
| Gender | {patient['gender']} |
| Age | {patient['age']} |
| Blood Group | {patient['blood_group']} |
| Diagnosis | {patient['diagnosis']} |
| Phone | {patient['phone']} |
| Emergency Contact | {patient['emergency_contact']} |
| City | {patient['city']} |
| Admission Date | {patient['admission_date']} |
| Discharge Date | {patient['discharge_date']} |
| Insurance Policy | {patient['insurance_policy_id']} |

📂 **Source Table:** patients
"""

    # =================================
    # LAB REPORTS
    # =================================

    if "lab" in q:

        name = q.replace(
            "show lab reports of",
            ""
        ).replace(
            "patient",
            ""
        ).strip()

        patient = get_patient_by_name(name)

        if not patient:
            return "❌ Patient not found."

        labs = get_lab_results(
            patient[0]["patient_id"]
        )

        if not labs:
            return "No lab reports found."

        response = "## 🧪 Lab Reports\n\n"

        for lab in labs[:10]:

            response += f"""
### {lab['test_name']}

• Lab ID: {lab['lab_id']}
• Result: {lab['result']}
• Report Date: {lab['report_date']}

---
"""

        response += "\n📂 **Source Table:** lab_results"

        return response

    # =================================
    # PRESCRIPTIONS
    # =================================

    if "prescription" in q:

        name = q.replace(
            "show prescriptions of",
            ""
        ).replace(
            "patient",
            ""
        ).strip()

        patient = get_patient_by_name(name)

        if not patient:
            return "❌ Patient not found."

        prescriptions = get_prescriptions(
            patient[0]["patient_id"]
        )

        if not prescriptions:
            return "No prescriptions found."

        response = "## 💊 Prescriptions\n\n"

        for p in prescriptions[:10]:

            response += f"""
### {p['medication_name']}

• Dosage: {p['dosage']}
• Date: {p['prescription_date']}

---
"""

        response += "\n📂 **Source Table:** prescriptions"

        return response

    # =================================
    # APPOINTMENTS
    # =================================

    if "appointment" in q:

        name = q.replace(
            "show appointments of",
            ""
        ).replace(
            "patient",
            ""
        ).strip()

        patient = get_patient_by_name(name)

        if not patient:
            return "❌ Patient not found."

        appointments = get_appointments(
            patient[0]["patient_id"]
        )

        if not appointments:
            return "No appointments found."

        response = "## 📅 Appointments\n\n"

        for app in appointments[:10]:

            response += f"""
### Appointment #{app['appointment_id']}

• Doctor ID: {app['doctor_id']}
• Date: {app['appointment_date']}
• Status: {app['status']}

---
"""

        response += "\n📂 **Source Table:** appointments"

        return response

    # =================================
    # BILLING
    # =================================

    if "billing" in q:

        name = q.replace(
            "show billing of",
            ""
        ).replace(
            "patient",
            ""
        ).strip()

        patient = get_patient_by_name(name)

        if not patient:
            return "❌ Patient not found."

        billing = get_billing(
            patient[0]["patient_id"]
        )

        if not billing:
            return "No billing records found."

        response = "## 💰 Billing Records\n\n"

        for bill in billing[:10]:

            response += f"""
### Bill #{bill['bill_id']}

• Amount: ₹{bill['amount']}
• Insurance: {bill['insurance_provider']}
• Status: {bill['payment_status']}

---
"""

        response += "\n📂 **Source Table:** billing"

        return response

    # =================================
    # COMPLETE HISTORY
    # =================================

    if "history" in q:

        name = q.replace(
            "give me history of",
            ""
        ).replace(
            "patient",
            ""
        ).strip()

        patient = get_patient_by_name(name)

        if not patient:
            return "❌ Patient not found."

        patient = patient[0]

        return f"""
## 🏥 Patient History

**Patient ID:** {patient['patient_id']}
**Patient Code:** {patient['patient_code']}
**Patient Name:** {patient['patient_name']}
**Diagnosis:** {patient['diagnosis']}
**Blood Group:** {patient['blood_group']}
**City:** {patient['city']}

📂 **Source Table:** patients
"""

    return "❌ No matching data found."