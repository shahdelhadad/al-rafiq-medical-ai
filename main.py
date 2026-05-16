# main.py — CLI entry point (the Streamlit UI is in app.py)
import uuid
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from agent import build_graph, ALL_TOOLS

load_dotenv()

def main():
    graph = build_graph(ALL_TOOLS)
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("👋 أهلاً بك! أنا رفيقك الطبي، جاهز أساعدك. (Type 'exit' to quit)\n")

    while True:
        user_input = input("👤 أنت: ").strip()

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "bye", "q", "خروج"}:
            print("👋 إلى اللقاء! أتمنى لك الصحة والعافية.")
            break

        try:
            result = graph.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
            )
            # The last message in state is always the final AI response
            response = result["messages"][-1].content
            print(f"\n🤖 الرفيق الطبي: {response}\n")

        except Exception as e:
            print(f"⚠️ حدث خطأ: {e}\n")


if __name__ == "__main__":
    main()
