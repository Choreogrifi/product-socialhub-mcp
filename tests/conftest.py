"""Shared test fixtures for socialhub-mcp."""

import os

import pytest
import respx


# ---------------------------------------------------------------------------
# Ensure env vars are always set before any import of SocialHubClient
# ---------------------------------------------------------------------------

os.environ.setdefault("SOCIALHUB_API_KEY", "sk_test_fake")
os.environ.setdefault("SOCIALHUB_API_URL", "https://api.socialhub.choreografii.com")

BASE = "https://api.socialhub.choreografii.com"


@pytest.fixture
def mock_api():
    """Activate a respx router that intercepts all httpx calls to the SocialHub API."""
    with respx.mock(base_url=BASE, assert_all_called=False) as router:
        yield router


# ---------------------------------------------------------------------------
# Sample payload fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_account():
    return {
        "id": "acc_001",
        "platform": "twitter",
        "username": "@choreografii",
        "status": "connected",
    }


@pytest.fixture
def sample_post():
    return {
        "id": "post_001",
        "platform": "twitter",
        "account_id": "acc_001",
        "content": "Hello world!",
        "status": "draft",
        "created_at": "2026-04-04T10:00:00Z",
    }


@pytest.fixture
def sample_usage():
    return {
        "plan": "pro",
        "posts_used": 42,
        "posts_limit": 500,
        "billing_period_end": "2026-04-30T23:59:59Z",
    }
