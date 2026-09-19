# Security

- No secrets in Git.
- D-Wave token is backend-only.
- Never put QPU credentials in Next.js public environment variables.
- Validate all API input with Pydantic.
- Restrict CORS.
- Bound simulation duration, vehicle count, QUBO size, shots and QAOA reps.
- Avoid arbitrary code execution from user input.
- Treat OSM/network data as untrusted external data.
- Do not expose internal exception traces in production UI.
- Add rate limits if deployed publicly.
- Clearly state that the system is not connected to real traffic infrastructure.
