from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol


@dataclass(frozen=True)
class ToolRequest:
    """A proposed tool invocation from the control plane."""
    tool_name: str
    params: Dict[str, Any]


@dataclass(frozen=True)
class ToolResult:
    """Structured result returned by the executor."""
    tool_name: str
    ok: bool
    data: Dict[str, Any]
    error: str | None = None


class Tool(Protocol):
    name: str
    description: str
    param_schema: Dict[str, type]
    required_params: List[str]

    def run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with validated params."""


class ToolRegistry:
    """Explicit registry for tools; no dynamic loading."""

    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")
        return self._tools[name]

    def list_tools(self) -> List[str]:
        return sorted(self._tools.keys())


class ToolExecutor:
    """Validates tool requests and executes registered tools safely."""

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def execute(self, request: ToolRequest) -> ToolResult:
        try:
            tool = self._registry.get_tool(request.tool_name)
        except KeyError as exc:
            return ToolResult(tool_name=request.tool_name, ok=False, data={}, error=str(exc))

        validation_error = self._validate_params(tool, request.params)
        if validation_error:
            return ToolResult(tool_name=tool.name, ok=False, data={}, error=validation_error)

        try:
            output = tool.run(request.params)
            return ToolResult(tool_name=tool.name, ok=True, data=output)
        except Exception as exc:  # noqa: BLE001 - surface tool errors as data
            return ToolResult(tool_name=tool.name, ok=False, data={}, error=str(exc))

    def _validate_params(self, tool: Tool, params: Dict[str, Any]) -> str | None:
        # Ensure only declared parameters are accepted.
        for key in params:
            if key not in tool.param_schema:
                return f"Unexpected parameter: {key}"

        # Ensure all required parameters are present.
        for key in tool.required_params:
            if key not in params:
                return f"Missing required parameter: {key}"

        # Type-check provided parameters.
        for key, value in params.items():
            expected_type = tool.param_schema[key]
            if not isinstance(value, expected_type):
                return f"Invalid type for {key}: expected {expected_type.__name__}"

        return None


class MockSQLTool:
    name = "mock_sql"
    description = "Execute a predefined SQL query against a mock database."
    param_schema = {
        "query": str,
        "limit": int,
    }
    required_params = ["query"]

    def run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder execution; no real SQL parsing or DB access.
        query = params["query"]
        limit = params.get("limit", 10)
        return {
            "rows": [
                {"id": 1, "value": "alpha"},
                {"id": 2, "value": "beta"},
            ][:limit],
            "query": query,
        }


class MockVectorSearchTool:
    name = "mock_vector_search"
    description = "Run a mock vector similarity search against a corpus."
    param_schema = {
        "embedding": list,
        "top_k": int,
    }
    required_params = ["embedding"]

    def run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder execution; no real vector math.
        top_k = params.get("top_k", 3)
        return {
            "matches": [
                {"doc_id": "doc-1", "score": 0.92},
                {"doc_id": "doc-2", "score": 0.87},
                {"doc_id": "doc-3", "score": 0.81},
            ][:top_k],
        }


if __name__ == "__main__":
    registry = ToolRegistry()
    registry.register_tool(MockSQLTool())
    registry.register_tool(MockVectorSearchTool())

    executor = ToolExecutor(registry)

    sql_request = ToolRequest(tool_name="mock_sql", params={"query": "SELECT * FROM t", "limit": 1})
    print(executor.execute(sql_request))

    vs_request = ToolRequest(tool_name="mock_vector_search", params={"embedding": [0.1, 0.2], "top_k": 2})
    print(executor.execute(vs_request))
