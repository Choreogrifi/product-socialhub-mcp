"""Authenticated HTTP client for the SocialHub API."""

import os
from typing import Any

import httpx


class SocialHubClient:
    """Thin async HTTP client wrapping the SocialHub REST API."""

    def __init__(self) -> None:
        self.api_key = os.environ.get("SOCIALHUB_API_KEY")
        self.base_url = os.environ.get(
            "SOCIALHUB_API_URL", "https://api.socialhub.choreografii.com"
        ).rstrip("/")
        if not self.api_key:
            raise ValueError("SOCIALHUB_API_KEY environment variable is required")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    @staticmethod
    def _handle_response(response: httpx.Response) -> Any:
        """Return parsed JSON on success, or a structured error dict on failure."""
        try:
            response.raise_for_status()
            if response.content:
                return response.json()
            return {}
        except httpx.HTTPStatusError as exc:
            body: Any = {}
            try:
                body = exc.response.json()
            except Exception:
                body = exc.response.text
            return {
                "error": True,
                "status_code": exc.response.status_code,
                "detail": body,
            }
        except Exception as exc:  # network-level errors
            return {"error": True, "detail": str(exc)}

    # ------------------------------------------------------------------
    # Public HTTP verbs
    # ------------------------------------------------------------------

    async def get(self, path: str, params: dict | None = None) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self._url(path), headers=self._headers(), params=params or {}
            )
            return self._handle_response(response)

    async def post(self, path: str, json: dict | None = None) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._url(path), headers=self._headers(), json=json or {}
            )
            return self._handle_response(response)

    async def patch(self, path: str, json: dict | None = None) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                self._url(path), headers=self._headers(), json=json or {}
            )
            return self._handle_response(response)

    async def delete(self, path: str) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.delete(self._url(path), headers=self._headers())
            return self._handle_response(response)

    async def post_sse(self, path: str, json: dict | None = None) -> str:
        """POST to an SSE endpoint and collect the full text stream.

        Each Server-Sent Event line that begins with ``data:`` is accumulated.
        The final concatenated string is returned.
        """
        chunks: list[str] = []
        headers = {**self._headers(), "Accept": "text/event-stream"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST", self._url(path), headers=headers, json=json or {}
            ) as response:
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as exc:
                    body: Any = {}
                    try:
                        # Inside a streaming context the response body may not
                        # have been buffered yet — read it first.
                        await exc.response.aread()
                        body = exc.response.json()
                    except Exception:
                        try:
                            body = exc.response.text
                        except Exception:
                            body = str(exc)
                    return f"[error] status={exc.response.status_code} detail={body}"

                async for line in response.aiter_lines():
                    line = line.strip()
                    if line.startswith("data:"):
                        payload = line[len("data:"):].strip()
                        # Skip SSE control signals
                        if payload in ("[DONE]", ""):
                            continue
                        chunks.append(payload)

        return "".join(chunks)
