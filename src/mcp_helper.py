"""Utility functions for interacting with Antigravity MCP.

Provides a thin wrapper around `antigravity.mcp.run` so the rest of the
project can call external services without dealing with the low‑level
API.
"""
import os
try:
    from antigravity.mcp import run as mcp_run
except ImportError:
    # Fallback for local development without Antigravity environment
    def mcp_run(*args, **kwargs):
        print(f"[MOCK] MCP run called with: args={args}, kwargs={kwargs}")
        return []

# Load MCP key from environment – Antigravity expects the key to be set
# in the `ANTIGRAVITY_MCP_KEY` variable.
MCP_KEY = os.getenv("ANTIGRAVITY_MCP_KEY")

def github_repo_list(org: str):
    """Return a list of repositories for a GitHub organization via MCP."""
    return mcp_run(
        service="github",
        command="repo",
        action="list",
        org=org,
    )

def github_issue_list(repo: str, state: str = "open"):
    """Return open issues for a given repository via MCP."""
    return mcp_run(
        service="github",
        command="issues",
        action="list",
        repo=repo,
        state=state,
    )
