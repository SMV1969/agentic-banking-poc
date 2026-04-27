# Agentic Banking PoC – Relationship Manager Assistant

This repository contains a **BFSI-focused Agentic AI PoC** that demonstrates how a Relationship Manager (RM) can query a core‑banking‑like system via **MCP‑ready tools** with PII masking and audit logging.

The PoC is structured into four layers:

1. **Presentation (UI)** – Streamlit app (`app.py`) acting as an RM assistant.
2. **Tool Layer** – Structured Python tools in `data_tools.py`.
3. **MCP Server Layer** – `AgenticBankingGateway` server in `mcp_server.py` built with the official MCP Python SDK.
4. **Data Layer** – SQLite mock core banking database (`banking_core.db`) populated by `setup_db.py`.

---

## MCP‑Ready Tools

These tools are implemented in `data_tools.py` and exposed via `mcp_server.py` using the Model Context Protocol (MCP). They are **read‑only**, return **structured JSON‑like objects**, and apply **PII masking** where appropriate.

### 1. `get_account_details_structured(account_id)`

Fetches full account details for a given account ID.

| Field         | Type   | Description                          |
| ------------- | ------ | ------------------------------------ |
| `account_id`  | str    | Unique account identifier            |
| `customer_name` | str  | Customer full name (not masked here; intended for internal RM view) |
| `balance`     | float  | Current balance                      |
| `account_type`| str    | Account type (e.g., Savings, Current, Gold) |
| `kyc_status`  | str    | KYC status (Verified, Pending, etc.) |

**Example call (from `tool_client_test.py`):**

```python
from data_tools import get_account_details_structured

get_account_details_structured("ACC003")
```

**Example response:**

```python
{
  "account_id": "ACC003",
  "account_type": "Gold",
  "balance": 75000.0,
  "customer_name": "Chiku Van",
  "kyc_status": "Verified"
}
```

---

### 2. `identify_high_value_customers_structured(threshold)`

Returns a list of **masked** high‑value customers whose balance is above the given threshold.

| Field       | Type   | Description                                           |
| ----------- | ------ | ----------------------------------------------------- |
| `masked_id` | str    | Deterministic token derived from customer name (e.g., `CUST_121f`), PII is not exposed |
| `balance`   | float  | Current balance of the high‑value account            |

**Example call (from `tool_client_test.py`):**

```python
from data_tools import identify_high_value_customers_structured

identify_high_value_customers_structured(50000.0)
```

**Example response (truncated):**

```python
[
  {"balance": 75000.0, "masked_id": "CUST_121f"},
  {"balance": 52000.0, "masked_id": "CUST_cfe5"},
  {"balance": 98000.75, "masked_id": "CUST_be84"},
  {"balance": 64000.0, "masked_id": "CUST_4659"},
  {"balance": 120000.0, "masked_id": "CUST_81e5"},
  {"balance": 51000.0, "masked_id": "CUST_c099"},
  {"balance": 220000.0, "masked_id": "CUST_3539"},
  {"balance": 90000.0, "masked_id": "CUST_10ca"},
  {"balance": 56000.5, "masked_id": "CUST_5e1a"},
  {"balance": 510000.0, "masked_id": "CUST_f030"},
  {"balance": 73000.0, "masked_id": "CUST_d9a6"},
  {"balance": 250000.0, "masked_id": "CUST_1221"}
]
```

PII masking is applied **before** data leaves the tool layer, ensuring that agents and UIs only see anonymized tokens.

---

## MCP Server: `AgenticBankingGateway`

The MCP server (`mcp_server.py`) wraps these tools using the official `mcp` Python SDK:

- Server name: `AgenticBankingGateway`
- Tool endpoints exposed via MCP:

| MCP Tool Name                    | Underlying Python Function                     | Description                                      |
| -------------------------------- | ---------------------------------------------- | ------------------------------------------------ |
| `mcp_get_account_details`        | `get_account_details_structured(account_id)`   | Returns full account & KYC details for an ID    |
| `mcp_list_high_value_customers`  | `identify_high_value_customers_structured(threshold)` | Returns masked high‑value customers list |

Any MCP‑compatible client (LLM agent, IDE extension, or internal AI gateway) can connect to this server and invoke these tools to power agentic banking workflows without direct access to the database.

---

## Headless Tool Test

For quick validation without UI or MCP client, you can run:

```bash
python tool_client_test.py
```

This script calls the same structured tools and prints their outputs, showcasing how the PoC logic works independently of the Streamlit front‑end.

---

## Streamlit RM Assistant

The Streamlit app (`app.py`) uses the same tools to provide a Relationship Manager interface:

- **Account queries** (e.g., `Get details for ACC003`) render an account overview with metrics.
- **High‑value queries** (e.g., `Show high value customers`) render a table of masked customer tokens and balances.
- All interactions are logged in `poc.log` for auditability.

This combination demonstrates how a bank could plug MCP‑based tools into both **human UIs** and **autonomous agents** while preserving data security and governance.