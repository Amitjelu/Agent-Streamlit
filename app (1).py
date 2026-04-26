import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title="Tool Toggle Agent", layout="centered")

st.title("🤖 Smart AI Agent")
st.write("Chat with the AI. Toggle Web Search ON or OFF.")

# -------------------------
# 1. SIDEBAR
# -------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    user_api_key = st.text_input("Enter Groq API Key:", type="password")

    use_search = st.toggle("Enable Web Search", value=True)

    if use_search:
        st.success("Web search tool is ON")
    else:
        st.warning("Web search tool is OFF")

# -------------------------
# 2. MEMORY
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------
# 3. SHOW CHAT HISTORY
# -------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------
# 4. USER INPUT
# -------------------------
if user_query := st.chat_input("Ask me anything..."):

    if not user_api_key:
        st.error("Please enter your API key in the sidebar.")
    else:

        # Show user message
        st.session_state.messages.append({"role": "user", "content": user_query})

        with st.chat_message("user"):
            st.markdown(user_query)

        # -------------------------
        # 4A. LLM
        # -------------------------
        llm = ChatGroq(
            temperature=0,
            model="llama-3.3-70b-versatile",   # FIXED MODEL
            api_key=user_api_key
        )

        # -------------------------
        # 4B. TOOLS
        # -------------------------
        web_tool = DuckDuckGoSearchRun()

        if use_search:
            active_tools = [web_tool]
        else:
            active_tools = []

        # -------------------------
        # 4C. SYSTEM PROMPT
        # -------------------------
        sys_prompt = """
You are a helpful AI assistant.

If web search is enabled, use the search tool to find current information.
If tools are unavailable, answer using your knowledge.

Always respond clearly.
"""

        # -------------------------
        # 4D. CREATE AGENT
        # -------------------------
        agent = create_react_agent(
            llm,
            tools=active_tools,
            prompt=sys_prompt
        )

        # -------------------------
        # 4E. CONVERT CHAT HISTORY
        # -------------------------
        langgraph_history = []

        for m in st.session_state.messages:
            if m["role"] == "user":
                langgraph_history.append(HumanMessage(content=m["content"]))
            else:
                langgraph_history.append(AIMessage(content=m["content"]))

        # -------------------------
        # 4F. RUN AGENT
        # -------------------------
        with st.chat_message("assistant"):

            if use_search:
                spinner_text = "🌍 Searching the web..."
            else:
                spinner_text = "🤖 Thinking..."

            with st.spinner(spinner_text):

                result = agent.invoke({"messages": langgraph_history})
                bot_answer = result["messages"][-1].content

            st.markdown(bot_answer)

        # Save assistant message
        st.session_state.messages.append(
            {"role": "assistant", "content": bot_answer}
        )
