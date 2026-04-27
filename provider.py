# provider.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from db import get_pg_connection


class BankingDataProvider(ABC):
    """
    Abstraction over the bank data source.

    Today: PostgresProvider (PoC DB).
    Future: ApiProvider (bank REST/SOAP APIs), DataLakeProvider, etc.
    """

    @abstractmethod
    def fetch_account_details(self, account_id: str) -> Optional[Dict]:
        ...

    @abstractmethod
    def fetch_customer_portfolio(self, customer_id: str) -> Dict:
        ...

    @abstractmethod
    def fetch_high_value_customers(self, threshold: float) -> List[Dict]:
        ...

    @abstractmethod
    def resolve_customer_id(self, account_id: str) -> Optional[str]:
        ...


class PostgresProvider(BankingDataProvider):
    """
    Concrete provider that reads from the core_poc schema in PostgreSQL.
    """

    def fetch_account_details(self, account_id: str) -> Optional[Dict]:
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
            return None

        acc_id, name, balance, prod, kyc = row
        return {
            "account_id": acc_id,
            "customer_name": name,
            "balance": float(balance),
            "account_type": prod,
            "kyc_status": kyc,
        }

    def fetch_customer_portfolio(self, customer_id: str) -> Dict:
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
            return {
                "customer_id": customer_id,
                "customer_name": None,
                "status": "NOT_FOUND",
                "accounts": [],
                "total_balance": 0.0,
            }

        accounts: List[Dict] = []
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

        return {
            "customer_id": customer_id,
            "customer_name": customer_name,
            "status": "FOUND",
            "accounts": accounts,
            "total_balance": total_balance,
        }

    def fetch_high_value_customers(self, threshold: float) -> List[Dict]:
        with get_pg_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT c.full_name,
                       SUM(a.balance) AS total_balance
                FROM core_poc.customer_master c
                JOIN core_poc.account_master a ON c.customer_id = a.customer_id
                GROUP BY c.full_name
                HAVING SUM(a.balance) > %s
                """,
                (threshold,),
            )
            rows = cur.fetchall()

        result: List[Dict] = []
        for name, total in rows:
            result.append(
                {
                    "customer_name": name,
                    "total_balance": float(total),
                }
            )
        return result

    def resolve_customer_id(self, account_id: str) -> Optional[str]:
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