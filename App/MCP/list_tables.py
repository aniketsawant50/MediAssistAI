from App.MCP.connector import DBConnector

try:
    conn = DBConnector.get_connection()
    cur = conn.cursor()

    # Fetch only 5 rows from doctors table
    cur.execute("""
        SELECT * FROM  Prescriptions
                LIMIT 5
       
    """)

    rows = cur.fetchall()

    print("\n👨‍⚕️ Doctors Table (First 5 Rows)\n")
    print("-" * 50)

    for row in rows:
        print(row)

    cur.close()
    conn.close()

except Exception as e:
    print("Error:", e)