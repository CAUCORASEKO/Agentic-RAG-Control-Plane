from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ToolResult:
    tool_name: str
    output: str
    success: bool
    metadata: Optional[Dict[str, Any]] = None


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, params: Optional[dict] = None) -> ToolResult:
        """Execute the tool and return a structured result."""


class ToolRegistry:
    """Explicit allowlist of tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, tool_name: str) -> BaseTool:
        if tool_name not in self._tools:
            raise KeyError(f"Tool not registered: {tool_name}")
        return self._tools[tool_name]

    def list_tools(self) -> List[str]:
        return sorted(self._tools.keys())


class ToolExecutor:
    """Executes tools from an explicit registry only."""

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def execute(self, tool_name: str, params: Optional[dict] = None) -> ToolResult:
        try:
            tool = self._registry.get(tool_name)
            result = tool.run(params)
        except Exception as exc:  # noqa: BLE001 - surface tool errors as data
            return ToolResult(
                tool_name=tool_name,
                output="",
                success=False,
                metadata={"error": str(exc)},
            )

        if result.tool_name != tool_name:
            return ToolResult(
                tool_name=tool_name,
                output="",
                success=False,
                metadata={"error": "Tool name mismatch in result"},
            )

        return result


class MockSQLTool(BaseTool):
    name = "mock_sql"
    description = "Simulate a safe, predefined SQL query execution."

    def run(self, params: Optional[dict] = None) -> ToolResult:
        # No SQL parsing or DB access.
        return ToolResult(
            tool_name=self.name,
            output="rows=2",
            success=True,
            metadata={"rows": [{"id": 1}, {"id": 2}]},
        )


class MockVectorSearchTool(BaseTool):
    name = "mock_vector_search"
    description = "Simulate a vector similarity search."

    def run(self, params: Optional[dict] = None) -> ToolResult:
        # No embeddings or vector math.
        return ToolResult(
            tool_name=self.name,
            output="matches=2",
            success=True,
            metadata={"matches": [{"doc_id": "doc-1"}, {"doc_id": "doc-2"}]},
        )


if __name__ == "__main__":
    registry = ToolRegistry()
    registry.register(MockSQLTool())
    registry.register(MockVectorSearchTool())

    executor = ToolExecutor(registry)
    print(executor.execute("mock_sql"))
    print(executor.execute("mock_vector_search"))
