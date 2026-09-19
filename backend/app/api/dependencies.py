"""FastAPI dependency providers for simulation session lookup."""

from app.api.session import SimulationSession, SimulationSessionManager, session_manager


def get_session_manager() -> SimulationSessionManager:
    """Dependency provider for global session manager."""
    return session_manager


def get_simulation_session(simulation_id: str) -> SimulationSession:
    """Dependency provider looking up an active session by simulation_id."""
    return session_manager.get_session(simulation_id)
