"""
duplicate_finder.py - Multi-Stage Duplicate Detection Engine
=============================================================
Data models and function declarations for running the 4-stage pipeline:
  Stage 1: Size grouping (via scanner)
  Stage 2: Partial hash sampling
  Stage 3: Full SHA-256 computation
  Stage 4: Byte-for-byte exact verification
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from scanner import ScanResult


@dataclass
class DuplicateGroup:
    """Represents a set of identical files."""
    size: int
    sha256: str
    files: List[Path]
    verified_byte_for_byte: bool = True

    @property
    def wasted_bytes(self) -> int:
        """Space wasted by duplicates (excluding 1 original keeper)."""
        pass

    @property
    def wasted_formatted(self) -> str:
        """Human-readable string of wasted space."""
        pass

    @property
    def size_formatted(self) -> str:
        """Human-readable string of individual file size."""
        pass

    def to_dict(self) -> dict:
        """Serialize duplicate group to a dictionary."""
        pass


@dataclass
class DetectionReport:
    """Complete summary of duplicate scan results and performance statistics."""
    scan_result: ScanResult
    groups: List[DuplicateGroup] = field(default_factory=list)
    stage_durations: Dict[str, float] = field(default_factory=dict)
    total_duration_seconds: float = 0.0

    @property
    def total_duplicate_groups(self) -> int:
        pass

    @property
    def total_duplicate_files(self) -> int:
        pass

    @property
    def redundant_files_count(self) -> int:
        pass

    @property
    def total_wasted_bytes(self) -> int:
        pass

    @property
    def total_wasted_formatted(self) -> str:
        pass

    def to_dict(self) -> dict:
        """Serialize report to a dictionary for JSON output."""
        pass


def find_duplicates(
    root_path: Path,
    min_size_bytes: int = 0,
    include_hidden: bool = False,
    follow_symlinks: bool = False,
    verify_byte_by_byte: bool = True,
    status_callback: Optional[Callable[[str, int, int], None]] = None,
) -> DetectionReport:
    """
    Execute the full 4-stage duplicate detection pipeline.
    Purely read-only; NEVER modifies or deletes files on disk.
    """
    pass


def export_report_json(report: DetectionReport, output_file: Path) -> None:
    """Export the detection report to a formatted JSON file."""
    pass


def generate_safe_cleanup_script(report: DetectionReport, script_path: Path) -> None:
    """
    Generate an explicit review-first cleanup shell script (bash or batch)
    with proposed deletion commands commented out by default.
    """
    pass
