"""High-level BenchmarkService orchestrating benchmark execution and reporting."""

from pathlib import Path

from app.benchmark.config import BenchmarkConfig
from app.benchmark.models import BenchmarkComparison, BenchmarkReport
from app.benchmark.reporting import (
    build_benchmark_report,
    export_report_to_csv,
    export_report_to_json,
)
from app.benchmark.runner import BenchmarkRunner


class BenchmarkService:
    """Service orchestrating scenario comparisons and exporting results."""

    def __init__(self, runner: BenchmarkRunner | None = None) -> None:
        self.runner = runner or BenchmarkRunner()

    def run_benchmark_scenario(self, config: BenchmarkConfig) -> BenchmarkComparison:
        """Run matched classical vs hybrid comparison for a single scenario."""
        return self.runner.run_matched_comparison(config)

    def run_benchmark_suite(
        self,
        base_config: BenchmarkConfig,
        scenarios: tuple[str, ...] = (
            "low-traffic",
            "congested-traffic",
            "dynamic-congestion",
            "accident",
            "road-closure",
            "emergency",
        ),
    ) -> BenchmarkReport:
        """Run matched comparison across a full benchmark scenario suite."""
        comparisons: list[BenchmarkComparison] = []

        for scenario_id in scenarios:
            cfg = base_config.model_copy(update={"scenario_id": scenario_id})
            comp = self.run_benchmark_scenario(cfg)
            comparisons.append(comp)

        report = build_benchmark_report(comparisons, seed=base_config.seed)
        return report

    def export_report(
        self, report: BenchmarkReport, output_dir_str: str = "benchmark_results"
    ) -> tuple[Path, Path]:
        """Export report to JSON and CSV files in output_dir."""
        out_dir = Path(output_dir_str)
        json_path = out_dir / f"{report.report_id}.json"
        csv_path = out_dir / f"{report.report_id}.csv"

        json_file = export_report_to_json(report, json_path)
        csv_file = export_report_to_csv(report, csv_path)

        return json_file, csv_file
