# Exact Operator Runbook

## Phase 1
Clone repository.

```bash
git clone https://github.com/Joann-jk/Quantum-Traffic-Priority-Routing.git
cd Quantum-Traffic-Priority-Routing
git checkout -b hackathon-nextjs
```

## Phase 2
Run original app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Record what works.

## Phase 3
Copy this documentation bundle into repository root.

## Phase 4
Open Codex and give `CODEX_FIRST_PROMPT.md`.

Do not allow code modification yet.

## Phase 5
Review:
- REPOSITORY_AUDIT.md
- MIGRATION_PLAN.md

If they are correct, continue.

## Phase 6
Tell Codex:
`Execute Stage 1 from TASKS.md. Stop at the gate.`

Repeat for every stage.

## Stage prompts

### Stage 2
`Execute Stage 2. Build backend domain models and tests. Stop at the gate.`

### Stage 3
`Execute Stage 3. Migrate network/routing while preserving existing behavior. Stop at the gate.`

### Stage 4
`Execute Stage 4. Migrate traffic simulation. Stop at the gate.`

### Stage 5
`Execute Stage 5. Implement traffic signals and fixed baseline. Stop at the gate.`

### Stage 6
`Execute Stage 6. Implement metrics. Stop at the gate.`

### Stage 7
`Execute Stage 7. Refactor existing Priority-Aware MTF into backend optimization modules with regression tests. Stop at the gate.`

### Stage 8
`Execute Stage 8 using QUANTUM_SPEC.md. Build signal QUBO. Stop at the gate.`

### Stage 9
`Execute Stage 9 using QUANTUM_SPEC.md. Implement QAOA with Qiskit Aer. Stop at the gate.`

### Stage 10
`Execute Stage 10. Integrate hybrid optimization. Stop at the gate.`

### Stage 11
`Execute Stage 11. Integrate adaptive signal control. Stop at the gate.`

### Stage 12
`Execute Stage 12. Implement events. Stop at the gate.`

### Stage 13
`Execute Stage 13. Implement emergency green corridor and restoration. Stop at the gate.`

### Stage 14
`Execute Stage 14. Implement FastAPI REST and WebSocket APIs. Stop at the gate.`

### Stage 15
`Execute Stage 15 using UI_SPEC.md. Build the Next.js frontend. Stop at the gate.`

### Stage 16
`Execute Stage 16. Implement baseline-vs-hybrid experiments and export. Stop at the gate.`

### Stage 17
`Execute Stage 17. Run all quality gates and fix failures. Stop at the gate.`

### Stage 18
`Execute Stage 18. Implement deployment. Stop at the gate.`

### Stage 19
`Execute Stage 19. Polish and verify the complete demo.`

## Gemini review

After Stage 19, ask Gemini to review the repository against:
- PRD.md
- QUANTUM_SPEC.md
- TESTING.md
- TASKS.md

Then give the findings to Codex for a verified repair pass.

## Final commands

Backend:
```bash
pytest -q
pytest --cov=backend/app
ruff check backend
mypy backend/app
```

Frontend:
```bash
npm run lint
npm run build
```
