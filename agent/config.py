"""Environment + model configuration.

Everything is read lazily (inside functions) so importing the package never
requires secrets. Keys are only needed when a node actually runs.
"""

import os

from dotenv import load_dotenv

# Load a local .env if present (no-op in production where env vars are set directly).
load_dotenv()


def openai_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set. Add it to your .env file.")
    return key


def github_token() -> str:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set. Add it to your .env file.")
    return token


def fast_model() -> str:
    return os.environ.get("FAST_MODEL", "gpt-4o-mini")


def smart_model() -> str:
    return os.environ.get("SMART_MODEL", "gpt-4o")


def github_mcp_url() -> str:
    return os.environ.get("GITHUB_MCP_URL", "https://api.githubcopilot.com/mcp/")


def github_mcp_transport() -> str:
    # "streamable_http" (remote, default) or "stdio" (local Docker server).
    return os.environ.get("GITHUB_MCP_TRANSPORT", "streamable_http")
