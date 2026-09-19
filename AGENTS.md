# Agent Instructions

You are the primary implementation agent.

## Read first
1. PRD.md
2. TASKS.md
3. ARCHITECTURE.md
4. TECH_STACK.md
5. Relevant subsystem spec.

## Existing repository rule

This is a migration/extension project.

Do NOT blindly rewrite:
- priority_aware_mtf.py
- traffic_simulator.py
- network_builder.py
- visualization.py

Inspect and preserve useful algorithms.

## Architecture rule

Final:
Next.js -> FastAPI -> Python domain/quantum/simulation.

Do not put Qiskit in Next.js.

## Execution loop

Inspect -> Plan -> Implement -> Test -> Fix -> Verify -> Update TASKS -> Continue.

## Quantum honesty

- QAOA Aer is quantum simulation, not a claim of real hardware execution.
- D-Wave/QPU is optional.
- Classical fallback must be explicit.
- Do not claim quantum advantage from benchmark results unless scientifically justified.

## Migration rule

When replacing Streamlit:
- preserve backend functionality,
- move presentation to Next.js,
- remove Streamlit only after migration is verified.

## Code quality

Python:
- type hints
- Pydantic validation
- small modules
- ruff
- mypy

TypeScript:
- strict mode
- typed API responses
- reusable components
- no `any` unless justified

## Stop conditions

Stop if:
- requirements conflict,
- an existing algorithm cannot be migrated without changing its documented behavior,
- QAOA result cannot be validated,
- a safety constraint cannot be enforced.
Record the issue in DECISIONS.md.
