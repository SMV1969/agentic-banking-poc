"""
Headless test client for the Agentic Banking PoC.

This script calls the same structured tool functions that are exposed
via the MCP server. It is useful for validating logic without the UI.
"""

from pprint import pprint

from data_tools import (
    get_account_details_structured,
    identify_high_value_customers_structured,
)


def test_account_details():
    print("=== Test: Account details ===")
    acc_id = "ACC003"
    result = get_account_details_structured(acc_id)
    if not result:
        print(f"Account {acc_id} not found.")
    else:
        pprint(result)
    print()


def test_high_value_customers():
    print("=== Test: High-value customers ===")
    threshold = 50000.0
    result = identify_high_value_customers_structured(threshold)
    print(f"Threshold: {threshold}")
    print(f"Count: {len(result)}")
    pprint(result)
    print()


def main():
    test_account_details()
    test_high_value_customers()


if __name__ == "__main__":
    main()