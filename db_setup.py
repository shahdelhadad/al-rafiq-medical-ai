import sqlite3
import os

DB_PATH = "clinic.db"

def init_db():
    # Remove old DB if it exists to ensure fresh generation
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Tables
    cursor.executescript('''
    CREATE TABLE patients (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        condition TEXT,
        contact TEXT
    );

    CREATE TABLE doctors (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        specialty TEXT,
        contact TEXT
    );

    CREATE TABLE prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        medication TEXT,
        dosage TEXT,
        instructions TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    );

    CREATE TABLE appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        appointment_date TEXT,
        status TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id),
        FOREIGN KEY(doctor_id) REFERENCES doctors(id)
    );
    ''')

    # Seed Data - Patients
    patients = [
        (1, "Ahmed Ali", 45, "Male", "Chronic Back Pain", "0501234567"),
        (2, "Sara Hassan", 32, "Female", "Knee Injury (ACL tear)", "0509876543"),
        (3, "Mahmoud Youssef", 55, "Male", "Hypertension & Diabetes", "0554443333"),
        (4, "Fatima Zahra", 28, "Female", "Migraines", "0522221111"),
        (5, "John Smith", 40, "Male", "Asthma", "0567778888")
    ]
    cursor.executemany('INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?)', patients)

    # Seed Data - Doctors
    doctors = [
        (101, "Dr. Omar Khaled", "Physiotherapy", "omar.khaled@clinic.com"),
        (102, "Dr. Mariam Youssef", "Sports Medicine", "mariam.y@clinic.com"),
        (103, "Dr. Tarek Ibrahim", "Cardiology", "tarek.i@clinic.com"),
        (104, "Dr. Layla Mahmoud", "Neurology", "layla.m@clinic.com"),
        (105, "Dr. Sarah Jensen", "Pulmonology", "sarah.j@clinic.com")
    ]
    cursor.executemany('INSERT INTO doctors VALUES (?, ?, ?, ?)', doctors)

    # Seed Data - Prescriptions
    prescriptions = [
        (1, "Ibuprofen 400mg", "1 pill twice a day", "Take after meals to avoid stomach upset"),
        (1, "Muscle Relaxant", "1 pill before bed", "May cause drowsiness"),
        (2, "Naproxen 500mg", "1 pill every 12 hours", "Take with food"),
        (3, "Lisinopril 10mg", "1 pill daily in the morning", "Monitor blood pressure regularly"),
        (3, "Metformin 500mg", "1 pill twice a day", "Take with meals"),
        (4, "Sumatriptan 50mg", "1 pill at onset of migraine", "Do not exceed 2 pills in 24 hours"),
        (5, "Albuterol Inhaler", "2 puffs every 4-6 hours", "Use as needed for shortness of breath")
    ]
    cursor.executemany('INSERT INTO prescriptions (patient_id, medication, dosage, instructions) VALUES (?, ?, ?, ?)', prescriptions)

    # Seed Data - Appointments
    appointments = [
        (1, 101, "2025-08-10 10:00:00", "Confirmed"),
        (2, 102, "2025-08-12 14:30:00", "Confirmed"),
        (3, 103, "2025-08-15 09:15:00", "Pending"),
        (4, 104, "2025-08-20 11:00:00", "Confirmed"),
        (5, 105, "2025-08-25 16:45:00", "Cancelled")
    ]
    cursor.executemany('INSERT INTO appointments (patient_id, doctor_id, appointment_date, status) VALUES (?, ?, ?, ?)', appointments)

    conn.commit()
    conn.close()
    print("✅ Successfully generated and seeded clinic.db")

if __name__ == "__main__":
    init_db()
