from __future__ import annotations
import os
import httpx
from typing import Any, Dict, Optional
from .models import RequestParams, ObservedResponse
from .parse_signals import parse_signals

class AzureOpenAIClient:
    """
    Minimal Azure OpenAI Chat Completions client via REST.
    """
    def __init__(self, endpoint: str, api_key: str, api_version: str, deployment: str):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.api_version = api_version
        self.deployment = deployment

    def chat_completions(self, prompt: str, params: RequestParams) -> ObservedResponse:
        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions"
        q = {"api-version": self.api_version}

        payload: Dict[str, Any] = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": params.temperature,
            "top_p": params.top_p,
            "max_tokens": params.max_output_tokens,
        }

        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=params.timeout_s) as client:
            r = client.post(url, params=q, headers=headers, json=payload)

        raw_json: Any = None
        content: Optional[str] = None
        finish_reason: Optional[str] = None
        error: Optional[str] = None

        try:
            raw_json = r.json()
        except Exception:
            raw_json = None

        if r.status_code >= 400:
            # try to capture Azure error payload
            error = (raw_json or {}).get("error", {}).get("message") if isinstance(raw_json, dict) else r.text
            signals = parse_signals(r.status_code, raw_json)
            return ObservedResponse(
                http_status=r.status_code,
                content=None,
                finish_reason=None,
                error=error,
                filter_signals=signals,
                headers=dict(r.headers),
                raw_json=raw_json,
            )

        # success payload
        if isinstance(raw_json, dict):
            try:
                choice0 = raw_json["choices"][0]
                finish_reason = choice0.get("finish_reason")
                msg = choice0.get("message", {})
                content = msg.get("content")
            except Exception:
                content = None

        signals = parse_signals(r.status_code, raw_json, finish_reason=finish_reason)
        return ObservedResponse(
            http_status=r.status_code,
            content=content,
            finish_reason=finish_reason,
            error=None,
            filter_signals=signals,
            headers=dict(r.headers),
            raw_json=raw_json,
        )
