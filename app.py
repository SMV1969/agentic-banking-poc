
import streamlit as st
from data_tools import get_account_details, identify_high_value_customers

st.set_page_config(page_title="Agentic Banking PoC", page_icon="🏦", layout="wide")

st.title("🏦 Agentic Banking PoC")
st.markdown("### Relationship Manager Assistant (Local Demo)")

st.sidebar.markdown("#### ℹ️ How this works")
st.sidebar.write(
    "- Mock core banking data in SQLite\n"
    "- Python functions act like MCP tools\n"
    "- PII masking for high-value customer lists\n"
    "- All running locally on your machine"
)

st.divider()

# Simple chat-like interaction
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Show chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_query = st.chat_input("Ask about an account or high-value customers...")

if user_query:
    # Add user message
    st.session_state["messages"].append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Basic routing logic (no LLM yet)
    response = ""

    q_lower = user_query.lower()

    if "high" in q_lower or "gold" in q_lower or "high value" in q_lower:
        response = identify_high_value_customers(50000.0)
    elif "acc" in q_lower:
        # crude extraction: find ACC + digits
        acc_id = None
        words = user_query.replace(",", " ").split()
        for w in words:
            if w.upper().startswith("ACC"):
                acc_id = w.upper()
                break
        if acc_id is None:
            response = "I could not detect an account ID like ACC001 in your question."
        else:
            response = get_account_details(acc_id)
    else:
        response = (
            "I currently support:\n"
            "- 'Show high value customers'\n"
            "- 'Get details for ACC001' (or any ACCxxx in the mock data)"
        )

    # Show assistant response
    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state["messages"].append({"role": "assistant", "content": response})