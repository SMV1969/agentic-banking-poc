import sqlite3
import hashlib
import logging
from typing import List, Dict
from pathlib import Path

DB_FILE = "banking_core.db"

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
    
def _get_connection():
    db_path = Path(DB_FILE)
    if not db_path.exists():
        logger.error("Database file not found at %s", db_path.absolute())
    return sqlite3.connect(db_path)
    
# --- PII masking helper ---

def mask_name(name: str) -> str:
    """
    Creates a consistent, non-reversible token for a name.
    Example: 'John Doe' -> 'CUST_58d1'
    """
    token = hashlib.md5(name.encode()).hexdigest()[:4]
    return f"CUST_{token}"


#-----get_customer_portfolio_structured_by_ID
def get_customer_portfolio_by_id(customer_id: str) -> Dict[str, object]:
    """
    Returns a portfolio view for a given customer_id (CIF):
    - list of accounts (id, type, balance, kyc)
    - total balance
    """
    logger.info(
        "TOOL_CALL|get_customer_portfolio_by_id|customer_id=%s", customer_id
    )

    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT account_id, customer_name, balance, account_type, kyc_status
        FROM accounts
        WHERE customer_id = ?
        """,
        (customer_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        logger.warning(
            "TOOL_RESULT|get_customer_portfolio_by_id|customer_id=%s|status=NOT_FOUND",
            customer_id,
        )
        return {
            "customer_id": customer_id,
            "customer_name": None,
            "status": "NOT_FOUND",
            "accounts": [],
            "total_balance": 0.0,
        }

    accounts = []
    total_balance = 0.0
    customer_name = rows[0][1]  # use name from first row

    for acc_id, name, balance, acc_type, kyc in rows:
        accounts.append(
            {
                "account_id": acc_id,
                "balance": balance,
                "account_type": acc_type,
                "kyc_status": kyc,
            }
        )
        total_balance += balance

    logger.info(
        "TOOL_RESULT|get_customer_portfolio_by_id|customer_id=%s|status=FOUND|count=%d|total_balance=%.2f",
        customer_id,
        len(accounts),
        total_balance,
    )

    return {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "status": "FOUND",
        "accounts": accounts,
        "total_balance": total_balance,
    }


def get_customer_id_by_account_id(account_id: str) -> str | None:
    """
    Returns customer_id for a given account_id, or None if not found.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT customer_id FROM accounts WHERE account_id = ?",
        (account_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return row[0]
    
#-----get_customer_portfolio_structured_by_ID

#-----get_customer_portfolio_structured


def get_customer_portfolio_structured(customer_name: str) -> Dict[str, object]:
    """
    Returns a portfolio view for a given customer_name:
    - list of accounts (id, type, balance, kyc)
    - total balance
    """
    logger.info("TOOL_CALL|get_customer_portfolio_structured|customer_name=%s", customer_name)

    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT account_id, balance, account_type, kyc_status
        FROM accounts
        WHERE customer_name = ?
        """,
        (customer_name,),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        logger.warning(
            "TOOL_RESULT|get_customer_portfolio_structured|customer_name=%s|status=NOT_FOUND",
            customer_name,
        )
        return {
            "customer_name": customer_name,
            "status": "NOT_FOUND",
            "accounts": [],
            "total_balance": 0.0,
        }

    accounts = []
    total_balance = 0.0
    for acc_id, balance, acc_type, kyc in rows:
        accounts.append(
            {
                "account_id": acc_id,
                "balance": balance,
                "account_type": acc_type,
                "kyc_status": kyc,
            }
        )
        total_balance += balance

    logger.info(
        "TOOL_RESULT|get_customer_portfolio_structured|customer_name=%s|status=FOUND|count=%d|total_balance=%.2f",
        customer_name,
        len(accounts),
        total_balance,
    )

    return {
        "customer_name": customer_name,
        "status": "FOUND",
        "accounts": accounts,
        "total_balance": total_balance,
    }


def list_customer_portfolios_above_threshold(threshold: float = 100000.0) -> List[Dict[str, object]]:
    """
    Aggregates accounts by customer_name and returns customers whose
    total portfolio balance exceeds the threshold.
    """
    logger.info(
        "TOOL_CALL|list_customer_portfolios_above_threshold|threshold=%.2f", threshold
    )

    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT customer_name, SUM(balance) as total_balance
        FROM accounts
        GROUP BY customer_name
        HAVING total_balance > ?
        """,
        (threshold,),
    )
    rows = cursor.fetchall()
    conn.close()

    results: List[Dict[str, object]] = []
    for name, total in rows:
        results.append({"customer_name": name, "total_balance": total})

    logger.info(
        "TOOL_RESULT|list_customer_portfolios_above_threshold|threshold=%.2f|count=%d",
        threshold,
        len(results),
    )

    return results
 
#-----get_customer_portfolio_structured


# --- Tool 1: get_details Structured ---
# ... existing imports, logger, _get_connection, mask_name,
# get_account_details, identify_high_value_customers stay as they are ...


def get_account_details_structured(account_id: str) -> Dict[str, object]:
    """
    Returns account details as a dict for UI rendering.
    Empty dict if account not found.
    """
    logger.info("TOOL_CALL|get_account_details_structured|account_id=%s", account_id)

    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT account_id, customer_name, balance, account_type, kyc_status "
        "FROM accounts WHERE account_id = ?",
        (account_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        logger.warning(
            "TOOL_RESULT|get_account_details_structured|account_id=%s|status=NOT_FOUND",
            account_id,
        )
        return {}

    acc_id, name, balance, acc_type, kyc = row
    logger.info(
        "TOOL_RESULT|get_account_details_structured|account_id=%s|status=FOUND|balance=%.2f|type=%s|kyc=%s",
        acc_id,
        balance,
        acc_type,
        kyc,
    )
    return {
        "account_id": acc_id,
        "customer_name": name,
        "balance": balance,
        "account_type": acc_type,
        "kyc_status": kyc,
    }


def identify_high_value_customers_structured(
    threshold: float = 50000.0,
) -> List[Dict[str, object]]:
    """
    Returns list of dicts with masked_id and balance for high-value customers.
    """
    logger.info(
        "TOOL_CALL|identify_high_value_customers_structured|threshold=%.2f", threshold
    )

    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT customer_name, balance FROM accounts WHERE balance > ?",
        (threshold,),
    )
    rows = cursor.fetchall()
    conn.close()

    result: List[Dict[str, object]] = []
    for name, balance in rows:
        result.append(
            {
                "masked_id": mask_name(name),
                "balance": balance,
            }
        )

    logger.info(
        "TOOL_RESULT|identify_high_value_customers_structured|threshold=%.2f|count=%d",
        threshold,
        len(result),
    )
    return result
    

# --- Tool 1: get_details ---


def get_account_details(account_id: str) -> str:
    """
    Fetch full account details for a specific ID (no masking, for RM single-customer view).
    """
    logger.info("TOOL_CALL|get_account_details|account_id=%s", account_id)

    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT account_id, customer_name, balance, account_type, kyc_status "
        "FROM accounts WHERE account_id = ?",
        (account_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        logger.warning("TOOL_RESULT|get_account_details|account_id=%s|status=NOT_FOUND", account_id)
        return f"Account {account_id} not found."

    acc_id, name, balance, acc_type, kyc = row
    logger.info(
        "TOOL_RESULT|get_account_details|account_id=%s|status=FOUND|balance=%.2f|type=%s|kyc=%s",
        acc_id,
        balance,
        acc_type,
        kyc,
    )

    return (
        f"Account: {acc_id}\n"
        f"Customer: {name}\n"
        f"Balance: {balance:,.2f}\n"
        f"Type: {acc_type}\n"
        f"KYC Status: {kyc}"
    )


# --- Tool 2: identify_high_value_customers ---


def identify_high_value_customers(threshold: float = 50000.0) -> str:
    """
    Returns masked high-value customers with balances above threshold.
    """
    logger.info("TOOL_CALL|identify_high_value_customers|threshold=%.2f", threshold)

    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT customer_name, balance FROM accounts WHERE balance > ?",
        (threshold,),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        logger.info(
            "TOOL_RESULT|identify_high_value_customers|threshold=%.2f|count=0", threshold
        )
        return (
            f"No customers found above the specified balance threshold of {threshold:,.2f}."
        )

    masked_results = []
    for name, balance in rows:
        masked_label = mask_name(name)
        masked_results.append(f"{masked_label} (Balance: {balance:,.2f})")

    logger.info(
        "TOOL_RESULT|identify_high_value_customers|threshold=%.2f|count=%d",
        threshold,
        len(masked_results),
    )

    return "High-value customers (masked): " + " | ".join(masked_results)

def identify_high_value_customers_structured(threshold: float = 50000.0) -> list[dict]:
    """
    Returns a list of dicts with masked_id and balance for high-value customers.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT customer_name, balance FROM accounts WHERE balance > ?",
        (threshold,),
    )
    rows = cursor.fetchall()
    conn.close()

    result = []
    for name, balance in rows:
        result.append(
            {
                "masked_id": mask_name(name),
                "balance": balance,
            }
        )
    return result
    