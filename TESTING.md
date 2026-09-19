# Testing

## Backend unit tests

- domain validation
- network creation
- route finding
- vehicle movement
- queue calculation
- signal transitions
- events
- QUBO construction
- QAOA wrapper
- decoder
- feasibility
- metrics
- emergency corridor

## Backend integration

- scenario -> simulation -> metrics
- traffic -> QUBO -> QAOA -> signal plan
- emergency -> route -> priority -> restoration
- event -> changed state -> optimization

## API tests

Use FastAPI TestClient for:
- health
- scenarios
- simulation
- events
- optimization
- emergency
- metrics

## Frontend

At minimum:
- TypeScript compilation
- lint
- build
- component tests for critical controls
- API client tests
- WebSocket state parsing tests

## E2E

If time allows, Playwright:
1. open dashboard
2. start simulation
3. trigger congestion
4. run optimization
5. trigger emergency
6. verify analytics

## Quality commands

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

Never weaken tests to make them pass.
