"""
scanner.py - Filesystem Scanner & Size-Based Grouping
=====================================================
Declarations for directory traversal, metadata extraction,
and size-based partitioning (Stage 1 of deduplication).
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional


@dataclass
class ScanResult:
    """Holds summary statistics and partitioned files from a filesystem scan."""
    root_directory: Path
    total_files_found: int = 0
    total_bytes_found: int = 0
    size_groups: Dict[int, List[Path]] = field(default_factory=dict)
    candidate_size_groups: Dict[int, List[Path]] = field(default_factory=dict)
    skipped_files: List[str] = field(default_factory=list)
    scan_duration_seconds: float = 0.0

    @property
    def candidate_file_count(self) -> int:
        """Total number of files in size groups with >= 2 files."""
        pass

    @property
    def pruned_unique_file_count(self) -> int:
        """Number of files pruned solely because their size is unique."""
        pass


def scan_directory(
    root_path: Path,
    min_size_bytes: int = 0,
    include_hidden: bool = False,
    follow_symlinks: bool = False,
    progress_callback: Optional[Callable[[int, Path], None]] = None,
) -> ScanResult:
    """
    Recursively scan a directory, catalog file sizes, and group candidate duplicates.
    Files with unique sizes are eliminated from candidate groups.
    """
    pass
