# data_tools.py
import hashlib
import logging
from typing import List, Dict, Optional

from db import get_pg_connection

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

    with get_pg_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.account_id,
                   c.full_name,
                   a.balance,
                   a.product_type,
                   k.kyc_status
            FROM core_poc.account_master a
            JOIN core_poc.customer_master c ON a.customer_id = c.customer_id
            LEFT JOIN core_poc.kyc_details k ON c.customer_id = k.customer_id
            WHERE a.account_id = %s
            """,
            (account_id,),
        )
        row = cur.fetchone()

    if not row:
        logger.warning(
            "TOOL_RESULT|get_account_details|account_id=%s|status=NOT_FOUND",
            account_id,
        )
        return f"Account {account_id} not found."

    acc_id, name, balance, prod, kyc = row
    logger.info(
        "TOOL_RESULT|get_account_details|account_id=%s|status=FOUND|balance=%.2f|type=%s|kyc=%s",
        acc_id,
        balance,
        prod,
        kyc,
    )

    return (
        f"Account: {acc_id}\n"
        f"Customer: {name}\n"
        f"Balance: {balance:,.2f}\n"
        f"Product: {prod}\n"
        f"KYC Status: {kyc}"
    )


# --- Tool 1b: get_account_details_structured ---

def get_account_details_structured(account_id: str) -> Dict[str, object]:
    """
    Returns account details as a dict for UI rendering.
    Empty dict if account not found.
    """
    logger.info("TOOL_CALL|get_account_details_structured|account_id=%s", account_id)

    with get_pg_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.account_id,
                   c.full_name,
                   a.balance,
                   a.product_type,
                   COALESCE(k.kyc_status, 'UNKNOWN') AS kyc_status
            FROM core_poc.account_master a
            JOIN core_poc.customer_master c ON a.customer_id = c.customer_id
            LEFT JOIN core_poc.kyc_details k ON c.customer_id = k.customer_id
            WHERE a.account_id = %s
            """,
            (account_id,),
        )
        row = cur.fetchone()

    if not row:
        logger.warning(
            "TOOL_RESULT|get_account_details_structured|account_id=%s|status=NOT_FOUND",
            account_id,
        )
        return {}

    acc_id, name, balance, prod, kyc = row
    logger.info(
        "TOOL_RESULT|get_account_details_structured|account_id=%s|status=FOUND|balance=%.2f|prod=%s|kyc=%s",
        acc_id,
        balance,
        prod,
        kyc,
    )

    return {
        "account_id": acc_id,
        "customer_name": name,
        "balance": float(balance),
        "account_type": prod,
        "kyc_status": kyc,
    }


# --- Tool 2: identify_high_value_customers (string) ---

def identify_high_value_customers(threshold: float = 50000.0) -> str:
    """
    Returns masked high-value customers with balances above threshold.
    """
    logger.info("TOOL_CALL|identify_high_value_customers|threshold=%.2f", threshold)

    with get_pg_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT c.full_name, SUM(a.balance) AS total_balance
            FROM core_poc.customer_master c
            JOIN core_poc.account_master a ON c.customer_id = a.customer_id
            GROUP BY c.full_name
            HAVING SUM(a.balance) > %s
            """,
            (threshold,),
        )
        rows = cur.fetchall()

    if not rows:
        logger.info(
            "TOOL_RESULT|identify_high_value_customers|threshold=%.2f|count=0",
            threshold,
        )
        return (
            f"No customers found above the specified balance threshold of {threshold:,.2f}."
        )

    masked_results = []
    for name, total in rows:
        masked_label = mask_name(name)
        masked_results.append(f"{masked_label} (Balance: {float(total):,.2f})")

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

    with get_pg_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT c.full_name, SUM(a.balance) AS total_balance
            FROM core_poc.customer_master c
            JOIN core_poc.account_master a ON c.customer_id = a.customer_id
            GROUP BY c.full_name
            HAVING SUM(a.balance) > %s
            """,
            (threshold,),
        )
        rows = cur.fetchall()

    result: List[Dict[str, object]] = []
    for name, total in rows:
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

    with get_pg_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.account_id,
                   c.full_name,
                   a.balance,
                   a.product_type,
                   COALESCE(k.kyc_status, 'UNKNOWN') AS kyc_status
            FROM core_poc.account_master a
            JOIN core_poc.customer_master c ON a.customer_id = c.customer_id
            LEFT JOIN core_poc.kyc_details k ON c.customer_id = k.customer_id
            WHERE a.customer_id = %s
            """,
            (customer_id,),
        )
        rows = cur.fetchall()

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

    accounts: List[Dict[str, object]] = []
    total_balance = 0.0
    customer_name = rows[0][1]

    for acc_id, name, balance, prod, kyc in rows:
        accounts.append(
            {
                "account_id": acc_id,
                "balance": float(balance),
                "account_type": prod,
                "kyc_status": kyc,
            }
        )
        total_balance += float(balance)

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


# --- Tool 4: resolve customer_id from account_id ---

def get_customer_id_by_account_id(account_id: str) -> Optional[str]:
    """
    Returns customer_id for a given account_id, or None if not found.
    """
    with get_pg_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT customer_id
            FROM core_poc.account_master
            WHERE account_id = %s
            """,
            (account_id,),
        )
        row = cur.fetchone()

    return row[0] if row else None