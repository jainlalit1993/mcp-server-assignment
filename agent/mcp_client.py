"""GitHub access — through the GitHub MCP server ONLY.

Agents never call the GitHub REST API directly. They use the read-only tools the
MCP server exposes (get file contents, list repo tree, search code, get repo).
Tools are loaded once and cached for the process.
"""

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from . import config

# Cache the loaded tools so we don't reconnect on every node.
_TOOLS_CACHE: list[BaseTool] | None = None


def make_client() -> MultiServerMCPClient:
    """Build the MCP client. Default = remote GitHub MCP server over HTTP."""
    token = config.github_token()
    transport = config.github_mcp_transport()

    if transport == "stdio":
        # LOCAL ALTERNATIVE: run the official server with Docker over stdio.
        return MultiServerMCPClient(
            {
                "github": {
                    "transport": "stdio",
                    "command": "docker",
                    "args": [
                        "run", "-i", "--rm",
                        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
                        "ghcr.io/github/github-mcp-server",
                    ],
                    "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": token},
                }
            }
        )

    # DEFAULT: remote GitHub MCP server, read-only, minimal toolset.
    return MultiServerMCPClient(
        {
            "github": {
                "transport": "streamable_http",
                "url": config.github_mcp_url(),
                "headers": {
                    "Authorization": f"Bearer {token}",
                    "X-MCP-Readonly": "true",
                    "X-MCP-Toolsets": "repos",
                },
            }
        }
    )


async def get_github_tools() -> list[BaseTool]:
    """Load (and cache) the GitHub MCP tools."""
    global _TOOLS_CACHE
    if _TOOLS_CACHE is None:
        client = make_client()
        _TOOLS_CACHE = await client.get_tools()
    return _TOOLS_CACHE
