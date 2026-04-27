import sqlite3
from pathlib import Path

DB_FILE = "banking_core.db"


def init_db():
    db_path = Path(DB_FILE)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Create accounts table (mock core)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            account_id TEXT PRIMARY KEY,
            customer_name TEXT,
            balance REAL,
            account_type TEXT,
            kyc_status TEXT
        )
        """
    )

    # 2. Seed mock data (20 accounts across types / KYC states)
    mock_data = [
        ("ACC001", "John Doe", 15000.50, "Savings", "Verified"),
        ("ACC002", "Jane Smith", 2500.00, "Current", "Pending"),
        ("ACC003", "Chiku Van", 75000.00, "Gold", "Verified"),
        ("ACC004", "Ravi Kumar", 52000.00, "Savings", "Verified"),
        ("ACC005", "Sara Ali", 98000.75, "Gold", "Verified"),
        ("ACC006", "Mohammed Faisal", 4300.00, "Current", "Pending"),
        ("ACC007", "Priya Singh", 64000.00, "Savings", "Verified"),
        ("ACC008", "Ahmed Hassan", 120000.00, "Gold", "Verified"),
        ("ACC009", "Lena George", 8000.25, "Savings", "Verified"),
        ("ACC010", "Rahul Mehta", 31000.00, "Current", "Pending"),
        ("ACC011", "Fatima Noor", 51000.00, "Savings", "Verified"),
        ("ACC012", "Kunal Shah", 220000.00, "Gold", "Verified"),
        ("ACC013", "Ayesha Khan", 47000.00, "Savings", "Pending"),
        ("ACC014", "Omar Saleh", 90000.00, "Current", "Verified"),
        ("ACC015", "Neha Jain", 56000.50, "Savings", "Verified"),
        ("ACC016", "Vikas Gupta", 1200.00, "Current", "Pending"),
        ("ACC017", "Sanjay Patel", 510000.00, "Gold", "Verified"),
        ("ACC018", "Meera Iyer", 45000.00, "Savings", "Verified"),
        ("ACC019", "Hassan Ali", 73000.00, "Current", "Verified"),
        ("ACC020", "Rashmi Rao", 250000.00, "Gold", "Verified"),
    ]

    cursor.executemany(
        "REPLACE INTO accounts (account_id, customer_name, balance, account_type, kyc_status) "
        "VALUES (?,?,?,?,?)",
        mock_data,
    )

    conn.commit()
    conn.close()

    print(f"Mock Banking Core Ready at {db_path.absolute()}")


if __name__ == "__main__":
    init_db()