from App.MCP.connector import DBConnector


def run_query(query, params=None):

    conn = DBConnector.get_connection()
    cur = conn.cursor()

    cur.execute(query, params or ())

    columns = [desc[0] for desc in cur.description]

    rows = cur.fetchall()

    result = []

    for row in rows:
        result.append(dict(zip(columns, row)))

    cur.close()
    conn.close()

    return result


# ==========================
# PATIENTS
# ==========================

def get_patient_by_id(patient_id):

    result = run_query("""
        SELECT *
        FROM patients
        WHERE patient_id = %s
    """, (patient_id,))

    return result


def get_patient_by_code(patient_code):

    return run_query("""
        SELECT *
        FROM patients
        WHERE patient_code = %s
    """, (patient_code,))
    

def get_patient_by_name(name):

    return run_query("""
        SELECT *
        FROM patients
        WHERE LOWER(patient_name)
        LIKE LOWER(%s)
    """, (f"%{name}%",))


# ==========================
# PRESCRIPTIONS
# ==========================

def get_prescriptions(patient_id):

    return run_query("""
        SELECT *
        FROM prescriptions
        WHERE patient_id=%s
        ORDER BY prescription_date DESC
    """, (patient_id,))


# ==========================
# LAB RESULTS
# ==========================

def get_lab_results(patient_id):

    return run_query("""
        SELECT *
        FROM lab_results
        WHERE patient_id=%s
        ORDER BY report_date DESC
    """, (patient_id,))


# ==========================
# APPOINTMENTS
# ==========================

def get_appointments(patient_id):

    return run_query("""
        SELECT *
        FROM appointments
        WHERE patient_id=%s
        ORDER BY appointment_date DESC
    """, (patient_id,))


# ==========================
# ADMISSIONS
# ==========================

def get_admissions(patient_id):

    return run_query("""
        SELECT *
        FROM admissions
        WHERE patient_id=%s
        ORDER BY admitted_on DESC
    """, (patient_id,))


# ==========================
# BILLING
# ==========================

def get_billing(patient_id):

    return run_query("""
        SELECT *
        FROM billing
        WHERE patient_id=%s
    """, (patient_id,))


# ==========================
# INSURANCE
# ==========================

def get_insurance(policy_id):

    return run_query("""
        SELECT *
        FROM insurance_policies
        WHERE policy_id=%s
    """, (policy_id,))


# ==========================
# DOCTORS
# ==========================

def get_doctors():

    return run_query("""
        SELECT *
        FROM doctors
    """)


# ==========================
# DEPARTMENTS
# ==========================

def get_departments():

    return run_query("""
        SELECT *
        FROM departments
    """)


# ==========================
# BRANCHES
# ==========================

def get_branches():

    return run_query("""
        SELECT *
        FROM hospital_branches
    """)


# ==========================
# COMPLETE HISTORY
# ==========================

def get_complete_history(patient_id):

    patient = get_patient_by_id(patient_id)

    return {
        "patient_details": patient,
        "prescriptions": get_prescriptions(patient_id),
        "lab_results": get_lab_results(patient_id),
        "appointments": get_appointments(patient_id),
        "admissions": get_admissions(patient_id),
        "billing": get_billing(patient_id)
    }