# tools/db.py
import os
import requests

# Dummy data
dummy_patients = [
    {"id": 1, "name": "Ahmed Ali", "condition": "Back pain"},
    {"id": 2, "name": "Sara Hassan", "condition": "Knee injury"}
]

dummy_doctors = [
    {"id": 101, "name": "Dr. Omar Khaled", "specialty": "Physiotherapy"},
    {"id": 102, "name": "Dr. Mariam Youssef", "specialty": "Sports Medicine"}
]

dummy_prescriptions = [
    {"patient_id": 1, "medication": "Painkillers", "dosage": "2/day"},
    {"patient_id": 2, "medication": "Anti-inflammatory", "dosage": "1/day"}
]

dummy_appointments = [
    {"patient_id": 1, "doctor_id": 101, "date": "2025-08-10"},
    {"patient_id": 2, "doctor_id": 102, "date": "2025-08-12"}
]

def _fallback_message(results, label):
    if not results:
        return f"No {label} found."
    return "\n".join([str(item) for item in results])

def fetch_patient_data(query, backend_url=None):
    if backend_url:
        try:
            resp = requests.get(f"{backend_url}/patients", params={"q": query})
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return f"Error fetching patient data from backend: {e}"
    # Dummy mode
    results = [p for p in dummy_patients if query.lower() in p["name"].lower()]
    return _fallback_message(results, "patients")

def fetch_doctor_data(query, backend_url=None):
    if backend_url:
        try:
            resp = requests.get(f"{backend_url}/doctors", params={"q": query})
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return f"Error fetching doctor data from backend: {e}"
    results = [d for d in dummy_doctors if query.lower() in d["name"].lower()]
    return _fallback_message(results, "doctors")

def fetch_prescriptions(query, backend_url=None):
    if backend_url:
        try:
            resp = requests.get(f"{backend_url}/prescriptions", params={"q": query})
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return f"Error fetching prescriptions from backend: {e}"
    results = [p for p in dummy_prescriptions if query.lower() in p["medication"].lower()]
    return _fallback_message(results, "prescriptions")

def fetch_appointments(query, backend_url=None):
    if backend_url:
        try:
            resp = requests.get(f"{backend_url}/appointments", params={"q": query})
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return f"Error fetching appointments from backend: {e}"
    results = [a for a in dummy_appointments if query.lower() in str(a["patient_id"])]
    return _fallback_message(results, "appointments")
