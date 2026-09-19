"""CLI entrypoint for running benchmark experiments.

Usage:
    python -m app.benchmark --scenario low-traffic --seed 42 --duration 60
"""

import argparse
import sys
from pathlib import Path

# Add backend directory to sys.path if invoked directly
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.benchmark.config import BenchmarkConfig
from app.benchmark.service import BenchmarkService


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Quantum vs Classical Traffic Optimization Benchmark"
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default="low-traffic",
        choices=[
            "low-traffic",
            "congested-traffic",
            "dynamic-congestion",
            "accident",
            "road-closure",
            "emergency",
            "all",
        ],
        help="Target scenario identifier or 'all' for full suite",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--duration", type=float, default=60.0, help="Simulation duration in seconds"
    )
    parser.add_argument(
        "--control-interval",
        type=float,
        default=5.0,
        help="Adaptive optimization interval in seconds",
    )
    parser.add_argument(
        "--output-dir", type=str, default="benchmark_results", help="Export output directory"
    )

    args = parser.parse_args()

    config = BenchmarkConfig(
        scenario_id=args.scenario if args.scenario != "all" else "low-traffic",
        duration_seconds=args.duration,
        control_interval_seconds=args.control_interval,
        seed=args.seed,
        output_dir=args.output_dir,
    )

    service = BenchmarkService()

    print("==================================================")
    print("Running Traffic Optimization Benchmark")
    print(f"Scenario: {args.scenario}")
    print(f"Seed: {args.seed} | Duration: {args.duration}s")
    print("==================================================")

    if args.scenario == "all":
        report = service.run_benchmark_suite(config)
    else:
        comp = service.run_benchmark_scenario(config)
        report = service.run_benchmark_suite(config, scenarios=(args.scenario,))

    json_path, csv_path = service.export_report(report, args.output_dir)

    print("\nBenchmark Execution Complete!")
    print(f"Report ID: {report.report_id}")
    print(f"JSON Export: {json_path}")
    print(f"CSV Export:  {csv_path}")

    print("\n--- Summary Results ---")
    for comp in report.comparisons:
        print(f"\nScenario: {comp.scenario_id}")
        print(f"  Fixed-Time Classical Avg Wait: {comp.classical_result.metrics.get('average_waiting_time_seconds', 0.0):.2f}s")
        print(f"  Hybrid QAOA Avg Wait:       {comp.hybrid_result.metrics.get('average_waiting_time_seconds', 0.0):.2f}s")
        if "average_waiting_time_seconds" in comp.metric_deltas:
            d = comp.metric_deltas["average_waiting_time_seconds"]
            print(f"  Absolute Delta:             {d.absolute_delta:+.2f}s")
            if d.relative_change_percent is not None:
                print(f"  Relative Change:            {d.relative_change_percent:+.1f}%")
        print(f"  QAOA Optimizations:         {comp.hybrid_result.optimization_metrics.get('optimization_count', 0)}")
        print(f"  QAOA Fallbacks:             {comp.hybrid_result.optimization_metrics.get('fallback_count', 0)}")


if __name__ == "__main__":
    main()
