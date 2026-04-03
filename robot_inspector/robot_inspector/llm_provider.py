"""
Generic LLM provider abstraction for multi-backend vision analysis.

Supports: AWS Bedrock, OpenRouter, OpenAI-compatible (Ollama/DeepSeek), Anthropic API.

Usage:
    provider = create_provider("bedrock")  # or via LLM_PROVIDER env var
    response = provider.send_vision_message(image_bytes, "Analyze this image")
"""

import os
import json
import base64
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert industrial quality inspector. "
    "Analyze images carefully and provide structured, actionable feedback."
)


class LLMProvider(ABC):
    """Base class for LLM providers. All must support vision (image + text)."""

    @abstractmethod
    def send_vision_message(
        self,
        image_bytes: bytes,
        prompt: str,
        system_prompt: str = SYSTEM_PROMPT,
    ) -> str:
        """Send image + text prompt, return raw text response."""
        ...


class BedrockProvider(LLMProvider):
    """AWS Bedrock with Claude (uses boto3 converse API)."""

    def __init__(self, region_name: str = "us-east-1",
                 model_id: str = "us.anthropic.claude-opus-4-6-v1"):
        import boto3
        self.client = boto3.client("bedrock-runtime", region_name=region_name)
        self.model_id = model_id
        logger.info(f"BedrockProvider: region={region_name}, model={model_id}")

    def send_vision_message(self, image_bytes, prompt, system_prompt=SYSTEM_PROMPT):
        resp = self.client.converse(
            modelId=self.model_id,
            messages=[{
                "role": "user",
                "content": [
                    {"image": {"format": "png", "source": {"bytes": image_bytes}}},
                    {"text": prompt},
                ],
            }],
            system=[{"text": system_prompt}] if system_prompt else [],
        )
        return resp["output"]["message"]["content"][0]["text"]


class OpenAICompatibleProvider(LLMProvider):
    """OpenAI-compatible API. Works with OpenRouter, Ollama, DeepSeek, vLLM, etc."""

    def __init__(self, base_url: str, api_key: str = "", model: str = "gpt-4o"):
        import httpx
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.http = httpx.Client(timeout=120)
        logger.info(f"OpenAICompatibleProvider: url={self.base_url}, model={model}")

    def send_vision_message(self, image_bytes, prompt, system_prompt=SYSTEM_PROMPT):
        b64 = base64.b64encode(image_bytes).decode()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                {"type": "text", "text": prompt},
            ],
        })
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        resp = self.http.post(
            f"{self.base_url}/chat/completions",
            json={"model": self.model, "messages": messages, "max_tokens": 4096},
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


class AnthropicProvider(LLMProvider):
    """Direct Anthropic API (no AWS)."""

    def __init__(self, api_key: str = "", model: str = "claude-sonnet-4-20250514"):
        import httpx
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.model = model
        self.http = httpx.Client(timeout=120)
        logger.info(f"AnthropicProvider: model={model}")

    def send_vision_message(self, image_bytes, prompt, system_prompt=SYSTEM_PROMPT):
        b64 = base64.b64encode(image_bytes).decode()
        body = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "image", "source": {
                        "type": "base64", "media_type": "image/png", "data": b64}},
                    {"type": "text", "text": prompt},
                ],
            }],
        }
        if system_prompt:
            body["system"] = system_prompt

        resp = self.http.post(
            "https://api.anthropic.com/v1/messages",
            json=body,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]


def create_provider(provider_name: str = None, **kwargs) -> LLMProvider:
    """
    Factory function to create an LLM provider.

    Args:
        provider_name: One of 'bedrock', 'openrouter', 'openai', 'anthropic'.
                       Falls back to LLM_PROVIDER env var, then 'bedrock'.
        **kwargs: Provider-specific config (overrides env vars).

    Env vars per provider:
        bedrock:    BEDROCK_REGION, BEDROCK_MODEL_ID
        openrouter: OPENROUTER_API_KEY, OPENROUTER_MODEL
        openai:     OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL
        anthropic:  ANTHROPIC_API_KEY, ANTHROPIC_MODEL
    """
    name = (provider_name or os.environ.get("LLM_PROVIDER", "bedrock")).lower()

    if name == "bedrock":
        return BedrockProvider(
            region_name=kwargs.get("region_name", os.environ.get("BEDROCK_REGION", "us-east-1")),
            model_id=kwargs.get("model_id", os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-opus-4-6-v1")),
        )
    elif name == "openrouter":
        return OpenAICompatibleProvider(
            base_url="https://openrouter.ai/api/v1",
            api_key=kwargs.get("api_key", os.environ.get("OPENROUTER_API_KEY", "")),
            model=kwargs.get("model", os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")),
        )
    elif name == "openai":
        return OpenAICompatibleProvider(
            base_url=kwargs.get("base_url", os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1")),
            api_key=kwargs.get("api_key", os.environ.get("OPENAI_API_KEY", "")),
            model=kwargs.get("model", os.environ.get("OPENAI_MODEL", "deepseek-r1")),
        )
    elif name == "anthropic":
        return AnthropicProvider(
            api_key=kwargs.get("api_key", os.environ.get("ANTHROPIC_API_KEY", "")),
            model=kwargs.get("model", os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")),
        )
    else:
        raise ValueError(f"Unknown LLM provider: {name}. Use: bedrock, openrouter, openai, anthropic")
