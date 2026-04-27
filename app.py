#app.py
import logging
import streamlit as st
import pandas as pd


from data_tools import (
    get_account_details,
    identify_high_value_customers,
    get_account_details_structured,
    identify_high_value_customers_structured,
    get_customer_portfolio_by_id,
    get_customer_id_by_account_id,
)



# --- Logging setup (same logger name as in data_tools.py) ---
logger = logging.getLogger("agentic_poc")
logger.setLevel(logging.INFO)
if not logger.handlers:
    file_handler = logging.FileHandler("poc.log")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# --- Streamlit page config ---
st.set_page_config(page_title="Agentic Banking PoC", page_icon="🏦", layout="wide")

st.title("🏦 Agentic Banking PoC")
st.markdown("### Relationship Manager Assistant (Local / Cloud Demo)")

st.sidebar.markdown("#### ℹ️ How this works")
st.sidebar.write(
    "- Mock core banking data in SQLite\n"
    "- Python functions behave like MCP-style tools\n"
    "- PII masking for high-value customer lists\n"
    "- Read-only access, no real customer data"
)

st.divider()

# --- Chat history state ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- User input ---
user_query = st.chat_input("Ask about an account, portfolio, or high-value customers...")

if user_query:
    logger.info('UI_QUERY|text="%s"', user_query.replace('"', "'"))

    # Store and display user message
    st.session_state["messages"].append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    response = ""
    route = ""
    q_lower = user_query.lower()

    # === ROUTING CONDITION STARTS HERE ===

    # Route 1: High-value customers
    if "high" in q_lower or "gold" in q_lower or "high value" in q_lower:
        route = "high_value"
        logger.info("ROUTING|high_value")
        hv_list = identify_high_value_customers_structured(50000.0)

        with st.chat_message("assistant"):
            if not hv_list:
                response = "No customers found above the specified balance threshold."
                st.warning(response)
            else:
                import pandas as pd

                df = pd.DataFrame(hv_list)
                df["balance"] = df["balance"].map(lambda x: f"{x:,.2f}")

                st.subheader("High-value customers (masked)")
                st.caption(
                    "PII is masked; only customer tokens and balances are shown."
                )
                st.table(
                    df.rename(
                        columns={
                            "masked_id": "Customer Token",
                            "balance": "Balance",
                        }
                    )
                )
                response = (
                    f"{len(hv_list)} high-value customers found (masked tokens shown)."
                )

    # Route 2: Account details
    elif "acc" in q_lower:
        route = "account_details"
        acc_id = None
        words = user_query.replace(",", " ").split()
        for w in words:
            if w.upper().startswith("ACC"):
                acc_id = w.upper()
                break

        if acc_id is None:
            response = "I could not detect an account ID like ACC001 in your question."
            logger.warning("ROUTING|account_details|status=NO_ACC_ID_DETECTED")
            with st.chat_message("assistant"):
                st.warning(response)
        else:
            logger.info("ROUTING|account_details|account_id=%s", acc_id)
            details = get_account_details_structured(acc_id)

            with st.chat_message("assistant"):
                if not details:
                    response = f"Account {acc_id} not found."
                    st.error(response)
                else:
                    st.subheader(f"Account overview – {details['account_id']}")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Balance", f"{details['balance']:,.2f}")
                    col2.metric("Type", details["account_type"])
                    col3.metric("KYC Status", details["kyc_status"])
                    st.info(f"Customer: **{details['customer_name']}**")

                    response = (
                        f"Account {details['account_id']} | "
                        f"{details['customer_name']} | "
                        f"{details['balance']:,.2f} | "
                        f"{details['account_type']} | "
                        f"{details['kyc_status']}"
                    )
    # Route 3: Customer portfolio (by customer_id or account_id)
    elif "portfolio" in q_lower or "cust" in q_lower:
        route = "customer_portfolio"
        logger.info("ROUTING|customer_portfolio")

        cust_id = None
        acc_id = None

        # Detect CUSTxxx or ACCxxx tokens in the query
        words = user_query.replace(",", " ").split()
        for w in words:
            w_up = w.upper()
            if w_up.startswith("CUST"):
                cust_id = w_up
                break
            if w_up.startswith("ACC"):
                acc_id = w_up

        # Resolve customer_id if only account_id is provided
        if not cust_id and acc_id:
            logger.info("ROUTING|customer_portfolio|via_account_id=%s", acc_id)
            cust_id = get_customer_id_by_account_id(acc_id)
            logger.info(
                "ROUTING|customer_portfolio|resolved_customer_id=%s", cust_id
            )

        with st.chat_message("assistant"):
            if not cust_id:
                response = (
                    "Please specify a customer id or account id, e.g.,\n"
                    "- 'Show portfolio for CUST1'\n"
                    "- 'Show portfolio for ACC001'"
                )
                st.warning(response)
            else:
                details = get_customer_portfolio_by_id(cust_id)
                if details["status"] == "NOT_FOUND":
                    response = f"No accounts found for customer id '{cust_id}'."
                    st.warning(response)
                else:
                    st.subheader(
                        f"Portfolio – {details['customer_name']} ({details['customer_id']})"
                    )
                    st.metric(
                        "Total balance",
                        f"{details['total_balance']:,.2f}",
                    )
                    df = pd.DataFrame(details["accounts"])
                    df["balance"] = df["balance"].map(
                        lambda x: f"{x:,.2f}"
                    )
                    st.table(
                        df.rename(
                            columns={
                                "account_id": "Account ID",
                                "kyc_status": "KYC",
                            }
                        )
                    )
                    response = (
                        f"{len(details['accounts'])} accounts, total balance "
                        f"{details['total_balance']:,.2f}"
                    )
    # Route 3: Customer portfolio (by customer_id or account_id)
    
   
    # Route 4: Help / unsupported query
    else:
        route = "help"
        response = (
            "I currently support:\n"
            "- \"Show high value customers\"\n"
            "- \"Get details for ACC001\" (or any ACCxxx in the mock data)\n"
            "- \"Show portfolio for <Customer Name>\""
        )
        with st.chat_message("assistant"):
            st.markdown(response)

    # === ROUTING CONDITION ENDS HERE ===

    logger.info("UI_RESPONSE|route=%s|length=%d", route, len(response))
    st.session_state["messages"].append({"role": "assistant", "content": response})