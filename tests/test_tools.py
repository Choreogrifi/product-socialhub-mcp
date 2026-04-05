"""Integration-style tests for every MCP tool using mocked HTTP responses."""

import httpx
import pytest
import respx

from socialhub_mcp.tools import accounts, posts, usage

BASE = "https://api.socialhub.choreografii.com"


# ===========================================================================
# Accounts
# ===========================================================================


@pytest.mark.asyncio
async def test_list_accounts_returns_list(mock_api, sample_account):
    mock_api.get("/api/v1/accounts").mock(
        return_value=httpx.Response(200, json=[sample_account])
    )
    result = await accounts.list_accounts()
    assert isinstance(result, list)
    assert result[0]["id"] == "acc_001"


@pytest.mark.asyncio
async def test_list_accounts_wrapped_response(mock_api, sample_account):
    """API may return {'accounts': [...]} — client should unwrap it."""
    mock_api.get("/api/v1/accounts").mock(
        return_value=httpx.Response(200, json={"accounts": [sample_account]})
    )
    result = await accounts.list_accounts()
    assert result[0]["platform"] == "twitter"


@pytest.mark.asyncio
async def test_list_accounts_api_error(mock_api):
    mock_api.get("/api/v1/accounts").mock(
        return_value=httpx.Response(401, json={"message": "Unauthorized"})
    )
    result = await accounts.list_accounts()
    assert result[0].get("error") is True
    assert result[0]["status_code"] == 401


# ===========================================================================
# Posts — create
# ===========================================================================


@pytest.mark.asyncio
async def test_create_post_minimal(mock_api, sample_post):
    mock_api.post("/api/v1/posts").mock(
        return_value=httpx.Response(201, json=sample_post)
    )
    result = await posts.create_post(
        platform="twitter", account_id="acc_001", content="Hello world!"
    )
    assert result["id"] == "post_001"
    assert result["status"] == "draft"


@pytest.mark.asyncio
async def test_create_post_with_schedule_and_media(mock_api, sample_post):
    enriched = {**sample_post, "scheduled_at": "2026-04-10T14:00:00Z", "media_urls": ["https://img.example.com/photo.jpg"]}
    mock_api.post("/api/v1/posts").mock(
        return_value=httpx.Response(201, json=enriched)
    )
    result = await posts.create_post(
        platform="twitter",
        account_id="acc_001",
        content="Look at this!",
        scheduled_at="2026-04-10T14:00:00Z",
        media_urls=["https://img.example.com/photo.jpg"],
    )
    assert result["scheduled_at"] == "2026-04-10T14:00:00Z"
    assert result["media_urls"][0].endswith("photo.jpg")


@pytest.mark.asyncio
async def test_create_post_api_error(mock_api):
    mock_api.post("/api/v1/posts").mock(
        return_value=httpx.Response(422, json={"message": "Validation error"})
    )
    result = await posts.create_post(
        platform="twitter", account_id="acc_001", content=""
    )
    assert result.get("error") is True
    assert result["status_code"] == 422


# ===========================================================================
# Posts — list
# ===========================================================================


@pytest.mark.asyncio
async def test_list_posts_no_filter(mock_api, sample_post):
    mock_api.get("/api/v1/posts").mock(
        return_value=httpx.Response(200, json=[sample_post])
    )
    result = await posts.list_posts()
    assert len(result) == 1
    assert result[0]["id"] == "post_001"


@pytest.mark.asyncio
async def test_list_posts_with_filters(mock_api, sample_post):
    mock_api.get("/api/v1/posts").mock(
        return_value=httpx.Response(200, json={"posts": [sample_post]})
    )
    result = await posts.list_posts(status="draft", platform="twitter", limit=5)
    assert result[0]["status"] == "draft"


@pytest.mark.asyncio
async def test_list_posts_empty(mock_api):
    mock_api.get("/api/v1/posts").mock(
        return_value=httpx.Response(200, json=[])
    )
    result = await posts.list_posts()
    assert result == []


# ===========================================================================
# Posts — approve
# ===========================================================================


@pytest.mark.asyncio
async def test_approve_post(mock_api, sample_post):
    approved = {**sample_post, "status": "approved"}
    mock_api.patch("/api/v1/posts/post_001/approve").mock(
        return_value=httpx.Response(200, json=approved)
    )
    result = await posts.approve_post("post_001")
    assert result["status"] == "approved"


@pytest.mark.asyncio
async def test_approve_post_not_found(mock_api):
    mock_api.patch("/api/v1/posts/bad_id/approve").mock(
        return_value=httpx.Response(404, json={"message": "Not found"})
    )
    result = await posts.approve_post("bad_id")
    assert result.get("error") is True
    assert result["status_code"] == 404


# ===========================================================================
# Posts — schedule
# ===========================================================================


@pytest.mark.asyncio
async def test_schedule_post(mock_api, sample_post):
    scheduled = {**sample_post, "status": "scheduled", "scheduled_at": "2026-04-10T14:00:00Z"}
    mock_api.patch("/api/v1/posts/post_001/schedule").mock(
        return_value=httpx.Response(200, json=scheduled)
    )
    result = await posts.schedule_post("post_001", "2026-04-10T14:00:00Z")
    assert result["status"] == "scheduled"
    assert result["scheduled_at"] == "2026-04-10T14:00:00Z"


# ===========================================================================
# Posts — publish
# ===========================================================================


@pytest.mark.asyncio
async def test_publish_post(mock_api, sample_post):
    published = {**sample_post, "status": "published"}
    mock_api.post("/api/v1/posts/post_001/publish").mock(
        return_value=httpx.Response(200, json=published)
    )
    result = await posts.publish_post("post_001")
    assert result["status"] == "published"


# ===========================================================================
# Posts — cancel
# ===========================================================================


@pytest.mark.asyncio
async def test_cancel_post(mock_api, sample_post):
    cancelled = {**sample_post, "status": "cancelled"}
    mock_api.patch("/api/v1/posts/post_001/cancel").mock(
        return_value=httpx.Response(200, json=cancelled)
    )
    result = await posts.cancel_post("post_001")
    assert result["status"] == "cancelled"


# ===========================================================================
# Posts — AI generation (SSE)
# ===========================================================================


@pytest.mark.asyncio
async def test_generate_post_sse(mock_api):
    """SSE stream should be collected and returned as a single string."""
    sse_body = (
        "data: Hello\n\n"
        "data:  from\n\n"
        "data:  AI!\n\n"
        "data: [DONE]\n\n"
    )
    mock_api.post("/api/v1/content/generate").mock(
        return_value=httpx.Response(
            200,
            content=sse_body.encode(),
            headers={"Content-Type": "text/event-stream"},
        )
    )
    result = await posts.generate_post(
        platform="twitter",
        account_id="acc_001",
        topic="spring product launch",
    )
    assert "Hello" in result
    assert "AI!" in result
    assert "[DONE]" not in result


@pytest.mark.asyncio
async def test_generate_post_with_context(mock_api):
    sse_body = "data: Generated with context\n\ndata: [DONE]\n\n"
    mock_api.post("/api/v1/content/generate").mock(
        return_value=httpx.Response(
            200,
            content=sse_body.encode(),
            headers={"Content-Type": "text/event-stream"},
        )
    )
    result = await posts.generate_post(
        platform="linkedin",
        account_id="acc_002",
        topic="AI trends",
        additional_context="Focus on enterprise adoption",
    )
    assert "Generated with context" in result


@pytest.mark.asyncio
async def test_generate_post_api_error(mock_api):
    mock_api.post("/api/v1/content/generate").mock(
        return_value=httpx.Response(403, json={"message": "Forbidden"})
    )
    result = await posts.generate_post(
        platform="twitter", account_id="acc_001", topic="test"
    )
    assert "[error]" in result
    assert "403" in result


# ===========================================================================
# Usage
# ===========================================================================


@pytest.mark.asyncio
async def test_current_usage(mock_api, sample_usage):
    mock_api.get("/api/v1/usage").mock(
        return_value=httpx.Response(200, json=sample_usage)
    )
    result = await usage.current_usage()
    assert result["plan"] == "pro"
    assert result["posts_used"] == 42
    assert result["posts_limit"] == 500


@pytest.mark.asyncio
async def test_current_usage_api_error(mock_api):
    mock_api.get("/api/v1/usage").mock(
        return_value=httpx.Response(500, json={"message": "Internal Server Error"})
    )
    result = await usage.current_usage()
    assert result.get("error") is True
    assert result["status_code"] == 500


# ===========================================================================
# Client — SocialHubClient unit tests
# ===========================================================================


def test_client_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("SOCIALHUB_API_KEY", raising=False)
    from socialhub_mcp.client import SocialHubClient
    with pytest.raises(ValueError, match="SOCIALHUB_API_KEY"):
        SocialHubClient()


def test_client_uses_custom_base_url(monkeypatch):
    monkeypatch.setenv("SOCIALHUB_API_KEY", "sk_test_x")
    monkeypatch.setenv("SOCIALHUB_API_URL", "https://staging.example.com")
    from socialhub_mcp.client import SocialHubClient
    client = SocialHubClient()
    assert client.base_url == "https://staging.example.com"


def test_client_default_base_url(monkeypatch):
    monkeypatch.setenv("SOCIALHUB_API_KEY", "sk_test_x")
    monkeypatch.delenv("SOCIALHUB_API_URL", raising=False)
    from socialhub_mcp.client import SocialHubClient
    client = SocialHubClient()
    assert client.base_url == "https://api.socialhub.choreografii.com"


def test_client_headers_contain_bearer(monkeypatch):
    monkeypatch.setenv("SOCIALHUB_API_KEY", "sk_test_xyz")
    from socialhub_mcp.client import SocialHubClient
    client = SocialHubClient()
    headers = client._headers()
    assert headers["Authorization"] == "Bearer sk_test_xyz"
    assert headers["Content-Type"] == "application/json"
