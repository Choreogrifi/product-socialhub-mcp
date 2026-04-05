"""Tools for managing connected social media accounts."""

from socialhub_mcp.client import SocialHubClient


async def list_accounts() -> list[dict]:
    """Return all connected social media accounts."""
    client = SocialHubClient()
    result = await client.get("/api/v1/accounts")
    if isinstance(result, list):
        return result
    # API may wrap in a top-level key
    if isinstance(result, dict):
        if result.get("error"):
            return [result]
        return result.get("accounts", result.get("data", [result]))
    return []
