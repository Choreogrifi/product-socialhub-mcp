"""Tools for retrieving subscription and usage information."""

from socialhub_mcp.client import SocialHubClient


async def current_usage() -> dict:
    """Return the current plan details and usage statistics."""
    client = SocialHubClient()
    result = await client.get("/api/v1/usage")
    if isinstance(result, dict):
        return result
    return {"data": result}
