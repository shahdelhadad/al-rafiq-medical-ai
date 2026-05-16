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


ALL_TOOLS = [
    search_web,
    get_patient_data,
    get_doctor_data,
    get_prescriptions,
    get_appointments,
]
