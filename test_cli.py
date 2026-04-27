
from data_tools import get_account_details, identify_high_value_customers


def main():
    print("=== Agentic Banking PoC - CLI Test ===\n")

    # 1. Test account details
    print("Test 1: Get details for ACC003")
    print("--------------------------------")
    result_1 = get_account_details("ACC003")
    print(result_1)
    print("\n")

    # 2. Test account not found
    print("Test 2: Get details for ACC999 (non-existent)")
    print("---------------------------------------------")
    result_2 = get_account_details("ACC999")
    print(result_2)
    print("\n")

    # 3. Test high-value customers
    print("Test 3: Identify high-value customers (> 50,000)")
    print("-----------------------------------------------")
    result_3 = identify_high_value_customers(50000.0)
    print(result_3)
    print("\n")


if __name__ == "__main__":
    main()