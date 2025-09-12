"""CheerLights MCP Server - A Model Context Protocol server for CheerLights API."""

__version__ = "2.0.0"
__author__ = "CheerLights Community"
__description__ = "A Model Context Protocol (MCP) server for interacting with CheerLights API"

from .server import create_server

__all__ = ["create_server", "__version__"]
