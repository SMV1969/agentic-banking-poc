import sqlite3
from pathlib import Path

DB_FILE = "banking_core.db"


def init_db():
    db_path = Path(DB_FILE)

    # Start fresh: delete existing DB file if it exists
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Create accounts table (mock core)
    cursor.execute(
        """
        CREATE TABLE accounts (
            account_id   TEXT PRIMARY KEY,
            customer_id  TEXT,
            customer_name TEXT,
            balance      REAL,
            account_type TEXT,
            kyc_status   TEXT
        )
        """
    )

    # 2. Seed mock data (customer_id added, all as strings)
    mock_data = [
        ("ACC001", "CUST1", "John Doe", 15000.50, "Savings", "Verified"),
        ("ACC002", "CUST2", "Jane Smith", 2500.00, "Current", "Pending"),
        ("ACC003", "CUST3", "Mr VanDan", 75000.00, "Gold", "Verified"),
        ("ACC004", "CUST4", "Ravi Kumar", 52000.00, "Savings", "Verified"),
        ("ACC005", "CUST5", "Sara Ali", 98000.75, "Gold", "Verified"),
        ("ACC006", "CUST6", "Mohammed Faisal", 4300.00, "Current", "Pending"),
        ("ACC007", "CUST7", "Priya Singh", 64000.00, "Savings", "Verified"),
        ("ACC008", "CUST8", "Ahmed Hassan", 120000.00, "Gold", "Verified"),
        ("ACC009", "CUST9", "Lena George", 8000.25, "Savings", "Verified"),
        ("ACC010", "CUST10", "Rahul Mehta", 31000.00, "Current", "Pending"),
        ("ACC011", "CUST11", "Fatima Noor", 51000.00, "Savings", "Verified"),
        ("ACC012", "CUST12", "Kunal Shah", 220000.00, "Gold", "Verified"),
        ("ACC013", "CUST13", "Ayesha Khan", 47000.00, "Savings", "Pending"),
        ("ACC014", "CUST14", "Omar Saleh", 90000.00, "Current", "Verified"),
        ("ACC015", "CUST15", "Neha Jain", 56000.50, "Savings", "Verified"),
        ("ACC016", "CUST15", "Neha Jain", 1200.00, "Current", "Pending"),
        ("ACC017", "CUST16", "Sanjay Patel", 510000.00, "Gold", "Verified"),
        ("ACC018", "CUST17", "Meera Iyer", 45000.00, "Savings", "Verified"),
        ("ACC019", "CUST18", "Hassan Ali", 73000.00, "Current", "Verified"),
        ("ACC020", "CUST19", "Rashmi Rao", 250000.00, "Gold", "Verified"),
        ("ACC021", "CUST1", "John Doe", 120000.00, "Current", "Verified"),
        ("ACC022", "CUST1", "John Doe", 300000.00, "Gold", "Verified"),
    ]

    cursor.executemany(
        """
        INSERT OR REPLACE INTO accounts (
            account_id,
            customer_id,
            customer_name,
            balance,
            account_type,
            kyc_status
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        mock_data,
    )

    conn.commit()
    conn.close()

    print(f"Mock Banking Core Ready at {db_path.absolute()}")


if __name__ == "__main__":
    init_db()