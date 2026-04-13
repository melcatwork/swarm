"""
Job tracker for long-running swarm analysis tasks.

Tracks pipeline execution status, progress, and results in memory.
"""
import logging
import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional
from threading import Lock

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Job execution status."""
    PENDING = "pending"
    PARSING = "parsing"
    EXPLORATION = "exploration"
    EVALUATION = "evaluation"
    ADVERSARIAL = "adversarial"
    MITIGATIONS = "mitigations"
    COMPLETED = "completed"
    FAILED = "failed"


class Job:
    """Represents a swarm analysis job."""

    def __init__(self, job_id: str, filename: str):
        self.job_id = job_id
        self.filename = filename
        self.status = JobStatus.PENDING
        self.progress_percent = 0
        self.current_phase = ""
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.completed_at: Optional[str] = None
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.logs: list[str] = []

    def update_status(self, status: JobStatus, progress: int, phase: str = ""):
        """Update job status and progress."""
        self.status = status
        self.progress_percent = progress
        self.current_phase = phase
        log_msg = f"[{self.job_id[:8]}] {status.value}: {phase} ({progress}%)"
        logger.info(log_msg)
        self.logs.append(f"{datetime.now(timezone.utc).isoformat()} - {log_msg}")

    def complete(self, result: Dict[str, Any]):
        """Mark job as completed with results."""
        self.status = JobStatus.COMPLETED
        self.progress_percent = 100
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.result = result
        logger.info(f"[{self.job_id[:8]}] Job completed successfully")
        self.logs.append(f"{datetime.now(timezone.utc).isoformat()} - Completed successfully")

    def fail(self, error: str):
        """Mark job as failed with error message."""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.error = error
        logger.error(f"[{self.job_id[:8]}] Job failed: {error}")
        self.logs.append(f"{datetime.now(timezone.utc).isoformat()} - Failed: {error}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for API response."""
        elapsed_seconds = None
        if self.completed_at:
            start = datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))
            end = datetime.fromisoformat(self.completed_at.replace("Z", "+00:00"))
            elapsed_seconds = (end - start).total_seconds()

        return {
            "job_id": self.job_id,
            "filename": self.filename,
            "status": self.status.value,
            "progress_percent": self.progress_percent,
            "current_phase": self.current_phase,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "elapsed_seconds": elapsed_seconds,
            "error": self.error,
            "logs": self.logs[-10:],  # Last 10 log entries
        }


class JobTracker:
    """
    Thread-safe in-memory job tracker.

    Stores job status and results for long-running swarm analyses.
    """

    def __init__(self, max_jobs: int = 100):
        self.jobs: Dict[str, Job] = {}
        self.max_jobs = max_jobs
        self.lock = Lock()

    def create_job(self, filename: str) -> str:
        """Create a new job and return job ID."""
        job_id = str(uuid.uuid4())
        with self.lock:
            job = Job(job_id, filename)
            self.jobs[job_id] = job

            # Cleanup old jobs if we exceed max
            if len(self.jobs) > self.max_jobs:
                self._cleanup_old_jobs()

        logger.info(f"Created job {job_id[:8]} for file {filename}")
        return job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        with self.lock:
            return self.jobs.get(job_id)

    def update_job(self, job_id: str, status: JobStatus, progress: int, phase: str = ""):
        """Update job status."""
        with self.lock:
            job = self.jobs.get(job_id)
            if job:
                job.update_status(status, progress, phase)

    def complete_job(self, job_id: str, result: Dict[str, Any]):
        """Mark job as completed."""
        with self.lock:
            job = self.jobs.get(job_id)
            if job:
                job.complete(result)

    def fail_job(self, job_id: str, error: str):
        """Mark job as failed."""
        with self.lock:
            job = self.jobs.get(job_id)
            if job:
                job.fail(error)

    def _cleanup_old_jobs(self):
        """Remove oldest completed/failed jobs when limit exceeded."""
        completed_jobs = [
            (job_id, job) for job_id, job in self.jobs.items()
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]
        ]

        if completed_jobs:
            # Sort by completion time and remove oldest
            completed_jobs.sort(key=lambda x: x[1].completed_at or "")
            oldest_job_id = completed_jobs[0][0]
            del self.jobs[oldest_job_id]
            logger.info(f"Cleaned up old job {oldest_job_id[:8]}")

    def list_jobs(self, limit: int = 20) -> list[Dict[str, Any]]:
        """List recent jobs."""
        with self.lock:
            jobs = sorted(
                self.jobs.values(),
                key=lambda j: j.started_at,
                reverse=True
            )[:limit]
            return [job.to_dict() for job in jobs]


# Global singleton instance
_job_tracker: Optional[JobTracker] = None


def get_job_tracker() -> JobTracker:
    """Get or create the global job tracker instance."""
    global _job_tracker
    if _job_tracker is None:
        _job_tracker = JobTracker()
    return _job_tracker
