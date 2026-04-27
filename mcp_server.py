from typing import Dict, List

from mcp.server.fastmcp import FastMCP
#
#from data_tools import (
#    get_account_details_structured,
#    identify_high_value_customers_structured,
#)


from data_tools import (
    get_account_details_structured,
    identify_high_value_customers_structured,
    get_customer_portfolio_structured,
    list_customer_portfolios_above_threshold,
)


# Initialize the MCP server
mcp = FastMCP("AgenticBankingGateway")


@mcp.tool(
    annotations={
        "title": "Get Account Details",
        "description": "Fetch full account details for a given account_id.",
        "readOnlyHint": True,
    }
)
def mcp_get_account_details(account_id: str) -> Dict[str, object]:
    """
    MCP tool: returns structured account details.
    """
    details = get_account_details_structured(account_id)
    if not details:
        return {"status": "NOT_FOUND", "account_id": account_id}
    return {"status": "FOUND", **details}


@mcp.tool(
    annotations={
        "title": "List High-Value Customers",
        "description": "Return masked high-value customers above the given threshold.",
        "readOnlyHint": True,
    }
)

#--- new added
@mcp.tool(
    annotations={
        "title": "Get Customer Portfolio",
        "description": "Return all accounts and total balance for a given customer_name.",
        "readOnlyHint": True,
    }
)
def mcp_get_customer_portfolio(customer_name: str) -> Dict[str, object]:
    """
    MCP tool: returns a customer's portfolio view.
    """
    return get_customer_portfolio_structured(customer_name)


@mcp.tool(
    annotations={
        "title": "List Top Customers by Portfolio",
        "description": "Return customers whose total portfolio exceeds the given threshold.",
        "readOnlyHint": True,
    }
)
def mcp_list_top_customers(threshold: float = 100000.0) -> Dict[str, object]:
    """
    MCP tool: returns customers with portfolio balances above threshold.
    """
    customers = list_customer_portfolios_above_threshold(threshold)
    return {"threshold": threshold, "count": len(customers), "customers": customers}

#--- new added end 


def mcp_list_high_value_customers(threshold: float = 50000.0) -> Dict[str, object]:
    """
    MCP tool: returns masked high-value customers and threshold used.
    """
    customers: List[Dict[str, object]] = identify_high_value_customers_structured(
        threshold
    )
    return {
        "threshold": threshold,
        "count": len(customers),
        "customers": customers,
    }


def main() -> None:
    """
    Entry point for the MCP server.
    """
    mcp.run()


if __name__ == "__main__":
    main()