import os
from dotenv import load_dotenv
from langchain_core.tools import tool

from tools.db import fetch_patient_data, fetch_doctor_data, fetch_prescriptions, fetch_appointments
from tools.search import SearchTool
from tools.summary import create_medical_summary
from tools.symptoms import evaluate_symptoms_and_recommend
from tools.fda import search_openfda_drug_reactions
from tools.pubmed import search_pubmed

load_dotenv()
_backend_url = os.getenv("BACKEND_API_URL")

@tool
def search_web(query: str) -> str:
    """Search the internet for general medical information, symptoms, or any topic
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
    """Combines a patient's conditions, prescriptions, and appointments into a single comprehensive AI-written medical summary report, and generates a downloadable PDF."""
    return create_medical_summary(patient_name, _backend_url)

@tool
def check_symptoms_and_recommend_doctor(symptoms: str) -> str:
    """Analyzes a patient's symptoms, determines the required medical specialty, and recommends the appropriate doctor from our clinic database."""
    return evaluate_symptoms_and_recommend(symptoms, _backend_url)

@tool
def search_fda_adverse_events(drug_name: str) -> str:
    """Queries the OpenFDA database (a massive U.S. government medical API) to find the most common adverse reactions and side effects reported for a specific drug."""
    return search_openfda_drug_reactions(drug_name)

@tool
def search_medical_journals(query: str) -> str:
    """Searches the NCBI PubMed database for official, peer-reviewed medical research articles. Use this for highly technical or academic medical queries."""
    return search_pubmed(query)

ALL_TOOLS = [
    search_web,
    get_patient_data,
    get_doctor_data,
    get_prescriptions,
    get_appointments,
    generate_medical_summary,
    check_symptoms_and_recommend_doctor,
    search_fda_adverse_events,
    search_medical_journals
]
