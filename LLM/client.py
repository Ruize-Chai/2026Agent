"""Lightweight LLM client wrapper for Oriflow.

Goals:
- Provide a small stable API that other parts (TUI, nodes, tests) can call.
- Support the `openai` backend. (The previous local `mock` backend has been removed.)
- Expose both sync and async methods.

The wrapper consults `Workflow.llm_config` for default credentials but allows
caller-provided overrides.
"""
from typing import Optional, Dict, Any
import asyncio
import os
import logging

# Logger for LLM client diagnostics
logger = logging.getLogger("oriflow.llm")
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("[LLM] %(levelname)s: %(message)s"))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)


class LLMClient:
    """A small LLM client wrapper.

    Args:
        backend: 'openai'
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

    def generate(self, prompt: str, model: str = "minimax/minimax-m2.5", max_tokens: int = 256, **kwargs: Any) -> str:
        """Synchronous generation helper.

        Returns generated text (string). Raises RuntimeError on misconfiguration.
        """
        # Automatically use requested minimax model if no official OpenAI endpoint is used
        if model in ["gpt-3.5-turbo", "qnas-v1"]:
            base = self.endpoint or os.environ.get("OPENAI_API_BASE") or ""
            if "openai.com" not in base:
                logger.info(f"Using requested model: minimax/minimax-m2.5")
                model = "minimax/minimax-m2.5"

        if self.backend == "openai":
            try:
                import openai
            except Exception as e:
                raise RuntimeError("openai package not available") from e

            creds = self._get_creds()
            try:
                creds_api_key = creds.get("api_key")
                creds_endpoint = creds.get("endpoint")
            except Exception:
                creds_api_key = None
                creds_endpoint = None

            # Ensure module-level credentials/env vars are set for compatibility
            try:
                if creds_api_key:
                    try:
                        setattr(openai, "api_key", creds_api_key)
                    except Exception:
                        pass
                    try:
                        os.environ["OPENAI_API_KEY"] = creds_api_key
                    except Exception:
                        pass
                if creds_endpoint:
                    try:
                        setattr(openai, "api_base", creds_endpoint)
                    except Exception:
                        pass
                    try:
                        os.environ["OPENAI_API_BASE"] = creds_endpoint
                    except Exception:
                        pass
            except Exception:
                pass

            # Attempt to use the new OpenAI client (openai>=1.0.0)
            OpenAIClass = getattr(openai, "OpenAI", None)
            if OpenAIClass is not None:
                logger.info("Detected openai.OpenAI (new client) available")
                # For openai>=1.0.0, we MUST pass credentials to the constructor to ensure 
                # they are recognized, especially when using custom endpoints.
                try:
                    # Sync credentials to variables for explicit passing
                    client_key = creds_api_key or os.environ.get("OPENAI_API_KEY")
                    client_base = creds_endpoint or os.environ.get("OPENAI_API_BASE")
                    if client_base:
                        client_base = client_base.rstrip("/")
                    
                    if client_key:
                        masked = f"{client_key[:4]}...{client_key[-4:]}" if len(client_key) > 8 else "***"
                        logger.info(f"Instantiating OpenAI client with key {masked} and base {client_base}")
                    
                    client = OpenAIClass(
                        api_key=client_key,
                        base_url=client_base
                    )
                except Exception:
                    logger.exception("Failed to instantiate OpenAI client; aborting new-client path")
                    client = None

                # Try Chat Completions via new client
                try:
                    messages = [{"role": "user", "content": prompt}]
                    logger.info("New client attributes: chat=%s, responses=%s", hasattr(client, "chat"), hasattr(client, "responses"))

                    if client is None:
                        raise RuntimeError("OpenAI client instance is None after instantiation")

                    if hasattr(client, "chat") and hasattr(client.chat, "completions"):
                        try:
                            resp = client.chat.completions.create(model=model, messages=messages, max_tokens=max_tokens, **kwargs)
                            logger.info("Used new client.chat.completions.create")
                        except Exception as e:
                            logger.exception("client.chat.completions.create failed: %s", e)
                            raise

                        try:
                            choice0 = resp.choices[0]
                            msg = getattr(choice0, "message", None)
                            if isinstance(msg, dict):
                                return msg.get("content", "") or ""
                            try:
                                return msg.content or ""
                            except Exception:
                                pass
                            return getattr(choice0, "text", "") or ""
                        except Exception:
                            logger.exception("Failed to extract content from chat completion response")
                            return ""

                    # Fallback: Responses API
                    if hasattr(client, "responses"):
                        try:
                            resp = client.responses.create(model=model, input=prompt, max_tokens=max_tokens, **kwargs)
                            logger.info("Used new client.responses.create")
                        except Exception as e:
                            logger.exception("client.responses.create failed: %s", e)
                            raise

                        try:
                            if getattr(resp, "output", None):
                                out = resp.output
                                if isinstance(out, (list, tuple)) and out:
                                    first = out[0]
                                    if isinstance(first, dict):
                                        cont = first.get("content")
                                        if isinstance(cont, list) and cont:
                                            c0 = cont[0]
                                            if isinstance(c0, dict):
                                                return c0.get("text", "") or ""
                                return str(resp)
                        except Exception:
                            logger.exception("Failed to extract content from responses API result")
                            return str(resp)

                except Exception as e:
                    # Log and attempt HTTP fallback to endpoint (bypass openai package)
                    logger.exception("New OpenAI client path failed: %s", e)
                    # If we have an api key and endpoint, try a direct HTTP call using httpx
                    try:
                        import httpx

                        api_key_for_http = creds_api_key or os.environ.get("OPENAI_API_KEY")
                        base = creds_endpoint or os.environ.get("OPENAI_API_BASE") or "https://api.openai.com"
                        base = base.rstrip("/")
                        
                        # Smart URL concatenation: don't double up /v1 or /chat/completions
                        if "/chat/completions" in base:
                            url = base
                        elif "/v1" in base:
                            url = base + "/chat/completions"
                        else:
                            url = base + "/v1/chat/completions"

                        headers = {"Authorization": f"Bearer {api_key_for_http}", "Content-Type": "application/json"}
                        body = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
                        logger.info("Attempting HTTP fallback to %s", url)
                        resp = httpx.post(url, json=body, headers=headers, timeout=30.0)
                        if resp.status_code >= 200 and resp.status_code < 300:
                            j = resp.json()
                            # try to extract text from chat completion shape
                            try:
                                if "choices" in j and isinstance(j["choices"], list) and j["choices"]:
                                    ch = j["choices"][0]
                                    # gpt responses may have message.content
                                    if "message" in ch and isinstance(ch["message"], dict):
                                        return ch["message"].get("content", "") or ""
                                    if "text" in ch:
                                        return ch.get("text", "") or ""
                                # fallback: try responses.output
                                if "output" in j:
                                    out = j["output"]
                                    if isinstance(out, list) and out:
                                        first = out[0]
                                        if isinstance(first, dict) and "content" in first:
                                            cont = first["content"]
                                            if isinstance(cont, list) and cont:
                                                c0 = cont[0]
                                                if isinstance(c0, dict) and "text" in c0:
                                                    return c0.get("text", "") or ""
                                return str(j)
                            except Exception:
                                return resp.text
                        else:
                            logger.error("HTTP fallback returned status %s: %s", resp.status_code, resp.text)
                    except Exception:
                        logger.exception("HTTP fallback also failed")
                    # re-raise the original exception to let caller know new-client path failed
                    raise

            # Legacy fallback: only attempt if the new OpenAIClass is not present
            if OpenAIClass is None:
                try:
                    if creds_api_key:
                        try:
                            setattr(openai, "api_key", creds_api_key)
                        except Exception:
                            pass
                    if creds_endpoint:
                        try:
                            setattr(openai, "api_base", creds_endpoint)
                        except Exception:
                            pass
                except Exception:
                    pass

                ChatCompletion = getattr(openai, "ChatCompletion", None)
                Completion = getattr(openai, "Completion", None)
                if ChatCompletion is not None:
                    logger.info("Using legacy openai.ChatCompletion API")
                if Completion is not None:
                    logger.info("Using legacy openai.Completion API")

                if ChatCompletion is not None:
                    messages = [{"role": "user", "content": prompt}]
                    resp = ChatCompletion.create(model=model, messages=messages, max_tokens=max_tokens, **kwargs)
                    if getattr(resp, "choices", None):
                        choice0 = resp.choices[0]
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

                raise RuntimeError("openai client is missing compatible legacy APIs (and no new OpenAI client present)")
            else:
                logger.error("Detected new openai.OpenAI client but new-client usage failed; not falling back to legacy APIs which are incompatible with openai>=1.0.0")
                raise RuntimeError("openai>=1.0.0 detected; ensure new client is usable or downgrade openai package")

        else:
            # Only `openai` backend is supported in this codebase.
            raise RuntimeError(f"unknown or unsupported backend: {self.backend}")

    async def generate_async(self, prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 256, **kwargs: Any) -> str:
        """Async wrapper around `generate`.

        Uses `asyncio.to_thread` so the sync openai client can be used safely.
        """
        return await asyncio.to_thread(self.generate, prompt, model, max_tokens, **kwargs)


def create_client(backend: str = "openai", api_key: Optional[str] = None, endpoint: Optional[str] = None) -> LLMClient:
    """Factory convenience to create an `LLMClient`."""
    return LLMClient(backend=backend, api_key=api_key, endpoint=endpoint)
