# Agentic Banking PoC – Relationship Manager Assistant

This repository contains a **BFSI-focused Agentic AI PoC** that demonstrates how a Relationship Manager (RM) can query a core‑banking‑like system via **MCP‑ready tools** with PII masking and audit logging.

The PoC is structured into four conceptual layers:

1. **Presentation (UI)** – Streamlit app (`app.py`) acting as an RM assistant.
2. **Tool Layer** – Structured Python tools in `data_tools.py`.
3. **MCP Server Layer** – (optional) `AgenticBankingGateway` server in `mcp_server.py` built with the official MCP Python SDK.
4. **Data Layer** – PostgreSQL schema (`core_poc`) that mimics core banking tables (customer, account, transactions, KYC).

---

## Data Layer – PostgreSQL core schema

The PoC uses a PostgreSQL database with a dedicated schema `core_poc`:

- `customer_master` – CIF/customer master.
- `account_master` – account master with balances and product types.
- `transactions` – account transaction history (for future extensions).
- `kyc_details` – customer KYC status and review dates.

Schema and seed data are provided as SQL files:

- `postgres_schema.sql` – creates `core_poc` schema and tables.
- `postgres_seed.sql` – inserts sample data for:
  - Customers: `CUST1` (John Doe), `CUST2` (Mary Smith).
  - Accounts: `ACC001`, `ACC002`, `ACC003` for CUST1; `ACC101` for CUST2.
  - KYC details for both customers.

---

## MCP‑ready tools (data_tools.py)

These tools are implemented in `data_tools.py`. They are **read‑only**, return **structured JSON‑like objects**, and apply **PII masking** where appropriate.

### 1. `get_account_details_structured(account_id)`

Fetch full account + KYC details for a given account ID.

| Field           | Type  | Description                                                |
|----------------|-------|------------------------------------------------------------|
| `account_id`   | str   | Unique account identifier                                  |
| `customer_name`| str   | Customer full name (RM internal view)                      |
| `balance`      | float | Current balance                                            |
| `account_type` | str   | Product type (e.g., Savings, Current, Term Deposit)        |
| `kyc_status`   | str   | KYC status (e.g., KYC_OK, KYC_DUE)                         |

### 2. `identify_high_value_customers_structured(threshold)`

Returns a list of **masked** high‑value customers whose total portfolio balance is above the given threshold.

| Field       | Type  | Description                                                                       |
|-------------|-------|-----------------------------------------------------------------------------------|
| `masked_id` | str   | Deterministic token derived from customer name (e.g., `CUST_121f`), PII not shown |
| `balance`   | float | Total portfolio balance for that customer                                        |

### 3. `get_customer_portfolio_by_id(customer_id)`

Returns a CIF‑based portfolio view for a given `customer_id` (CUSTx):

- List of accounts with type / balance / KYC.
- Total relationship balance.
- Customer name and status flag.

### 4. `get_customer_id_by_account_id(account_id)`

Utility function that resolves `customer_id` (CIF) from an `account_id` (ACCx), used to support queries like “Show portfolio for ACC001”.

---

## Optional MCP server – `AgenticBankingGateway`

If you include `mcp_server.py`, the tool layer can be wrapped in an MCP server:

- Server name: `AgenticBankingGateway`.
- Example MCP tools (names are illustrative):
  - `mcp_get_account_details` → `get_account_details_structured(account_id)`.
  - `mcp_list_high_value_customers` → `identify_high_value_customers_structured(threshold)`.

Any MCP‑compatible client (LLM agent, IDE extension, internal AI gateway) can connect to this server and invoke tools against the same PostgreSQL schema, without direct DB access.

---

## Streamlit RM Assistant (app.py)

The Streamlit app (`app.py`) uses these tools to provide a Relationship Manager–friendly interface:

- **Account queries**  
  - Prompt: `Get details for ACC001`  
  - Shows metrics: balance, product type, KYC status, customer name.

- **Customer portfolio queries**  
  - Prompts: `Show portfolio for CUST1`, `Show portfolio for ACC001`  
  - Shows CIF‑level portfolio: list of accounts + total relationship balance.

- **High‑value customer queries**  
  - Prompt: `Show high value customers`  
  - Shows masked tokens (`CUST_xxxx`) and balances, with PII hidden.

All interactions and tool calls are logged to `poc.log` for demo and audit purposes.

---

## 1. Local setup

```bash
git clone https://github.com/SMV1969/agentic-banking-poc.git
cd agentic-banking-poc

python -m venv .venv
.\.venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

---

## 2. PostgreSQL schema and sample data

Create or reuse a PostgreSQL database (the examples below use the default `postgres` DB):

```bash
psql -U postgres -d postgres -f postgres_schema.sql
psql -U postgres -d postgres -f postgres_seed.sql
```

This creates schema `core_poc` and loads CUST1/CUST2 + ACC001… data.

---

## 3. Configure DB connection

The app reads connection settings from environment variables via `.env`.

1. Copy the example file:

```bash
copy .env.example .env   # Windows
```

2. Edit `.env`:

```env
PG_HOST=localhost
PG_PORT=5432
PG_DB=postgres
PG_USER=postgres
PG_PASS=yourpassword
```

> In a client bank, these values would point to the **core transactional database** or a curated data mart / data lake, rather than the local PoC instance.

---

## 4. Run the app locally

From the project root:

```bash
.\.venv\Scripts\activate
streamlit run app.py
```

Try prompts such as:

- `Show high value customers`
- `Get details for ACC001`
- `Show portfolio for CUST1`
- `Show portfolio for ACC001`

---

## 5. Deployment (Streamlit Cloud)

To deploy on Streamlit Community Cloud:

1. Create a new app pointing to this GitHub repo.  
2. In app settings, add the same DB environment variables (`PG_HOST`, `PG_PORT`, `PG_DB`, `PG_USER`, `PG_PASS`) as **secrets**.  
3. Ensure your PostgreSQL instance is reachable from Streamlit Cloud (e.g., public IP or SSH tunnel / cloud DB).  
4. Once the app builds, use the same prompts as in local setup.

This PoC then becomes a template: in a real bank, you would swap the PoC Postgres with the bank’s **core system** or **data lake** and keep the same agentic tool and UI logic.