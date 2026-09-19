"""API routes for controlled benchmarking."""

from fastapi import APIRouter

from app.benchmark.config import BenchmarkConfig
from app.benchmark.models import BenchmarkComparison
from app.benchmark.service import BenchmarkService

benchmark_router = APIRouter(prefix="/benchmarks", tags=["Benchmarking"])


@benchmark_router.get("/scenarios")
def get_benchmark_scenarios() -> list[dict[str, str]]:
    """List available benchmark scenarios."""
    return [
        {"id": "low-traffic", "name": "Low Traffic", "description": "Low-demand baseline scenario"},
        {"id": "congested-traffic", "name": "Congested Traffic", "description": "High-volume queueing scenario"},
        {"id": "dynamic-congestion", "name": "Dynamic Congestion Spike", "description": "Mid-simulation demand spike"},
        {"id": "accident", "name": "Traffic Accident", "description": "Capacity reduction accident scenario"},
        {"id": "road-closure", "name": "Road Closure", "description": "Temporary edge closure scenario"},
        {"id": "emergency", "name": "Emergency Corridor", "description": "Emergency vehicle green corridor scenario"},
    ]


@benchmark_router.post("/run", response_model=BenchmarkComparison)
def run_benchmark(config: BenchmarkConfig) -> BenchmarkComparison:
    """Run a matched Classical vs Hybrid QAOA comparison for a scenario."""
    service = BenchmarkService()
    return service.run_benchmark_scenario(config)
