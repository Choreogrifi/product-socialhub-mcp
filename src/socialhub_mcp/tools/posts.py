"""Tools for creating and managing social media posts."""

from typing import Any

from socialhub_mcp.client import SocialHubClient


async def create_post(
    platform: str,
    account_id: str,
    content: str,
    scheduled_at: str | None = None,
    media_urls: list[str] | None = None,
) -> dict:
    """Create a new post draft via the SocialHub API."""
    client = SocialHubClient()
    payload: dict[str, Any] = {
        "platform": platform,
        "account_id": account_id,
        "content": content,
    }
    if scheduled_at is not None:
        payload["scheduled_at"] = scheduled_at
    if media_urls:
        payload["media_urls"] = media_urls
    return await client.post("/api/v1/posts", json=payload)


async def generate_post(
    platform: str,
    account_id: str,
    topic: str,
    additional_context: str | None = None,
) -> str:
    """Call the AI content-generation endpoint (SSE) and return the generated text."""
    client = SocialHubClient()
    payload: dict[str, Any] = {
        "platform": platform,
        "account_id": account_id,
        "topic": topic,
    }
    if additional_context is not None:
        payload["additional_context"] = additional_context
    return await client.post_sse("/api/v1/content/generate", json=payload)


async def list_posts(
    status: str | None = None,
    platform: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """List posts, optionally filtered by status and/or platform."""
    client = SocialHubClient()
    params: dict[str, Any] = {"limit": limit}
    if status is not None:
        params["status"] = status
    if platform is not None:
        params["platform"] = platform
    result = await client.get("/api/v1/posts", params=params)
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        if result.get("error"):
            return [result]
        return result.get("posts", result.get("data", [result]))
    return []


async def approve_post(post_id: str) -> dict:
    """Approve a post so it can be scheduled or published."""
    client = SocialHubClient()
    return await client.patch(f"/api/v1/posts/{post_id}/approve")


async def schedule_post(post_id: str, scheduled_at: str) -> dict:
    """Schedule an approved post for a specific time (ISO 8601)."""
    client = SocialHubClient()
    return await client.patch(
        f"/api/v1/posts/{post_id}/schedule",
        json={"scheduled_at": scheduled_at},
    )


async def publish_post(post_id: str) -> dict:
    """Publish an approved post immediately."""
    client = SocialHubClient()
    return await client.post(f"/api/v1/posts/{post_id}/publish")


async def cancel_post(post_id: str) -> dict:
    """Cancel a scheduled post."""
    client = SocialHubClient()
    return await client.patch(f"/api/v1/posts/{post_id}/cancel")
