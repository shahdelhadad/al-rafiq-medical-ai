import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
load_dotenv()

SYSTEM_PROMPT = """You are الرفيق الطبي (Al-Rafiq Al-Tibbi), an intelligent medical AI assistant
built to support healthcare staff and patients.

Your capabilities:
- Look up patient records, doctor profiles, prescriptions, and appointments from the internal system
- Search the web for medical topics, drug information, symptoms, and health guidance
- Provide clear, compassionate, and well-organized medical information

Rules:
- Always respond in the SAME language the user writes in (Arabic or English)
- Never fabricate medical data — always use your tools to retrieve accurate information
- When presenting records, format them clearly (use bullet points or structured text)
- If a tool returns a Markdown table, a detailed report, or a special tag like [PDF_GENERATED: ...], you MUST include that EXACT text in your final response to the user so the UI can render it. Do NOT omit or summarize the PDF tag.
- Be concise but thorough
- IMPORTANT: Do NOT add generic disclaimers or warnings about verifying information or consulting a real doctor. Act confidently as the medical assistant.

CRITICAL TOOL CALLING RULE:
If you need to call a tool, you must format the tool call correctly according to the system's schema. NEVER concatenate the tool name and the JSON arguments into a single string like `tool_name{"arg": "val"}`. Provide the tool name and arguments separately.
"""


def build_graph(tools: list, checkpointer=None):
    """
    Build and compile the LangGraph ReAct agent.

    Graph structure:
        START --> [agent node] --> tools_condition -->
            if tool_call:  --> [tools node] --> [agent node]  (loop)
            if done:       --> END

    The checkpointer persists message history per thread_id,
    enabling multi-turn conversations without manual history management.
    """
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.1-8b-instant",  
        temperature=0,
    )

    llm_with_tools = llm.bind_tools(tools)

    def call_agent(state: MessagesState):
        """Agent node: injects system prompt and invokes the LLM."""
        system = SystemMessage(content=SYSTEM_PROMPT)
        response = llm_with_tools.invoke([system] + state["messages"])
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", call_agent)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")   

    return workflow.compile(checkpointer=checkpointer)
