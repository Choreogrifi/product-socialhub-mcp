"""FastMCP server — exposes SocialHub actions as MCP tools."""

from fastmcp import FastMCP

from socialhub_mcp.tools import accounts, posts, usage

mcp = FastMCP("SocialHub")


# ---------------------------------------------------------------------------
# Account tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def social_accounts_list() -> list[dict]:
    """List all connected social media accounts."""
    return await accounts.list_accounts()


# ---------------------------------------------------------------------------
# Post tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def social_post_create(
    platform: str,
    account_id: str,
    content: str,
    scheduled_at: str | None = None,
    media_urls: list[str] | None = None,
) -> dict:
    """Create a post draft.

    Args:
        platform: Target platform identifier (e.g. 'twitter', 'linkedin').
        account_id: Connected account UUID.
        content: Post body text.
        scheduled_at: Optional ISO 8601 datetime to auto-schedule on creation.
        media_urls: Optional list of media attachment URLs.
    """
    return await posts.create_post(
        platform=platform,
        account_id=account_id,
        content=content,
        scheduled_at=scheduled_at,
        media_urls=media_urls,
    )


@mcp.tool()
async def social_post_generate(
    platform: str,
    account_id: str,
    topic: str,
    additional_context: str | None = None,
) -> str:
    """Generate post content using AI. Returns the generated content string.

    Streams the AI-generated text from the SocialHub content-generation
    endpoint (SSE) and returns the full result as a single string.

    Args:
        platform: Target platform (e.g. 'twitter', 'instagram').
        account_id: Connected account UUID used to tailor tone/style.
        topic: Subject or prompt for the generated post.
        additional_context: Extra instructions or background for the AI.
    """
    return await posts.generate_post(
        platform=platform,
        account_id=account_id,
        topic=topic,
        additional_context=additional_context,
    )


@mcp.tool()
async def social_post_list(
    status: str | None = None,
    platform: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """List posts with optional filters.

    Args:
        status: Filter by post status ('draft', 'approved', 'scheduled',
                'published', 'cancelled').
        platform: Filter by platform identifier.
        limit: Maximum number of posts to return (default 20).
    """
    return await posts.list_posts(status=status, platform=platform, limit=limit)


@mcp.tool()
async def social_post_approve(post_id: str) -> dict:
    """Approve a post for publishing.

    Args:
        post_id: UUID of the post to approve.
    """
    return await posts.approve_post(post_id)


@mcp.tool()
async def social_post_schedule(post_id: str, scheduled_at: str) -> dict:
    """Schedule an approved post.

    Args:
        post_id: UUID of the post to schedule.
        scheduled_at: Publication datetime in ISO 8601 format
                      (e.g. '2026-04-10T14:00:00Z').
    """
    return await posts.schedule_post(post_id, scheduled_at)


@mcp.tool()
async def social_post_publish(post_id: str) -> dict:
    """Publish an approved post immediately.

    Args:
        post_id: UUID of the post to publish.
    """
    return await posts.publish_post(post_id)


@mcp.tool()
async def social_post_cancel(post_id: str) -> dict:
    """Cancel a scheduled post.

    Args:
        post_id: UUID of the scheduled post to cancel.
    """
    return await posts.cancel_post(post_id)


# ---------------------------------------------------------------------------
# Usage tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def social_usage_current() -> dict:
    """Get current subscription plan and usage statistics."""
    return await usage.current_usage()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
