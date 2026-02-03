from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


@dataclass
class AgentContext:
    # The user-provided query or task description.
    user_query: str
    # Interpreted intent of the user query (placeholder for future LLM use).
    intent: Optional[str] = None
    # Planned tool names in execution order.
    planned_tools: List[str] = field(default_factory=list)
    # Results from executed tools.
    tool_results: List[str] = field(default_factory=list)
    # Evaluation of whether results satisfy the intent.
    evaluation: Optional[str] = None
    # Number of tool execution retries attempted.
    retries: int = 0
    # Maximum number of retries before giving up.
    max_retries: int = 1


class AgentState(Enum):
    # ENTRY: Initialize run and validate inputs.
    ENTRY = "ENTRY"
    # PLAN: Determine intent and tool plan (placeholder).
    PLAN = "PLAN"
    # EXECUTE_TOOL: Execute next planned tool (placeholder).
    EXECUTE_TOOL = "EXECUTE_TOOL"
    # EVALUATE: Judge tool results against the intent.
    EVALUATE = "EVALUATE"
    # REFLECT: Decide whether to retry, replan, or finalize.
    REFLECT = "REFLECT"
    # GENERATE: Produce a response (placeholder).
    GENERATE = "GENERATE"
    # END: Terminal state.
    END = "END"


class AgentController:
    def __init__(self, context: AgentContext) -> None:
        self.context = context
        self.state = AgentState.ENTRY

    def run(self) -> AgentContext:
        """Run the explicit state machine to completion."""
        while self.state != AgentState.END:
            self._step()
            self.state = self._transition()
        return self.context

    def _step(self) -> None:
        if self.state == AgentState.ENTRY:
            self._entry()
            return
        if self.state == AgentState.PLAN:
            self._plan()
            return
        if self.state == AgentState.EXECUTE_TOOL:
            self._execute_tool()
            return
        if self.state == AgentState.EVALUATE:
            self._evaluate()
            return
        if self.state == AgentState.REFLECT:
            self._reflect()
            return
        if self.state == AgentState.GENERATE:
            self._generate()
            return
        if self.state == AgentState.END:
            return
        raise ValueError(f"Unknown state: {self.state}")

    def _transition(self) -> AgentState:
        # Deterministic transitions; no LLM calls are made.
        if self.state == AgentState.ENTRY:
            return AgentState.PLAN
        if self.state == AgentState.PLAN:
            return AgentState.EXECUTE_TOOL
        if self.state == AgentState.EXECUTE_TOOL:
            return AgentState.EVALUATE
        if self.state == AgentState.EVALUATE:
            return AgentState.REFLECT
        if self.state == AgentState.REFLECT:
            if self.context.evaluation == "sufficient":
                return AgentState.GENERATE
            if self.context.retries < self.context.max_retries:
                return AgentState.EXECUTE_TOOL
            return AgentState.GENERATE
        if self.state == AgentState.GENERATE:
            return AgentState.END
        if self.state == AgentState.END:
            return AgentState.END
        raise ValueError(f"Unknown state: {self.state}")

    def _entry(self) -> None:
        # Minimal validation; placeholder for future input checks.
        if not self.context.user_query:
            raise ValueError("user_query must be non-empty")

    def _plan(self) -> None:
        # Placeholder intent extraction and tool planning.
        self.context.intent = "answer_user_query"
        self.context.planned_tools = ["mock_sql"]

    def _execute_tool(self) -> None:
        # Placeholder tool execution.
        if self.context.planned_tools:
            tool_name = self.context.planned_tools[0]
            self.context.tool_results.append(f"{tool_name}_result_placeholder")
        else:
            self.context.tool_results.append("no_tool_planned")

    def _evaluate(self) -> None:
        # Deterministic evaluation: always sufficient for now.
        self.context.evaluation = "sufficient"

    def _reflect(self) -> None:
        # Placeholder reflection: retry counter increments if insufficient.
        if self.context.evaluation != "sufficient":
            self.context.retries += 1

    def _generate(self) -> None:
        # Placeholder response generation.
        pass


def run_once(user_query: str) -> AgentContext:
    """Convenience runner for a single deterministic pass."""
    context = AgentContext(user_query=user_query)
    controller = AgentController(context)
    return controller.run()


if __name__ == "__main__":
    final_ctx = run_once("demo query")
    print(f"intent={final_ctx.intent}")
    print(f"planned_tools={final_ctx.planned_tools}")
    print(f"tool_results={final_ctx.tool_results}")
    print(f"evaluation={final_ctx.evaluation}")
    print(f"retries={final_ctx.retries}")
