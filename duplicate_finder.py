"""
duplicate_finder.py - Multi-Stage Duplicate Detection Engine
=============================================================
Data models and function declarations for running the 4-stage pipeline:
  Stage 1: Size grouping (via scanner)
  Stage 2: Partial hash sampling
  Stage 3: Full SHA-256 computation
  Stage 4: Byte-for-byte exact verification
"""


from dataclasses import dataclass, field, asdict, is_dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional
from collections import defaultdict
import json
import time

from scanner import ScanResult, scan_directory
from hash_utils import (
    format_bytes,
    compute_file_sha256,
    compute_partial_hash,
    compare_files_byte_by_byte,
)

# Aliases for backwards compatibility
calculate_sha256 = compute_file_sha256
files_are_identical = compare_files_byte_by_byte


def report_progress(callback, message, current, total):
    """Call the progress callback if one was supplied."""
    if callback is not None:
        callback(message, current, total)



# ---------- Data classes ----------

@dataclass
class DuplicateGroup:
    """Represents a set of identical files."""
    size: int
    sha256: str
    files: List[Path]
    verified_byte_for_byte: bool = True

    @property
    def wasted_bytes(self) -> int:
        """Space wasted by duplicates, keeping one original."""
        return max(0, len(self.files) - 1) * self.size

    @property
    def wasted_formatted(self) -> str:
        """Human-readable wasted space."""
        return format_bytes(self.wasted_bytes)

    @property
    def size_formatted(self) -> str:
        """Human-readable size of one file."""
        return format_bytes(self.size)

    def to_dict(self) -> dict:
        """Convert this group to a JSON-friendly dictionary."""
        return {
            "size_bytes": self.size,
            "size_formatted": self.size_formatted,
            "sha256": self.sha256,
            "files": [str(path) for path in self.files],
            "file_count": len(self.files),
            "wasted_bytes": self.wasted_bytes,
            "wasted_formatted": self.wasted_formatted,
            "verified_byte_for_byte": self.verified_byte_for_byte,
        }


@dataclass
class DetectionReport:
    """Complete summary of duplicate detection."""
    scan_result: ScanResult
    groups: List[DuplicateGroup] = field(default_factory=list)
    stage_durations: Dict[str, float] = field(default_factory=dict)
    total_duration_seconds: float = 0.0

    @property
    def total_duplicate_groups(self) -> int:
        return len(self.groups)

    @property
    def total_duplicate_files(self) -> int:
        """Count all files that belong to duplicate groups."""
        return sum(len(group.files) for group in self.groups)

    @property
    def redundant_files_count(self) -> int:
        """Count extra copies, excluding one keeper per group."""
        return sum(max(0, len(group.files) - 1) for group in self.groups)

    @property
    def total_wasted_bytes(self) -> int:
        return sum(group.wasted_bytes for group in self.groups)

    @property
    def total_wasted_formatted(self) -> str:
        return format_bytes(self.total_wasted_bytes)

    def to_dict(self) -> dict:
        """Convert the report to a JSON-friendly dictionary."""
        if is_dataclass(self.scan_result):
            scan_data = asdict(self.scan_result)
        elif hasattr(self.scan_result, "to_dict"):
            scan_data = self.scan_result.to_dict()
        else:
            scan_data = str(self.scan_result)

        # Convert any Path values inside the scan result to strings.
        def make_json_safe(value):
            if isinstance(value, Path):
                return str(value)
            if isinstance(value, dict):
                return {str(k): make_json_safe(v) for k, v in value.items()}
            if isinstance(value, (list, tuple)):
                return [make_json_safe(item) for item in value]
            return value

        return {
            "scan_result": make_json_safe(scan_data),
            "duplicate_groups": [
                group.to_dict() for group in self.groups
            ],
            "summary": {
                "total_duplicate_groups": self.total_duplicate_groups,
                "total_duplicate_files": self.total_duplicate_files,
                "redundant_files_count": self.redundant_files_count,
                "total_wasted_bytes": self.total_wasted_bytes,
                "total_wasted_formatted": self.total_wasted_formatted,
            },
            "stage_durations_seconds": self.stage_durations,
            "total_duration_seconds": self.total_duration_seconds,
        }


# ---------- Duplicate detection ----------


def find_duplicates(
    root_path: Path,
    min_size_bytes: int = 0,
    include_hidden: bool = False,
    follow_symlinks: bool = False,
    verify_byte_by_byte: bool = True,
    status_callback: Optional[Callable[[str, int, int], None]] = None,
) -> DetectionReport:
    """Scan, hash, and verify duplicate files without modifying them."""

    start_time = time.perf_counter()
    stage_durations = {}

    # Stage 1: Use scanner.py to discover files.
    stage_start = time.perf_counter()

    scan_result = scan_directory(
        root_path=Path(root_path),
        min_size_bytes=min_size_bytes,
        include_hidden=include_hidden,
        follow_symlinks=follow_symlinks,
    )

    stage_durations["scan"] = time.perf_counter() - stage_start

    # Stage 2: Partial hash sampling on size candidates.
    stage_start = time.perf_counter()
    candidate_size_groups = scan_result.candidate_size_groups
    partial_candidate_groups = defaultdict(list)

    total_size_candidates = sum(
        len(paths) for paths in candidate_size_groups.values()
    )
    partial_counter = 0

    for size, paths in candidate_size_groups.items():
        partial_map = defaultdict(list)
        for path in paths:
            partial_counter += 1
            report_progress(
                status_callback, "Sampling partial hashes", partial_counter, total_size_candidates
            )
            try:
                p_hash = compute_partial_hash(path)
                partial_map[p_hash].append(path)
            except OSError as error:
                scan_result.skipped_files.append(f"{path}: {error}")

        for p_hash, matching in partial_map.items():
            if len(matching) >= 2:
                partial_candidate_groups[size].extend(matching)

    stage_durations["partial_hash"] = time.perf_counter() - stage_start
    stage_durations["size_grouping"] = stage_durations["partial_hash"]

    # Stage 3: Calculate full SHA-256 for surviving candidate files.
    stage_start = time.perf_counter()
    hashes = {}

    all_candidates = [
        path
        for paths in partial_candidate_groups.values()
        for path in paths
    ]

    total = len(all_candidates)

    for index, path in enumerate(all_candidates, start=1):
        report_progress(
            status_callback, "Hashing files", index, total
        )

        try:
            hashes[path] = calculate_sha256(path)
        except OSError as error:
            scan_result.skipped_files.append(
                f"{path}: {error}"
            )

    stage_durations["hashing"] = time.perf_counter() - stage_start

    # Stage 4: Group matching hashes and verify file contents byte-by-byte.
    stage_start = time.perf_counter()
    duplicate_groups = []

    for size, paths in partial_candidate_groups.items():
        hash_groups = defaultdict(list)

        for path in paths:
            if path in hashes:
                hash_groups[hashes[path]].append(path)

        for digest, matching_paths in hash_groups.items():
            if len(matching_paths) < 2:
                continue

            if not verify_byte_by_byte:
                duplicate_groups.append(
                    DuplicateGroup(
                        size=size,
                        sha256=digest,
                        files=matching_paths,
                        verified_byte_for_byte=False,
                    )
                )
                continue

            # Split matching hashes into byte-identical groups.
            verified_groups = []

            for path in matching_paths:
                placed = False

                for group in verified_groups:
                    try:
                        if files_are_identical(path, group[0]):
                            group.append(path)
                            placed = True
                            break
                    except OSError as error:
                        scan_result.skipped_files.append(
                            f"{path}: {error}"
                        )

                if not placed:
                    verified_groups.append([path])

            for group in verified_groups:
                if len(group) > 1:
                    duplicate_groups.append(
                        DuplicateGroup(
                            size=size,
                            sha256=digest,
                            files=group,
                            verified_byte_for_byte=True,
                        )
                    )

    stage_durations["byte_verification"] = (
        time.perf_counter() - stage_start
    )

    return DetectionReport(
        scan_result=scan_result,
        groups=duplicate_groups,
        stage_durations=stage_durations,
        total_duration_seconds=time.perf_counter() - start_time,
    )


# ---------- Export and safe cleanup proposal ----------

def export_report_json(report: DetectionReport, output_file: Path) -> None:
    """Export the detection report as formatted JSON."""
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(report.to_dict(), file, indent=4)


def generate_safe_cleanup_script(
    report: DetectionReport,
    script_path: Path
) -> None:
    """
    Generate a review-first Bash script.
    Deletion commands are comments and will NOT run automatically.
    """
    script_path = Path(script_path)
    script_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "#!/usr/bin/env bash",
        "# REVIEW CAREFULLY before enabling any deletion command.",
        "# This script does not delete files as generated.",
        "",
    ]

    for number, group in enumerate(report.groups, start=1):
        lines.append(f"# Duplicate group {number}")
        lines.append(f"# SHA-256: {group.sha256}")
        lines.append(f"# Size per file: {group.size_formatted}")

        # Keep the first path and propose the remaining copies.
        for duplicate in group.files[1:]:
            safe_path = Path(duplicate).as_posix().replace("'", "'\\''")
            lines.append(f"# rm -- '{safe_path}'")

        lines.append("")

    with script_path.open("w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(lines))

