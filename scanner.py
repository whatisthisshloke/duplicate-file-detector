from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional
import os
import time

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
        return sum(
            len(files)
            for files in self.candidate_size_groups.values()
        )

    @property
    def pruned_unique_file_count(self) -> int:
        """Number of files pruned solely because their size is unique."""
        return sum(
            len(files)
            for files in self.size_groups.values()
            if len(files) == 1
        )



def scan_directory(
    root_path: Path,
    min_size_bytes: int = 0,
    include_hidden: bool = False,
    follow_symlinks: bool = False,
    progress_callback: Optional[Callable[[int, Path], None]] = None,
) -> ScanResult:

    if not root_path.is_dir():
        raise NotADirectoryError("Directory does not exist")

    if min_size_bytes < 0:
        raise ValueError("Minimum size cannot be negative")

    start_time = time.time()
    result = ScanResult(root_directory=root_path)

    for current_dir, dirs, files in os.walk(root_path):

        for filename in files:
            file_path = Path(current_dir) / filename

            if not include_hidden and filename.startswith("."):
                continue

            try:
                file_size = file_path.stat().st_size

                if file_size < min_size_bytes:
                    continue

                result.total_files_found += 1
                result.total_bytes_found += file_size

                if file_size not in result.size_groups:
                    result.size_groups[file_size] = []

                result.size_groups[file_size].append(file_path)

                if progress_callback is not None:
                    progress_callback(
                        result.total_files_found, file_path
                    )

            except OSError:
                result.skipped_files.append(str(file_path))

    for size, paths in result.size_groups.items():
        if len(paths) >= 2:
            result.candidate_size_groups[size] = paths

    result.scan_duration_seconds = time.time() - start_time

    return result
