"""
test_duplicates.py - Unit and Integration Tests for Duplicate File Detector
=============================================================================
Tests covering directory scanning, size grouping, partial hashing,
full SHA-256 computation, byte-by-byte verification, collision demonstration,
and CLI utilities.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scanner import ScanResult, scan_directory
from hash_utils import (
    format_bytes,
    compute_file_sha256,
    compute_partial_hash,
    compare_files_byte_by_byte,
    toy_hash,
)
from duplicate_finder import (
    DuplicateGroup,
    DetectionReport,
    find_duplicates,
    export_report_json,
    generate_safe_cleanup_script,
)
from collision_demo import (
    demonstrate_pigeonhole_principle,
    demonstrate_birthday_paradox,
    demonstrate_sha256_comparison,
)
from main import parse_size_string


class TestHashUtils(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)

    def test_format_bytes(self):
        self.assertEqual(format_bytes(0), "0.00 B")
        self.assertEqual(format_bytes(500), "500.00 B")
        self.assertEqual(format_bytes(1024), "1.00 KB")
        self.assertEqual(format_bytes(1024 * 1024), "1.00 MB")
        self.assertEqual(format_bytes(1024 * 1024 * 1024), "1.00 GB")
        with self.assertRaises(ValueError):
            format_bytes(-1)

    def test_compute_file_sha256(self):
        file_path = Path(self.temp_dir) / "sample.txt"
        file_path.write_bytes(b"Hello, world!")
        expected_hash = "315f5bdb76d078c43b8ac0064e4a0164612b1fce77c869345bfc94c75894edd3"
        self.assertEqual(compute_file_sha256(file_path), expected_hash)

        with self.assertRaises(ValueError):
            compute_file_sha256(file_path, chunk_size=0)

    def test_compute_partial_hash(self):
        file_path = Path(self.temp_dir) / "sample.txt"
        file_path.write_bytes(b"A" * 10000)
        p_hash = compute_partial_hash(file_path, sample_size=100)
        self.assertIsInstance(p_hash, str)
        self.assertEqual(len(p_hash), 64)

        with self.assertRaises(ValueError):
            compute_partial_hash(file_path, sample_size=0)

    def test_compare_files_byte_by_byte(self):
        file1 = Path(self.temp_dir) / "file1.bin"
        file2 = Path(self.temp_dir) / "file2.bin"
        file3 = Path(self.temp_dir) / "file3.bin"

        file1.write_bytes(b"identical content" * 100)
        file2.write_bytes(b"identical content" * 100)
        file3.write_bytes(b"different content" * 100)

        self.assertTrue(compare_files_byte_by_byte(file1, file2))
        self.assertFalse(compare_files_byte_by_byte(file1, file3))
        self.assertTrue(compare_files_byte_by_byte(file1, file1))

    def test_toy_hash(self):
        self.assertEqual(toy_hash("a", 16), ord("a") % 16)
        # Anagrams collide under sum of ASCII values
        self.assertEqual(toy_hash("listen", 16), toy_hash("silent", 16))
        self.assertEqual(toy_hash(b"stop", 16), toy_hash(b"pots", 16))

        with self.assertRaises(ValueError):
            toy_hash("test", num_buckets=0)


class TestScanner(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.temp_dir)

    def test_scan_directory_basic(self):
        (self.temp_dir / "f1.txt").write_text("aaa")
        (self.temp_dir / "f2.txt").write_text("bbb")
        (self.temp_dir / "f3.txt").write_text("longer text")

        result = scan_directory(self.temp_dir)
        self.assertEqual(result.total_files_found, 3)
        self.assertEqual(len(result.size_groups[3]), 2)
        self.assertIn(3, result.candidate_size_groups)
        self.assertEqual(result.candidate_file_count, 2)
        self.assertEqual(result.pruned_unique_file_count, 1)

    def test_scan_directory_hidden_files(self):
        (self.temp_dir / ".hidden.txt").write_text("secret")
        (self.temp_dir / "normal.txt").write_text("public")

        res_no_hidden = scan_directory(self.temp_dir, include_hidden=False)
        self.assertEqual(res_no_hidden.total_files_found, 1)

        res_hidden = scan_directory(self.temp_dir, include_hidden=True)
        self.assertEqual(res_hidden.total_files_found, 2)

    def test_scan_directory_min_size(self):
        (self.temp_dir / "tiny.txt").write_bytes(b"123")
        (self.temp_dir / "large.txt").write_bytes(b"1234567890")

        result = scan_directory(self.temp_dir, min_size_bytes=5)
        self.assertEqual(result.total_files_found, 1)

    def test_scan_directory_errors(self):
        with self.assertRaises(FileNotFoundError):
            scan_directory(self.temp_dir / "nonexistent")

        file_path = self.temp_dir / "file.txt"
        file_path.write_text("hi")
        with self.assertRaises(NotADirectoryError):
            scan_directory(file_path)

        with self.assertRaises(ValueError):
            scan_directory(self.temp_dir, min_size_bytes=-1)


class TestDuplicateFinder(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.temp_dir)

    def test_find_duplicates_with_identical_and_different_files(self):
        content_a = b"Exact duplicate content here."
        content_b = b"Different content of same len"  # exactly 29 bytes

        (self.temp_dir / "copy1.txt").write_bytes(content_a)
        (self.temp_dir / "copy2.txt").write_bytes(content_a)
        (self.temp_dir / "same_size_diff_content.txt").write_bytes(content_b)
        (self.temp_dir / "unique_size.txt").write_bytes(b"short")

        report = find_duplicates(self.temp_dir)
        self.assertEqual(report.total_duplicate_groups, 1)
        self.assertEqual(report.total_duplicate_files, 2)
        self.assertEqual(report.redundant_files_count, 1)
        self.assertEqual(report.total_wasted_bytes, len(content_a))

        group = report.groups[0]
        self.assertEqual(group.size, len(content_a))
        self.assertTrue(group.verified_byte_for_byte)
        self.assertEqual(len(group.files), 2)

    def test_empty_files(self):
        (self.temp_dir / "empty1.txt").write_bytes(b"")
        (self.temp_dir / "empty2.txt").write_bytes(b"")

        report = find_duplicates(self.temp_dir)
        self.assertEqual(report.total_duplicate_groups, 1)
        self.assertEqual(report.groups[0].size, 0)

    def test_export_report_and_cleanup_script(self):
        (self.temp_dir / "d1.txt").write_bytes(b"test data")
        (self.temp_dir / "d2.txt").write_bytes(b"test data")

        report = find_duplicates(self.temp_dir)
        json_path = self.temp_dir / "report.json"
        script_path = self.temp_dir / "cleanup.sh"

        export_report_json(report, json_path)
        self.assertTrue(json_path.exists())

        generate_safe_cleanup_script(report, script_path)
        self.assertTrue(script_path.exists())
        content = script_path.read_text(encoding="utf-8")
        self.assertIn("#!/usr/bin/env bash", content)
        self.assertIn("# rm -- '", content)


class TestCollisionDemo(unittest.TestCase):
    def test_demonstrate_pigeonhole_principle(self):
        items = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
        buckets = demonstrate_pigeonhole_principle(items, num_buckets=4)
        # N = 9, K = 4 -> ceil(9/4) = 3
        max_size = max(len(v) for v in buckets.values())
        self.assertGreaterEqual(max_size, 3)

    def test_pigeonhole_empty_and_invalid(self):
        self.assertEqual(demonstrate_pigeonhole_principle([], num_buckets=4), {})
        with self.assertRaises(ValueError):
            demonstrate_pigeonhole_principle(["a"], num_buckets=0)

    def test_demonstrate_sha256_comparison(self):
        # Must execute without errors and compare colliding toy hashes
        demonstrate_sha256_comparison("listen", "silent")


class TestMainUtilities(unittest.TestCase):
    def test_parse_size_string(self):
        self.assertEqual(parse_size_string("500"), 500)
        self.assertEqual(parse_size_string("500B"), 500)
        self.assertEqual(parse_size_string("500 B"), 500)
        self.assertEqual(parse_size_string("10KB"), 10 * 1024)
        self.assertEqual(parse_size_string("10 KB"), 10 * 1024)
        self.assertEqual(parse_size_string("4MB"), 4 * 1024 * 1024)
        self.assertEqual(parse_size_string("4 MB"), 4 * 1024 * 1024)
        self.assertEqual(parse_size_string("1GB"), 1024 ** 3)

        with self.assertRaises(ValueError):
            parse_size_string("-10KB")

        with self.assertRaises(ValueError):
            parse_size_string("100XYZ")

        with self.assertRaises(ValueError):
            parse_size_string("")


if __name__ == "__main__":
    unittest.main()

