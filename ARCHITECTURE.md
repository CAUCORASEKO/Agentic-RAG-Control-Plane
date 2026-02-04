# Architecture

This document explains the architectural intent, key design decisions, and trade-offs behind the Agentic RAG Control Plane reference implementation. It focuses on the “why” behind the structure rather than restating high-level overview material.

## 1. Architectural Goals

The architecture is designed to solve four recurring problems in agentic retrieval-augmented systems:

- **Make control explicit.** Planning, tool selection, evaluation, and response construction are treated as first-class steps rather than implicit behavior inside a single model call.
- **Bound risk and variability.** Tool use and retries are constrained by deterministic transitions and allowlisted execution, reducing unintended side effects.
- **Enable auditing.** Each decision and transition is observable, which supports debugging, evaluation, and accountability.
- **Keep components testable.** The control plane is decomposed into small, deterministic units that can be tested without model calls or external services.

## 2. Control Plane vs Execution Plane

The control plane is the decision layer: it interprets intent, selects tools, evaluates outcomes, and decides whether to retry or finish. The execution plane performs the work: retrieval, database access, external calls, and any side effects.

This separation exists to mitigate three risks:

- **Opaque decision-making.** When planning and execution are interleaved, it becomes difficult to understand why a tool was invoked or why a result was accepted.
- **Unbounded side effects.** If planning can directly execute tools, accidental or unsafe actions are harder to prevent.
- **Non-deterministic retries.** Without a distinct control layer, retry behavior is often implicit and unpredictable.

By keeping control flow separate from execution, the system can enforce policy (allowlisting, bounded retries) and provide a clear audit trail.

## 3. Agent State Machine

The system uses explicit states and deterministic transitions to make control flow predictable. The state machine in `agent_state_machine.py` defines entry, planning, execution, evaluation, reflection, generation, and termination as discrete steps.

This design prioritizes:

- **Determinism.** Transitions are rule-based, not model-driven.
- **Debuggability.** It is always clear which step failed and why.
- **Extensibility.** New states or transition rules can be added without changing unrelated behavior.

The trade-off is reduced flexibility compared to free-form chains. That is intentional: the goal is controlled behavior, not maximal autonomy.

## 4. Tool Invocation Model

Tools are executed only through an explicit allowlist and structured invocation, as implemented in `tools/registry.py`. The registry enforces a fixed catalog of tools, and the executor validates that results are consistent with the requested tool.

Key decisions:

- **Allowlist over discovery.** Only registered tools can be called, preventing accidental or implicit execution.
- **Structured results.** Tools return a `ToolResult` with explicit success and metadata, enabling downstream evaluation.
- **No free-form execution.** Free-form SQL or arbitrary shell calls are intentionally excluded to reduce risk and make tool use auditable.

This favors safety and traceability over convenience. It also makes tool behavior easier to test in isolation.

## 5. Evaluation and Reflection Loop

The evaluation step assesses whether the current context is sufficient and faithful to the user’s intent, and produces an explicit confidence signal. Reflection is a bounded loop that decides whether to retry, replan, or finalize.

The loop is bounded for two reasons:

- **Operational safety.** Unbounded retries can cause runaway costs or unintended side effects.
- **Predictable latency.** Deterministic bounds enable clearer performance expectations.

The architecture favors explicit evaluation signals rather than implicit confidence inferred from a model output. The goal is controlled correction, not open-ended agent exploration.

## 6. Observability and Traceability

Every major decision should be observable: chosen intent, planned tools, tool inputs/outputs, evaluation decisions, and retry counts. Traceability matters because agentic systems are often blamed for outcomes without a clear explanation of why they happened.

The control plane is structured so that:

- Each state transition is a trace event.
- Tool invocations are logged with inputs and structured results.
- Evaluations and reflection decisions can be replayed.

This supports reproducibility, incident analysis, and systematic improvement.

## 7. Non-Goals

This project explicitly does not attempt to be:

- A production-ready orchestration system.
- A general-purpose agent framework with dynamic, open-ended tool discovery.
- A system that performs arbitrary side effects without explicit, enforceable policy.
- A benchmarked or optimized runtime for latency or throughput.

The focus is architectural clarity and controllability.

## 8. Future Extensions

Potential extensions that align with the current design:

- Richer evaluation signals (e.g., separate sufficiency vs. faithfulness checks).
- Policy modules for tool gating and parameter validation.
- State persistence for replayable traces.
- Expanded tool registry with typed schemas and validation.
- Pluggable planners that remain bounded by the same control-plane rules.
