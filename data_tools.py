# data_tools.py
import hashlib
import logging
from typing import List, Dict, Optional

#from provider import PostgresProvider
#--- BankingDataProvider
def _init_provider() -> BankingDataProvider:
    mode = os.getenv("DATA_PROVIDER", "postgres").lower()
    if mode == "api":
        return ApiProvider()
    # default
    return PostgresProvider()

#--- BankingDataProvider

provider = _init_provider()

# --- Logging setup ---
logger = logging.getLogger("agentic_poc")
logger.setLevel(logging.INFO)
if not logger.handlers:
    file_handler = logging.FileHandler("poc.log")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# --- Provider 
provider = PostgresProvider()

# --- Provider 

# --- PII masking helper ---

def mask_name(name: str) -> str:
    token = hashlib.md5(name.encode()).hexdigest()[:4]
    return f"CUST_{token}"


# --- Core helpers ---

def _get_balance_for_account(account_id: str) -> Optional[float]:
    """Get latest balance from account_master for an account."""
    with get_pg_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT balance
            FROM core_poc.account_master
            WHERE account_id = %s
            """,
            (account_id,),
        )
        row = cur.fetchone()
    return row[0] if row else None


# --- Tool 1: get_account_details (string) ---

def get_account_details(account_id: str) -> str:
    """
    Fetch full account details for a specific ID (no masking, for RM single-customer view).
    """
    logger.info("TOOL_CALL|get_account_details|account_id=%s", account_id)

    data = provider.fetch_account_details(account_id)

    if not data:
        logger.warning(
            "TOOL_RESULT|get_account_details|account_id=%s|status=NOT_FOUND",
            account_id,
        )
        return f"Account {account_id} not found."

    logger.info(
        "TOOL_RESULT|get_account_details|account_id=%s|status=FOUND|balance=%.2f|type=%s|kyc=%s",
        data["account_id"],
        data["balance"],
        data["account_type"],
        data["kyc_status"],
    )

    return (
        f"Account: {data['account_id']}\n"
        f"Customer: {data['customer_name']}\n"
        f"Balance: {data['balance']:,.2f}\n"
        f"Type: {data['account_type']}\n"
        f"KYC Status: {data['kyc_status']}"
    )
    
# --- Tool 1b: get_account_details_structured ---

def get_account_details_structured(account_id: str) -> Dict[str, object]:
    """
    Returns account details as a dict for UI rendering.
    Empty dict if account not found.
    """
    logger.info("TOOL_CALL|get_account_details_structured|account_id=%s", account_id)

    data = provider.fetch_account_details(account_id)

    if not data:
        logger.warning(
            "TOOL_RESULT|get_account_details_structured|account_id=%s|status=NOT_FOUND",
            account_id,
        )
        return {}

    logger.info(
        "TOOL_RESULT|get_account_details_structured|account_id=%s|status=FOUND|balance=%.2f|prod=%s|kyc=%s",
        data["account_id"],
        data["balance"],
        data["account_type"],
        data["kyc_status"],
    )
    return data



# --- Tool 2: identify_high_value_customers (string) ---

def identify_high_value_customers(threshold: float = 50000.0) -> str:
    """
    Returns masked high-value customers with balances above threshold.
    """
    logger.info("TOOL_CALL|identify_high_value_customers|threshold=%.2f", threshold)

    rows = identify_high_value_customers_structured(threshold)

    if not rows:
        logger.info(
            "TOOL_RESULT|identify_high_value_customers|threshold=%.2f|count=0",
            threshold,
        )
        return (
            f"No customers found above the specified balance threshold of {threshold:,.2f}."
        )

    masked_results = [
        f"{row['masked_id']} (Balance: {row['balance']:,.2f})" for row in rows
    ]

    logger.info(
        "TOOL_RESULT|identify_high_value_customers|threshold=%.2f|count=%d",
        threshold,
        len(masked_results),
    )

    return "High-value customers (masked): " + " | ".join(masked_results)


# --- Tool 2b: identify_high_value_customers_structured ---

def identify_high_value_customers_structured(
    threshold: float = 50000.0,
) -> List[Dict[str, object]]:
    """
    Returns list of dicts with masked_id and balance for high-value customers.
    """
    logger.info(
        "TOOL_CALL|identify_high_value_customers_structured|threshold=%.2f",
        threshold,
    )

    rows = provider.fetch_high_value_customers(threshold)

    result: List[Dict[str, object]] = []
    for row in rows:
        name = row["customer_name"]
        total = row["total_balance"]
        result.append(
            {
                "masked_id": mask_name(name),
                "balance": float(total),
            }
        )

    logger.info(
        "TOOL_RESULT|identify_high_value_customers_structured|threshold=%.2f|count=%d",
        threshold,
        len(result),
    )
    return result

# --- Tool 3: customer portfolio by customer_id (CIF) ---

def get_customer_portfolio_by_id(customer_id: str) -> Dict[str, object]:
    """
    Portfolio view for a given customer_id (CIF).
    """
    logger.info(
        "TOOL_CALL|get_customer_portfolio_by_id|customer_id=%s",
        customer_id,
    )

    details = provider.fetch_customer_portfolio(customer_id)

    if details["status"] == "NOT_FOUND":
        logger.warning(
            "TOOL_RESULT|get_customer_portfolio_by_id|customer_id=%s|status=NOT_FOUND",
            customer_id,
        )
    else:
        logger.info(
            "TOOL_RESULT|get_customer_portfolio_by_id|customer_id=%s|status=FOUND|count=%d|total_balance=%.2f",
            customer_id,
            len(details["accounts"]),
            details["total_balance"],
        )

    return details

# --- Tool 4: resolve customer_id from account_id ---

def get_customer_id_by_account_id(account_id: str) -> Optional[str]:
    """
    Returns customer_id for a given account_id, or None if not found.
    """
    return provider.resolve_customer_id(account_id)