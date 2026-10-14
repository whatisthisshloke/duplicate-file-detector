"""
main.py - Duplicate File Detector CLI Entry Point
=================================================
CLI interface declarations for parsing user arguments, invoking detection,
printing terminal reports, running math demos, and exporting safe scripts.
"""


import argparse
from pathlib import Path
import sys

from duplicate_finder import (
    DetectionReport,
    find_duplicates,
    export_report_json,
    generate_safe_cleanup_script,
)
from collision_demo import run_interactive_demo


def parse_size_string(size_str: str) -> int:
    """
    Convert a size like '1024', '4KB', '10MB', or '1GB' to bytes.
    """
    size_str = size_str.strip()
    if size_str.startswith("-"):
        raise ValueError("Size cannot be negative.")

    size_str = size_str.upper()

    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4,
    }

    # Find the numeric part and the unit.
    number = ""
    unit = ""

    for char in size_str:
        if char.isdigit() or char == ".":
            if unit:
                raise ValueError(f"Invalid size string: {size_str}")
            number += char
        elif char.isspace():
            continue
        else:
            unit += char

    if not number:
        raise ValueError(f"Invalid size: {size_str}")

    if unit == "":
        unit = "B"

    if unit not in units:
        raise ValueError(f"Unknown size unit: {unit}")

    value = float(number)

    if value < 0:
        raise ValueError("Size cannot be negative.")

    return int(value * units[unit])


def print_banner() -> None:
    """Print the application header banner."""
    print("=" * 55)
    print("          DUPLICATE FILE DETECTOR")
    print("       Mathematical Foundations Project")
    print("=" * 55)


def display_report_cli(
    report: DetectionReport,
    verbose: bool = True
) -> None:
    """Print summary statistics and duplicate groups."""

    print("\n========== SCAN SUMMARY ==========")
    print(f"Duplicate groups: {report.total_duplicate_groups}")
    print(f"Files in duplicate groups: {report.total_duplicate_files}")
    print(f"Redundant copies: {report.redundant_files_count}")
    print(f"Potential wasted space: {report.total_wasted_formatted}")
    print(f"Scan duration: {report.total_duration_seconds:.3f} seconds")

    if not report.groups:
        print("\nNo duplicate files found.")
        return

    if verbose:
        print("\n========== DUPLICATE GROUPS ==========")

        for index, group in enumerate(report.groups, start=1):
            print(f"\nGroup {index}")
            print(f"File size: {group.size_formatted}")
            print(f"SHA-256: {group.sha256}")
            print(f"Byte-verified: {group.verified_byte_for_byte}")
            print(f"Potential wasted space: {group.wasted_formatted}")

            for file_path in group.files:
                print(f"  - {file_path}")


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""

    parser = argparse.ArgumentParser(
        description="Find duplicate files in a directory or run collision demos."
    )

    parser.add_argument(
        "folder",
        type=Path,
        nargs="?",
        default=None,
        help="Folder to scan (optional; if omitted, terminal menu opens)."
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the Pigeonhole Principle & Hash Collision interactive demo."
    )

    parser.add_argument(
        "--min-size",
        type=parse_size_string,
        default=0,
        help="Minimum file size, e.g. 100B, 4KB, or 10MB."
    )

    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and folders."
    )

    parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Follow symbolic links."
    )

    parser.add_argument(
        "--no-byte-verify",
        action="store_true",
        help="Skip byte-for-byte verification."
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Show the summary without listing duplicate groups."
    )

    parser.add_argument(
        "--json",
        type=Path,
        metavar="OUTPUT",
        help="Export the report to a JSON file."
    )

    parser.add_argument(
        "--cleanup-script",
        type=Path,
        metavar="OUTPUT",
        help="Generate a review-only Bash cleanup script."
    )

    return parser


def run_interactive_menu() -> None:
    """Run interactive menu when no folder argument is provided."""
    while True:
        print("\n--- Main Menu ---")
        print("1. Scan directory for duplicate files")
        print("2. Run Pigeonhole Principle & Hash Collision Demonstration")
        print("3. Exit")

        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            folder_input = input("Enter directory path to scan (press Enter for 'test_folder'): ").strip()
            folder_path = Path(folder_input) if folder_input else Path("test_folder")

            if not folder_path.is_dir():
                print(f"Error: Directory not found or not a directory: {folder_path}")
                continue

            try:
                report = find_duplicates(
                    root_path=folder_path,
                    min_size_bytes=0,
                    include_hidden=False,
                    follow_symlinks=False,
                    verify_byte_by_byte=True,
                )
                display_report_cli(report, verbose=True)
            except Exception as error:
                print(f"Error during scan: {error}")

        elif choice == "2":
            run_interactive_demo()

        elif choice == "3":
            print("Exiting Duplicate File Detector.")
            break

        else:
            print("Invalid choice. Please select 1, 2, or 3.")


def main() -> None:
    """Main CLI entry point."""
    parser = build_arg_parser()
    args = parser.parse_args()

    print_banner()

    if args.demo:
        run_interactive_demo()
        return

    if args.folder is None:
        run_interactive_menu()
        return

    if not args.folder.is_dir():
        parser.error(f"Folder does not exist or is not a directory: {args.folder}")

    try:
        report = find_duplicates(
            root_path=args.folder,
            min_size_bytes=args.min_size,
            include_hidden=args.include_hidden,
            follow_symlinks=args.follow_symlinks,
            verify_byte_by_byte=not args.no_byte_verify,
        )

        display_report_cli(
            report,
            verbose=not args.quiet
        )

        if args.json:
            export_report_json(report, args.json)
            print(f"\nJSON report saved to: {args.json}")

        if args.cleanup_script:
            generate_safe_cleanup_script(report, args.cleanup_script)
            print(f"Review-only cleanup script saved to: {args.cleanup_script}")

    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()

