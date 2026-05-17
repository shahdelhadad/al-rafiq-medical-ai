import os
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_groq import ChatGroq

load_dotenv()

serper_api_key = os.getenv("SERPER_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

if not serper_api_key:
    raise ValueError("مفتاح API الخاص بـ SERPER_API_KEY غير موجود في ملف .env")
if not groq_api_key:
    raise ValueError("مفتاح API الخاص بـ GROQ_API_KEY غير موجود في ملف .env")

search = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant", temperature=0)

def is_arabic(text: str) -> bool:
    """Check if the text contains Arabic characters."""
    return any("\u0600" <= char <= "\u06FF" for char in text)

def SearchTool(query: str) -> str:
    """
    Search the web and summarize results in Arabic if needed.
    """
    results = search.results(query)

    if not results or "organic" not in results:
        return "⚠️ لم أجد نتائج للبحث."

    snippets = [item.get("snippet", "") for item in results["organic"][:5]]
    combined_text = " ".join(snippets)

    if is_arabic(query):
        summary_prompt = f"""
        لخص لي هذه المعلومات بإيجاز وبأسلوب بسيط يفهمه كبار السن:
        {combined_text}
        """
        summary = llm.invoke(summary_prompt)
        return f"📖 ملخص البحث:\n{summary}"
    else:
        summary_prompt = f"Summarize this information in simple, clear English:\n{combined_text}"
        summary = llm.invoke(summary_prompt)
        return f"Summary:\n{summary}"
