import os
import uuid
from fpdf import FPDF
from langchain_groq import ChatGroq
from tools.db import fetch_patient_data, fetch_prescriptions, fetch_appointments

class PDFReport(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Medical Summary Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(content: str, patient_name: str) -> str:
    pdf = PDFReport()
    pdf.add_page()
    
    
    pdf.set_font("helvetica", size=11)
    
    cleaned_content = content.replace('**', '').replace('*', '-')
    
    cleaned_content = cleaned_content.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 8, cleaned_content)
    
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/summary_{patient_name.replace(' ', '_')}_{uuid.uuid4().hex[:6]}.pdf"
    pdf.output(filename)
    return filename

def create_medical_summary(patient_name: str, backend_url=None) -> str:
    """Combines a patient's conditions, prescriptions, and appointments into a single comprehensive AI-written medical summary report, and generates a downloadable PDF."""
    patient_info = fetch_patient_data(patient_name, backend_url)
    prescriptions = fetch_prescriptions(patient_name, backend_url)
    appointments = fetch_appointments(patient_name, backend_url)
    
    llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-8b-instant", temperature=0)
    
    prompt = f"""
    You are a professional medical scribe. Given the following raw database records for patient '{patient_name}', 
    generate a cohesive medical summary report.
    Use clear headings, bullet points, and professional medical terminology. Do not use complex markdown. Please write in English.
    
    Patient Data:
    {patient_info}
    
    Prescriptions:
    {prescriptions}
    
    Appointments:
    {appointments}
    """
    
    content = llm.invoke(prompt).content
    
    pdf_path = generate_pdf(content, patient_name)
    
    return f"[PDF_GENERATED: {pdf_path}]\n\n" + content
