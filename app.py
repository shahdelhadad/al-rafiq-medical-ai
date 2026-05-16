# app.py
import uuid
import streamlit as st
from langchain_core.messages import HumanMessage
from agent import build_graph, ALL_TOOLS

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="الرفيق الطبي | Medical AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, body { font-family: 'Inter', sans-serif !important; }

.stApp { background-color: #0d1117; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #161b27 0%, #0d1117 100%);
    border-right: 1px solid #21262d;
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }

/* Header card */
.hero {
    background: linear-gradient(135deg, #161b27 0%, #0d1117 100%);
    border: 1px solid #21262d;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    text-align: center;
}
.hero h1 {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #58a6ff, #3fb950);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 8px 0;
}
.hero p { color: #8b949e; font-size: 0.92rem; margin: 0; }

/* Tool badge */
.tool-badge {
    display: inline-block;
    background: #0d2137;
    color: #58a6ff;
    border: 1px solid #1f6feb;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin: 2px 3px;
}

/* Status pill */
.status-online {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #0d2818;
    color: #3fb950;
    border: 1px solid #238636;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
}
.dot { width: 7px; height: 7px; background: #3fb950;
        border-radius: 50%; display: inline-block;
        animation: blink 2s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

/* Section label */
.section-label {
    color: #484f58;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
    margin: 18px 0 8px 0;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Tool display names ────────────────────────────────────────────────────────
TOOL_LABELS = {
    "search_web":       "🔍 Web Search",
    "get_patient_data": "👤 Patient Lookup",
    "get_doctor_data":  "👨‍⚕️ Doctor Lookup",
    "get_prescriptions":"💊 Prescriptions",
    "get_appointments": "📅 Appointments",
}

# ── Session state init ────────────────────────────────────────────────────────
def init_state():
    if "graph" not in st.session_state:
        # Build the LangGraph agent once and cache it in session
        st.session_state.graph = build_graph(ALL_TOOLS)
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

# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding: 16px 0 8px'>
            <div style='font-size:2.8rem'>🏥</div>
            <h2 style='color:#e6edf3; margin:6px 0 2px; font-size:1.2rem'>الرفيق الطبي</h2>
            <p style='color:#8b949e; font-size:.82rem; margin:0'>Al-Rafiq Al-Tibbi</p>
            <br>
            <span class='status-online'><span class='dot'></span>Online</span>
        </div>
        """, unsafe_allow_html=True)

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

        if st.button("🔄 New Conversation", use_container_width=True, type="primary"):
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.tool_call_count = 0
            st.rerun()

        st.markdown("""
        <div style='text-align:center; color:#484f58; font-size:.73rem; margin-top:24px'>
            LangGraph · LLaMA3-70B · Groq<br>
            <span style='color:#238636'>● </span>Powered by Al-Rafiq AI
        </div>
        """, unsafe_allow_html=True)

# ── Message rendering ─────────────────────────────────────────────────────────
def render_messages():
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
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
                st.markdown(msg["content"])

# ── Core: stream a response from the graph ────────────────────────────────────
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

                        elif node_name == "agent":
                            # LLM spoke — if it's a final answer (no more tool calls)
                            if hasattr(msg, "content") and msg.content:
                                if not getattr(msg, "tool_calls", None):
                                    final_response = msg.content
                                    status.empty()
                                    output.markdown(final_response)

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

# ── Main layout ───────────────────────────────────────────────────────────────
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
