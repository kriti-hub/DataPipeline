"""Pipeline run metrics collector.

Tracks extraction / validation / transform / load counts and timings so the
orchestrator can persist them to ``_pipeline_runs``.

Usage::

    from src.etl.utils.metrics import PipelineMetrics
    m = PipelineMetrics(run_id="run-001")
    m.record_extraction("workers", records=1200, duration_ms=340)
    m.record_validation(passed=1195, quarantined=5)
    print(m.summary())
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class StageMetric:
    """Timing and record counts for a single pipeline stage."""

    stage: str
    started_at: str = ""
    completed_at: str = ""
    duration_ms: float = 0.0
    records_in: int = 0
    records_out: int = 0
    errors: int = 0
    details: dict[str, Any] = field(default_factory=dict)


class PipelineMetrics:
    """Accumulates metrics across all ETL stages for a single run."""

    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.completed_at: str | None = None
        self.status: str = "Running"
        self.stages: list[StageMetric] = []

        # Aggregate counters
        self.records_extracted: int = 0
        self.records_validated: int = 0
        self.records_quarantined: int = 0
        self.records_loaded: int = 0
        self.error_message: str | None = None

    # ------------------------------------------------------------------
    # Stage helpers
    # ------------------------------------------------------------------

    def start_stage(self, stage_name: str) -> StageMetric:
        """Begin timing a pipeline stage.

        Args:
            stage_name: Human-readable stage label.

        Returns:
            The :class:`StageMetric` being tracked.
        """
        metric = StageMetric(
            stage=stage_name,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        self.stages.append(metric)
        return metric

    def end_stage(self, metric: StageMetric, **kwargs: Any) -> None:
        """Finalize a stage metric with timing and counts.

        Args:
            metric: The metric returned by :meth:`start_stage`.
            **kwargs: Additional fields to set on the metric
                      (records_in, records_out, errors, details).
        """
        metric.completed_at = datetime.now(timezone.utc).isoformat()
        for k, v in kwargs.items():
            if hasattr(metric, k):
                setattr(metric, k, v)

    # ------------------------------------------------------------------
    # Convenience recorders
    # ------------------------------------------------------------------

    def record_extraction(
        self,
        endpoint: str,
        records: int,
        duration_ms: float,
    ) -> None:
        """Log extraction results for one endpoint."""
        self.records_extracted += records
        sm = StageMetric(
            stage=f"extract:{endpoint}",
            records_out=records,
            duration_ms=duration_ms,
        )
        self.stages.append(sm)

    def record_validation(
        self,
        passed: int,
        quarantined: int,
    ) -> None:
        """Log validation totals."""
        self.records_validated = passed
        self.records_quarantined = quarantined

    def record_load(self, table: str, rows: int) -> None:
        """Log how many rows were loaded into a table."""
        self.records_loaded += rows
        sm = StageMetric(stage=f"load:{table}", records_out=rows)
        self.stages.append(sm)

    # ------------------------------------------------------------------
    # Finalize
    # ------------------------------------------------------------------

    def finalize(self, status: str = "Success", error: str | None = None) -> None:
        """Mark the run as complete.

        Args:
            status: Final status string (``Success``, ``Failed``, ``Partial``).
            error: Optional error message if the run failed.
        """
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.status = status
        self.error_message = error

    def summary(self) -> dict[str, Any]:
        """Return a flat dict suitable for ``_pipeline_runs`` insertion."""
        started = datetime.fromisoformat(self.started_at)
        completed = (
            datetime.fromisoformat(self.completed_at) if self.completed_at else None
        )
        duration = (completed - started).total_seconds() if completed else None

        return {
            "run_id": self.run_id,
            "pipeline_name": "wellnow_staffing_etl",
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "records_extracted": self.records_extracted,
            "records_validated": self.records_validated,
            "records_quarantined": self.records_quarantined,
            "records_loaded": self.records_loaded,
            "error_message": self.error_message,
            "run_duration_seconds": round(duration, 2) if duration else None,
            "_batch_id": self.run_id,
        }
