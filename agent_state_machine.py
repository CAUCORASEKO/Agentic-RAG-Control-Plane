from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class State(Enum):
    # ENTRY: Initialize context for a new agent run.
    ENTRY = "ENTRY"
    # PLAN: Produce a structured plan for tool usage or reasoning steps.
    PLAN = "PLAN"
    # EXECUTE_TOOL: Execute a single planned tool action (placeholder here).
    EXECUTE_TOOL = "EXECUTE_TOOL"
    # EVALUATE: Evaluate tool outputs against the plan and goal.
    EVALUATE = "EVALUATE"
    # REFLECT: Decide whether to iterate, adjust, or proceed.
    REFLECT = "REFLECT"
    # GENERATE_RESPONSE: Produce the final user-facing response.
    GENERATE_RESPONSE = "GENERATE_RESPONSE"
    # END: Terminal state for the run.
    END = "END"


@dataclass
class AgentContext:
    goal: str
    plan: List[str] = field(default_factory=list)
    tool_results: List[str] = field(default_factory=list)
    evaluation: Optional[str] = None
    response: Optional[str] = None
    step_count: int = 0


def transition(state: State, ctx: AgentContext) -> State:
    """Deterministic transition function based on state and context.

    This function encodes the explicit state machine. No LLM calls are made.
    """
    if state == State.ENTRY:
        return State.PLAN

    if state == State.PLAN:
        return State.EXECUTE_TOOL

    if state == State.EXECUTE_TOOL:
        return State.EVALUATE

    if state == State.EVALUATE:
        return State.REFLECT

    if state == State.REFLECT:
        # Minimal single-loop behavior: always proceed to response.
        return State.GENERATE_RESPONSE

    if state == State.GENERATE_RESPONSE:
        return State.END

    if state == State.END:
        return State.END

    raise ValueError(f"Unknown state: {state}")


def step(state: State, ctx: AgentContext) -> None:
    """Run the side effects for a given state.

    Each state mutates context in a minimal, placeholder way.
    """
    if state == State.ENTRY:
        ctx.step_count += 1
        return

    if state == State.PLAN:
        # Placeholder plan: explicitly stated steps.
        ctx.plan = ["search", "read", "synthesize"]
        ctx.step_count += 1
        return

    if state == State.EXECUTE_TOOL:
        # Placeholder tool execution: no real tools invoked.
        ctx.tool_results.append("tool_result_placeholder")
        ctx.step_count += 1
        return

    if state == State.EVALUATE:
        # Placeholder evaluation: deterministic outcome.
        ctx.evaluation = "sufficient"
        ctx.step_count += 1
        return

    if state == State.REFLECT:
        # Placeholder reflection: no changes, proceed.
        ctx.step_count += 1
        return

    if state == State.GENERATE_RESPONSE:
        # Placeholder response generation.
        ctx.response = "response_placeholder"
        ctx.step_count += 1
        return

    if state == State.END:
        return

    raise ValueError(f"Unknown state: {state}")


def run_once(goal: str) -> AgentContext:
    """Simulate a single deterministic loop through the state machine."""
    ctx = AgentContext(goal=goal)
    state = State.ENTRY

    while state != State.END:
        step(state, ctx)
        state = transition(state, ctx)

    return ctx


if __name__ == "__main__":
    final_ctx = run_once("demo goal")
    print(f"steps={final_ctx.step_count}")
    print(f"plan={final_ctx.plan}")
    print(f"tool_results={final_ctx.tool_results}")
    print(f"evaluation={final_ctx.evaluation}")
    print(f"response={final_ctx.response}")
