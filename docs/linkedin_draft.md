I’ve been exploring what *agentic RAG* actually means beyond tool routing.

Most examples today focus on:
input → agent → tool → answer

That works for demos, but breaks down when you need:
- traceability
- evaluation
- cost control
- predictable behavior

I started building a small reference project that treats agentic RAG as a **control plane problem**, not just an orchestration problem.

Key ideas:
- explicit planning vs execution
- safe, registered tools
- evaluation and bounded reflection loops
- PostgreSQL as a unified backend (memory, retrieval, logs)

This is not a framework or a product — just a transparent, hackable reference implementation.

Repo: https://github.com/CAUCORASEKO/agentic-rag-control-plane