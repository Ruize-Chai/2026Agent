"""Lightweight LLM client wrapper for Oriflow.

Goals:
- Provide a small stable API that other parts (TUI, nodes, tests) can call.
- Support multiple backends (currently `openai` and a local `mock`).
- Expose both sync and async methods.

The wrapper consults `Workflow.llm_config` for default credentials but allows
caller-provided overrides.
"""
from typing import Optional, Dict, Any
import asyncio


class LLMClient:
    """A small LLM client wrapper.

    Args:
        backend: 'openai' or 'mock'
        api_key: optional API key override
        endpoint: optional API base/endpoint override
    """

    def __init__(self, backend: str = "openai", api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.backend = backend
        self.api_key = api_key
        self.endpoint = endpoint

    def _get_creds(self) -> Dict[str, Optional[str]]:
        if self.api_key is not None or self.endpoint is not None:
            return {"api_key": self.api_key, "endpoint": self.endpoint}
        try:
            from Workflow.llm_config import get_llm_api

            return get_llm_api()
        except Exception:
            return {"api_key": None, "endpoint": None}

    def generate(self, prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 256, **kwargs: Any) -> str:
        """Synchronous generation helper.

        Returns generated text (string). Raises RuntimeError on misconfiguration.
        """
        if self.backend == "openai":
            try:
                import openai
            except Exception as e:
                raise RuntimeError("openai package not available") from e

            creds = self._get_creds()
            if creds.get("api_key"):
                try:
                    setattr(openai, "api_key", creds.get("api_key"))
                except Exception:
                    pass
            if creds.get("endpoint"):
                try:
                    setattr(openai, "api_base", creds.get("endpoint"))
                except Exception:
                    pass

            # Prefer ChatCompletion when available for chat-models
            ChatCompletion = getattr(openai, "ChatCompletion", None)
            Completion = getattr(openai, "Completion", None)

            if ChatCompletion is not None:
                messages = [{"role": "user", "content": prompt}]
                resp = ChatCompletion.create(model=model, messages=messages, max_tokens=max_tokens, **kwargs)
                if getattr(resp, "choices", None):
                    choice0 = resp.choices[0]
                    # choice0 may expose message (dict-like) or text
                    try:
                        return choice0.message.get("content") or getattr(choice0, "text", "")
                    except Exception:
                        return getattr(choice0, "text", "") or ""
                return ""

            if Completion is not None:
                resp = Completion.create(model=model, prompt=prompt, max_tokens=max_tokens, **kwargs)
                if getattr(resp, "choices", None):
                    return getattr(resp.choices[0], "text", "") or ""
                return ""

            raise RuntimeError("openai client is missing Completion/ChatCompletion APIs")

        elif self.backend == "mock":
            # Simple deterministic mock useful for tests and offline dev
            return f"[mock]{prompt[:200]}"

        else:
            raise RuntimeError(f"unknown backend: {self.backend}")

    async def generate_async(self, prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 256, **kwargs: Any) -> str:
        """Async wrapper around `generate`.

        Uses `asyncio.to_thread` so the sync openai client can be used safely.
        """
        return await asyncio.to_thread(self.generate, prompt, model, max_tokens, **kwargs)


def create_client(backend: str = "openai", api_key: Optional[str] = None, endpoint: Optional[str] = None) -> LLMClient:
    """Factory convenience to create an `LLMClient`."""
    return LLMClient(backend=backend, api_key=api_key, endpoint=endpoint)
