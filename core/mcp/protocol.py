from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
import json

@dataclass
class MCPContext:
    """
    Standard Context object for MCP requests.
    Carries execution environment details.
    """
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    language: str = "en"
    platform: str = "win32"

@dataclass
class MCPRequest:
    """
    Standard Request object following JSON-RPC style.
    """
    method: str
    params: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None
    context: Optional[MCPContext] = None

    def to_json(self):
        return json.dumps(asdict(self))

@dataclass
class MCPResponse:
    """
    Standard Response object.
    """
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

    def to_json(self):
        return json.dumps(asdict(self))

@dataclass
class MCPResource:
    """
    Represents a resource (like a file template) available to the system.
    """
    uri: str
    name: str
    mimeType: str = "text/markdown"
    content: Optional[str] = None
