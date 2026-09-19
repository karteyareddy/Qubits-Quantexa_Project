"""Benchmark runner managing single and matched comparison executions."""

import time
import uuid

from app.benchmark.comparison import compare_results
from app.benchmark.config import BenchmarkConfig
from app.benchmark.controls import (
    FixedTimeStrategy,
    HybridQuantumStrategy,
    TrafficControlStrategy,
)
from app.benchmark.models import BenchmarkComparison, BenchmarkRunResult
from app.benchmark.scenarios import build_benchmark_scenario
from app.metrics.service import MetricsService


class BenchmarkRunner:
    """Execution engine for reproducible matched traffic benchmarks."""

    def __init__(self, metrics_service: MetricsService | None = None) -> None:
        self.metrics_service = metrics_service or MetricsService()

    def run_single(
        self,
        config: BenchmarkConfig,
        strategy: TrafficControlStrategy,
        *,
        seed_override: int | None = None,
    ) -> BenchmarkRunResult:
        """Execute a single strategy benchmark run with precise wall-clock timing."""
        effective_seed = seed_override if seed_override is not None else config.seed
        scenario, events = build_benchmark_scenario(
            config.scenario_id,
            seed=effective_seed,
            duration_seconds=config.duration_seconds,
        )

        run_id = f"bmk-{strategy.name}-{uuid.uuid4().hex[:8]}"
        t_start = time.perf_counter()

        try:
            sim, observations, emerg_svc, opt_stats = strategy.run_simulation(
                scenario=scenario,
                events=events,
                control_interval_seconds=config.control_interval_seconds,
            )
            wall_time = time.perf_counter() - t_start

            # Evaluate Stage 6 metrics using trajectory observations
            sc_metrics = self.metrics_service.evaluate(
                scenario_id=config.scenario_id,
                final_state=sim.state,
                observations=observations,
            )

            tm = sc_metrics.traffic_metrics
            em = sc_metrics.environmental_metrics
            em_m = sc_metrics.emergency_metrics

            traffic_dict = {
                "total_vehicles": tm.total_vehicles,
                "completed_vehicles": tm.completed_vehicles,
                "completion_rate": tm.completion_rate,
                "throughput_vph": tm.throughput * 60.0,
                "average_travel_time_seconds": tm.average_travel_seconds,
                "average_waiting_time_seconds": tm.average_waiting_seconds,
                "max_waiting_time_seconds": tm.max_waiting_seconds,
                "total_waiting_time_seconds": tm.total_waiting_seconds,
                "average_queue_length": tm.average_queue_length,
                "max_queue_length": tm.max_queue_length,
                "fuel_consumed_liters": em.fuel_liters,
                "co2_emitted_kg": em.co2_kg,
            }

            emerg_dict = {
                "emergency_waiting_time_seconds": em_m.emergency_average_waiting_seconds,
                "emergency_travel_time_seconds": em_m.emergency_average_travel_seconds,
                "total_corridors_active": len(emerg_svc.corridor_history),
            }

            return BenchmarkRunResult(
                run_id=run_id,
                scenario_id=config.scenario_id,
                control_strategy=strategy.name,
                seed=effective_seed,
                duration_seconds=config.duration_seconds,
                metrics=traffic_dict,
                optimization_metrics=opt_stats,
                emergency_metrics=emerg_dict,
                wall_clock_runtime_seconds=wall_time,
                status="COMPLETED",
            )
        except Exception as err:  # noqa: BLE001
            wall_time = time.perf_counter() - t_start
            return BenchmarkRunResult(
                run_id=run_id,
                scenario_id=config.scenario_id,
                control_strategy=strategy.name,
                seed=effective_seed,
                duration_seconds=config.duration_seconds,
                wall_clock_runtime_seconds=wall_time,
                status="FAILED",
                failure_reason=str(err),
            )

    def run_matched_comparison(
        self,
        config: BenchmarkConfig,
        classical_strategy: TrafficControlStrategy | None = None,
        hybrid_strategy: TrafficControlStrategy | None = None,
    ) -> BenchmarkComparison:
        """Run matched comparison: Classical Fixed-Time vs Hybrid QAOA under identical initial state."""
        c_strat = classical_strategy or FixedTimeStrategy()
        h_strat = hybrid_strategy or HybridQuantumStrategy()

        res_c = self.run_single(config, c_strat)
        res_h = self.run_single(config, h_strat)

        return compare_results(config.scenario_id, res_c, res_h)
