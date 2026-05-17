import os
import sqlite3

DB_PATH = "clinic.db"

def _run_query(query: str, params: tuple = ()) -> list:
    """Helper to run a SQLite query and return dicts."""
    if not os.path.exists(DB_PATH):
        return [{"error": f"Database not found at {DB_PATH}. Run db_setup.py first."}]
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def _format_markdown(rows: list, entity_name: str) -> str:
    """Format a list of dictionary rows into a markdown table or fallback message."""
    if not rows:
        return f"No {entity_name} found."
    
    if "error" in rows[0]:
        return rows[0]["error"]
        
    headers = list(rows[0].keys())
    header_row = "| " + " | ".join(headers) + " |"
    divider_row = "|" + "|".join(["---"] * len(headers)) + "|"
    
    table_rows = []
    for row in rows:
        str_values = [str(row[h]) for h in headers]
        table_rows.append("| " + " | ".join(str_values) + " |")
        
    return f"**Results for {entity_name}:**\n" + "\n".join([header_row, divider_row] + table_rows)


def fetch_patient_data(query: str, backend_url=None) -> str:
    sql = "SELECT * FROM patients WHERE name LIKE ? OR condition LIKE ?"
    param = f"%{query}%"
    rows = _run_query(sql, (param, param))
    return _format_markdown(rows, "patients")

def fetch_doctor_data(query: str, backend_url=None) -> str:
    sql = "SELECT * FROM doctors WHERE name LIKE ? OR specialty LIKE ?"
    param = f"%{query}%"
    rows = _run_query(sql, (param, param))
    return _format_markdown(rows, "doctors")

def fetch_prescriptions(query: str, backend_url=None) -> str:
    sql = """
    SELECT pr.medication, pr.dosage, pr.instructions, p.name as patient_name
    FROM prescriptions pr
    JOIN patients p ON pr.patient_id = p.id
    WHERE p.name LIKE ? OR pr.medication LIKE ?
    """
    param = f"%{query}%"
    rows = _run_query(sql, (param, param))
    return _format_markdown(rows, "prescriptions")

def fetch_appointments(query: str, backend_url=None) -> str:
    sql = """
    SELECT a.appointment_date, a.status, p.name as patient_name, d.name as doctor_name
    FROM appointments a
    JOIN patients p ON a.patient_id = p.id
    JOIN doctors d ON a.doctor_id = d.id
    WHERE p.name LIKE ?
    """
    param = f"%{query}%"
    rows = _run_query(sql, (param,))
    return _format_markdown(rows, "appointments")
