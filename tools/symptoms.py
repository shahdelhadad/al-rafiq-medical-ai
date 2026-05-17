import os
from langchain_groq import ChatGroq
from tools.search import SearchTool
from tools.db import fetch_doctor_data

def evaluate_symptoms_and_recommend(symptoms: str, backend_url=None) -> str:
    """Analyzes a patient's symptoms, determines the required medical specialty, and recommends the appropriate doctor from our clinic database."""
    
    # 1. Search web for the symptoms
    search_query = f"What medical specialty treats these symptoms: {symptoms}"
    web_results = SearchTool(search_query)
    
    # 2. Ask LLM to determine the specialty
    llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-8b-instant", temperature=0)
    specialty_prompt = f"Based on these search results:\n{web_results}\nWhat single medical specialty (e.g. Cardiology, Neurology, Pulmonology, Physiotherapy, Sports Medicine) treats symptoms '{symptoms}'? Reply with ONLY the specialty name."
    specialty = llm.invoke(specialty_prompt).content.strip()
    
    # 3. Query the DB for doctors in that specialty
    doctors = fetch_doctor_data(specialty, backend_url)
    
    # 4. Synthesize recommendation
    return f"**Symptom Analysis:**\nBased on the symptoms '{symptoms}', the required specialty appears to be **{specialty}**.\n\n**Available Specialists at our Clinic:**\n{doctors}"
