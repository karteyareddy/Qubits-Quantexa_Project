"""Stage 1 HTTP routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Return the backend health status."""
    return {"status": "ok"}
