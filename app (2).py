import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
import os

st.set_page_config(page_title="Live Web Agent", layout="centered")

st.title("🌍 The Live Internet Agent")
st.write("Ask me anything about current events. I will browse the web to find the answer.")

# --- 1. SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ System Config")
    user_api_key = st.text_input("Groq API Key:", type="password")
    tavily_api_key = st.text_input("Tavily API Key:", type="password")
    model_choice = st.selectbox(
        "Select Groq Model:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it", "mixtral-8x7b-32768"],
        index=0
    )

    st.divider()

    # ✅ TOOL TOGGLE
    use_search = st.toggle("🔍 Enable Web Search", value=True)
    if use_search:
        st.success("Web search is ON — AI will browse the web.")
    else:
        st.warning("Web search is OFF — AI will answer from memory only.")

    st.markdown("[Get free Tavily API key](https://app.tavily.com/sign-in)")
    st.markdown("[Get free Groq API key](https://console.groq.com/keys)")

# --- 2. MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. DISPLAY CHAT HISTORY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 4. CHAT INPUT ---
if user_query := st.chat_input("Ask about today's news..."):

    if not user_api_key:
        st.error("Please enter your Groq API Key in the sidebar.")
    elif not tavily_api_key and use_search:
        st.error("Please enter your Tavily API Key in the sidebar (required when Web Search is ON).")

    else:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        os.environ["TAVILY_API_KEY"] = tavily_api_key if tavily_api_key else ""

        llm = ChatGroq(
            temperature=0,
            model=model_choice,
            api_key=user_api_key
        )

        # --- 4B. TOOL TOGGLE LOGIC ---
        web_tool = TavilySearchResults(
            max_results=5,
            description="Search the internet for current, up-to-date information"
        )

        if use_search:
            active_tools = [web_tool]   # Web search ON
        else:
            active_tools = []           # Web search OFF

        # System prompt adapts to toggle state
        if use_search:
            sys_prompt = """You are a live research assistant.
Rules:
- Always use the web search tool to gather current information.
- Do not answer from memory alone.
- Search first, then summarize clearly.
"""
        else:
            sys_prompt = """You are a helpful AI assistant.
Rules:
- Answer using your own knowledge (web search is currently disabled).
- Be clear and concise.
- If you are unsure, say so honestly.
"""

        # ✅ Pass active_tools instead of hardcoded [web_tool]
        agent = create_react_agent(llm, tools=active_tools, prompt=sys_prompt)

        langgraph_history = []
        for m in st.session_state.messages:
            if m["role"] == "user":
                langgraph_history.append(HumanMessage(content=m["content"]))
            else:
                langgraph_history.append(AIMessage(content=m["content"]))

        with st.chat_message("assistant"):
            mode_label = "🔍 Browsing the web..." if use_search else "🧠 Thinking from memory..."
            with st.spinner(mode_label):
                try:
                    result_state = agent.invoke({"messages": langgraph_history})
                    bot_answer = result_state["messages"][-1].content if "messages" in result_state else "Sorry, I couldn't retrieve the answer."
                except Exception as e:
                    error_msg = str(e)
                    if "401" in error_msg or "invalid_api_key" in error_msg.lower():
                        bot_answer = "⚠️ **Invalid Groq API Key.** Please check your key in the sidebar."
                    elif "429" in error_msg or "rate_limit" in error_msg.lower():
                        bot_answer = "⚠️ **Rate limit hit.** Please wait a moment and try again."
                    else:
                        bot_answer = f"⚠️ **Error:** `{error_msg}`"

            st.markdown(bot_answer)

        st.session_state.messages.append({"role": "assistant", "content": bot_answer})
