"""Oriflow LLM wrapper package.

Exports:
- `LLMClient`: simple client wrapper supporting sync/async calls and multiple backends.
- `create_client`: convenience factory.
- re-exports Workflow.llm_config helpers: `set_llm_api`, `get_llm_api`, `clear_llm_api`.

This module is small and intentionally framework-agnostic so the TUI or other
parts of the system can import a single stable API for invoking language models.
"""
from .client import LLMClient, create_client

from Workflow.llm_config import set_llm_api, get_llm_api, clear_llm_api

__all__ = [
    "LLMClient",
    "create_client",
    "set_llm_api",
    "get_llm_api",
    "clear_llm_api",
]
