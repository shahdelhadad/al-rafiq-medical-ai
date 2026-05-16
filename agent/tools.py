# agent/tools.py
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from tools.db import (
    fetch_patient_data,
    fetch_doctor_data,
    fetch_prescriptions,
    fetch_appointments,
)
from tools.search import SearchTool

load_dotenv()
_backend_url = os.getenv("BACKEND_API_URL")


@tool
def search_web(query: str) -> str:
    """Search the internet for medical information, drug details, symptoms, or any topic
    not available in the internal database. Summarizes results in the user's language."""
    return SearchTool(query)


@tool
def get_patient_data(name: str) -> str:
    """Fetch a patient's record from the healthcare system by their name.
    Returns condition and personal information."""
    return fetch_patient_data(name, _backend_url)


@tool
def get_doctor_data(name: str) -> str:
    """Fetch a doctor's profile from the healthcare system by their name.
    Returns specialty and contact information."""
    return fetch_doctor_data(name, _backend_url)


@tool
def get_prescriptions(query: str) -> str:
    """Fetch prescription details for a patient name or medication name.
    Returns medication name and dosage instructions."""
    return fetch_prescriptions(query, _backend_url)


@tool
def get_appointments(query: str) -> str:
    """Fetch upcoming appointment information for a patient by their name.
    Returns appointment date and assigned doctor."""
    return fetch_appointments(query, _backend_url)


@tool
def generate_medical_summary(patient_name: str) -> str:
    """Combines a patient's conditions, prescriptions, and appointments into a single comprehensive AI-written medical summary report."""
    from langchain_groq import ChatGroq
    
    patient_info = fetch_patient_data(patient_name, _backend_url)
    prescriptions = fetch_prescriptions(patient_name, _backend_url)
    appointments = fetch_appointments(patient_name, _backend_url)
    
    # Use the 8B model for summarizing to save latency and cost
    llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-8b-instant", temperature=0)
    
    prompt = f"""
    You are a professional medical scribe. Given the following raw database records for patient '{patient_name}', 
    generate a cohesive, beautifully formatted medical summary report in Markdown. 
    Use clear headings, bullet points, and professional medical terminology.
    If any data is missing (e.g. no prescriptions), simply omit that section or state it clearly.
    
    Patient Data:
    {patient_info}
    
    Prescriptions:
    {prescriptions}
    
    Appointments:
    {appointments}
    """
    
    response = llm.invoke(prompt)
    return response.content


@tool
def check_symptoms_and_recommend_doctor(symptoms: str) -> str:
    """Analyzes a patient's symptoms, determines the required medical specialty, and recommends the appropriate doctor from our clinic database."""
    from langchain_groq import ChatGroq
    from tools.search import SearchTool
    
    # 1. Search web for the symptoms
    search_query = f"What medical specialty treats these symptoms: {symptoms}"
    web_results = SearchTool(search_query)
    
    # 2. Ask LLM to determine the specialty
    llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-8b-instant", temperature=0)
    specialty_prompt = f"Based on these search results:\n{web_results}\nWhat single medical specialty (e.g. Cardiology, Neurology, Pulmonology, Physiotherapy, Sports Medicine) treats symptoms '{symptoms}'? Reply with ONLY the specialty name."
    specialty = llm.invoke(specialty_prompt).content.strip()
    
    # 3. Query the DB for doctors in that specialty
    doctors = fetch_doctor_data(specialty, _backend_url)
    
    # 4. Synthesize recommendation
    return f"**Symptom Analysis:**\nBased on the symptoms '{symptoms}', the required specialty appears to be **{specialty}**.\n\n**Available Specialists at our Clinic:**\n{doctors}"


ALL_TOOLS = [
    search_web,
    get_patient_data,
    get_doctor_data,
    get_prescriptions,
    get_appointments,
    generate_medical_summary,
    check_symptoms_and_recommend_doctor,
]
