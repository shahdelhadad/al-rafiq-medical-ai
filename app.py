import os
import re
import uuid
import sqlite3
import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from agent import build_graph, ALL_TOOLS

st.set_page_config(
    page_title="الرفيق الطبي | Medical AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

*, body { font-family: 'Outfit', sans-serif !important; }

.stApp { 
    background: linear-gradient(145deg, #020617 0%, #0f172a 100%); 
    color: #f8fafc;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.45) !important;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* Header card */
.hero {
    background: rgba(30, 41, 59, 0.3);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 32px 32px;
    margin-bottom: 28px;
    text-align: center;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
}
.hero h1 {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #38bdf8, #818cf8, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 10px 0;
    letter-spacing: -0.02em;
}
.hero p { color: #94a3b8; font-size: 1rem; margin: 0; font-weight: 300; }

/* Chat inputs and blocks */
[data-testid="stChatInput"] {
    background: rgba(30, 41, 59, 0.6) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(10px);
}

/* Buttons */
.stButton>button {
    border-radius: 12px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
    border-color: #38bdf8 !important;
    color: #38bdf8 !important;
}

/* Tool badge */
.tool-badge {
    display: inline-block;
    background: rgba(14, 165, 233, 0.1);
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.2);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
    margin: 2px 3px;
    backdrop-filter: blur(4px);
    transition: all 0.2s;
}
.tool-badge:hover {
    background: rgba(14, 165, 233, 0.2);
    transform: translateY(-1px);
}

/* Status pill */
.status-online {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(16, 185, 129, 0.1);
    color: #34d399;
    border: 1px solid rgba(52, 211, 153, 0.2);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.1);
}
.dot { width: 8px; height: 8px; background: #34d399;
        border-radius: 50%; display: inline-block;
        box-shadow: 0 0 8px #34d399;
        animation: blink 2.5s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.4} }

/* Section label */
.section-label {
    color: #64748b;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: .1em;
    text-transform: uppercase;
    margin: 24px 0 12px 0;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

TOOL_LABELS = {
    "search_web":       "🔍 Web Search",
    "get_patient_data": "👤 Patient Lookup",
    "get_doctor_data":  "👨‍⚕️ Doctor Lookup",
    "get_prescriptions":"💊 Prescriptions",
    "get_appointments": "📅 Appointments",
    "generate_medical_summary": "📝 Medical Summary",
    "check_symptoms_and_recommend_doctor": "🩺 Symptom Checker",
    "search_fda_adverse_events": "🏛️ OpenFDA API",
    "search_medical_journals": "📚 PubMed API",
}

def init_state():
    if "conn" not in st.session_state:
        st.session_state.conn = sqlite3.connect("chat_memory.db", check_same_thread=False)
    if "checkpointer" not in st.session_state:
        st.session_state.checkpointer = SqliteSaver(st.session_state.conn)
        st.session_state.checkpointer.setup()  # ensures memory tables exist
    if "graph" not in st.session_state:
        # Build the LangGraph agent once and cache it in session
        st.session_state.graph = build_graph(ALL_TOOLS, st.session_state.checkpointer)
    if "thread_id" not in st.session_state:
        # Each conversation gets a unique ID for MemorySaver
        st.session_state.thread_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        # UI message log: list of {role, content, tools_used}
        st.session_state.messages = []
    if "tool_call_count" not in st.session_state:
        st.session_state.tool_call_count = 0
    if "quick_query" not in st.session_state:
        st.session_state.quick_query = None

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding: 16px 0 8px'>
            <div style='font-size:2.8rem'>🏥</div>
            <h2 style='color:#f8fafc; margin:6px 0 2px; font-size:1.2rem'>الرفيق الطبي</h2>
            <p style='color:#94a3b8; font-size:.82rem; margin:0'>Al-Rafiq Al-Tibbi</p>
            <br>
            <span class='status-online'><span class='dot'></span>Online</span>
        </div>
        """, unsafe_allow_html=True)
        
        # New Chat Button - Moved up and made smaller
        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            if st.button("✨ New Chat", use_container_width=True, type="primary"):
                st.session_state.messages = []
                st.session_state.thread_id = str(uuid.uuid4())
                st.session_state.tool_call_count = 0
                st.rerun()

        st.divider()

        st.markdown("<p class='section-label'>Session Stats</p>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("💬 Messages", len(st.session_state.messages))
        c2.metric("🔧 Tool Calls", st.session_state.tool_call_count)

        st.divider()

        st.markdown("<p class='section-label'>Quick Actions</p>", unsafe_allow_html=True)
        quick_actions = {
            "👤 Ahmed Ali's record":       "Find patient named Ahmed Ali",
            "👨‍⚕️ Dr. Omar Khaled":        "Show me doctor named Dr. Omar Khaled",
            "💊 Ahmed Ali's prescriptions": "What prescription does Ahmed Ali have?",
            "📅 Ahmed Ali's appointments":  "When is Ahmed Ali's next appointment?",
        }
        for label, query in quick_actions.items():
            if st.button(label, use_container_width=True):
                st.session_state.quick_query = query

        st.divider()

        st.markdown("""
        <div style='text-align:center; color:#484f58; font-size:.73rem; margin-top:24px'>
            LangGraph · LLaMA3-70B · Groq<br>
            <span style='color:#238636'>● </span>Powered by Al-Rafiq AI
        </div>
        """, unsafe_allow_html=True)

def render_message_with_pdf(content: str):
    """Detects PDF_GENERATED tag, strips it from text, and renders a download button."""
    match = re.search(r'\[PDF_GENERATED:\s*(.*?)\]', content)
    if match:
        pdf_path = match.group(1)
        clean_content = content.replace(match.group(0), "").strip()
        st.markdown(clean_content)
        try:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_bytes,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf",
                key=uuid.uuid4().hex  # unique key to prevent UI collisions
            )
        except Exception:
            pass
    else:
        st.markdown(content)

def render_messages():
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🏥"):
                if msg.get("tools_used"):
                    badges = "".join(
                        f'<span class="tool-badge">{TOOL_LABELS.get(t, t)}</span>'
                        for t in msg["tools_used"]
                    )
                    st.markdown(
                        f'<div style="margin-bottom:8px; color:#8b949e; font-size:.82rem">'
                        f'🔧 Used: {badges}</div>',
                        unsafe_allow_html=True,
                    )
                render_message_with_pdf(msg["content"])

def run_agent(user_input: str):
    """
    Stream graph updates and render the response live.
    stream_mode='updates' yields one dict per node execution:
        { "agent": {"messages": [AIMessage(...)]} }
        { "tools": {"messages": [ToolMessage(...)]} }
    We intercept tool messages to show which tools fired,
    and the final AIMessage (no tool_calls) as the response.
    """
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    tools_used = []
    final_response = ""

    with st.chat_message("assistant", avatar="🏥"):
        status = st.empty()
        output = st.empty()

        try:
            for event in st.session_state.graph.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="updates",
            ):
                for node_name, node_data in event.items():
                    for msg in node_data.get("messages", []):

                        if node_name == "tools":
                            # A tool just ran — capture its name
                            tool_name = getattr(msg, "name", "unknown")
                            tools_used.append(tool_name)
                            st.session_state.tool_call_count += 1
                            label = TOOL_LABELS.get(tool_name, tool_name)
                            status.markdown(
                                f'<div style="color:#8b949e; font-size:.85rem">'
                                f'🔧 Using <b style="color:#58a6ff">{label}</b>…</div>',
                                unsafe_allow_html=True,
                            )
                            
                            # Safely extract PDF tag if the tool generated one
                            if hasattr(msg, "content") and "[PDF_GENERATED:" in msg.content:
                                match = re.search(r'\[PDF_GENERATED:\s*(.*?)\]', msg.content)
                                if match:
                                    st.session_state.pending_pdf_path = match.group(1)

                        elif node_name == "agent":
                            # LLM spoke — if it's a final answer (no more tool calls)
                            if hasattr(msg, "content") and msg.content:
                                if not getattr(msg, "tool_calls", None):
                                    final_response = msg.content
                                    
                                    # Inject PDF tag if a tool generated one
                                    if hasattr(st.session_state, "pending_pdf_path"):
                                        final_response += f"\n\n[PDF_GENERATED: {st.session_state.pending_pdf_path}]"
                                        del st.session_state.pending_pdf_path
                                        
                                    status.empty()
                                    with output.container():
                                        render_message_with_pdf(final_response)

        except Exception as e:
            final_response = f"⚠️ Something went wrong: {e}"
            output.markdown(final_response)
            status.empty()

    # Persist to UI history
    st.session_state.messages.append({
        "role": "assistant",
        "content": final_response or "عذرًا، لم أتمكن من الرد.",
        "tools_used": list(dict.fromkeys(tools_used)),  # deduplicated, order preserved
    })

def main():
    init_state()
    render_sidebar()

    st.markdown("""
    <div class='hero'>
        <h1>🏥 الرفيق الطبي &nbsp;|&nbsp; Medical AI Assistant</h1>
        <p>Your intelligent healthcare companion — search, look up records, and get medical guidance</p>
    </div>
    """, unsafe_allow_html=True)

    render_messages()

    # Handle sidebar quick-action buttons
    if st.session_state.quick_query:
        query = st.session_state.quick_query
        st.session_state.quick_query = None
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
        run_agent(query)
        st.rerun()

    # Main chat input
    if prompt := st.chat_input("Ask me anything — medical records, symptoms, medications…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        run_agent(prompt)


if __name__ == "__main__":
    main()
