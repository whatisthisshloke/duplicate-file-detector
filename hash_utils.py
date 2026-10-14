"""
hash_utils.py - Hash Generation and Byte Verification Utilities
================================================================
Function declarations and signatures for SHA-256 computation,
partial hashing, byte-for-byte stream verification, and toy hash functions.
"""

from pathlib import Path
from typing import Union
import hashlib


DEFAULT_CHUNK_SIZE = 64 * 1024  # 64 KB read buffer
PARTIAL_SAMPLE_SIZE = 4 * 1024  # 4 KB prefix sample


def format_bytes(byte_count: int) -> str:
    """
    Format byte count into a human-readable string (B, KB, MB, GB, TB).
    """
    if byte_count < 0:
        raise ValueError("Byte count cannot be negative")

    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(byte_count)

    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{byte_count} B"


def compute_file_sha256(file_path: Union[str, Path], chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    """
    Compute full SHA-256 checksum of a file by streaming chunks.
    Maintains O(1) memory footprint for arbitrarily large files.
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero")

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            sha256.update(chunk)

    return sha256.hexdigest()


def compute_partial_hash(file_path: Union[str, Path], sample_size: int = PARTIAL_SAMPLE_SIZE) -> str:
    """
    Compute a fast partial SHA-256 hash of a file's head and tail
    as an early filtering heuristic before full-file hashing.
    """
    if sample_size <= 0:
        raise ValueError("Sample size must be greater than zero")

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        file.seek(0, 2)
        file_size = file.tell()

        if file_size <= 2 * sample_size:
            file.seek(0)
            sha256.update(file.read())
        else:
            file.seek(0)
            head = file.read(sample_size)
            sha256.update(head)

            file.seek(-sample_size, 2)
            tail = file.read(sample_size)
            sha256.update(tail)

    return sha256.hexdigest()


def compare_files_byte_by_byte(file1: Union[str, Path], file2: Union[str, Path], chunk_size: int = DEFAULT_CHUNK_SIZE) -> bool:
    """
    Compare two files byte by byte.
    Return True if their contents are identical, otherwise False.
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero")

    try:
        if Path(file1).resolve() == Path(file2).resolve():
            return True
    except OSError:
        pass

    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        while True:
            chunk1 = f1.read(chunk_size)
            chunk2 = f2.read(chunk_size)

            if chunk1 != chunk2:
                return False

            if not chunk1:
                return True


def toy_hash(data: Union[str, bytes, Path], num_buckets: int = 16) -> int:
    """
    A simple toy hash function mapping arbitrary input to a finite set of buckets.
    Demonstrates the Pigeonhole Principle when inputs N > num_buckets K.
    """
    if num_buckets <= 0:
        raise ValueError("Number of buckets must be greater than zero")

    if isinstance(data, Path):
        data = data.read_bytes()
    elif isinstance(data, str):
        data = data.encode("utf-8")

    total = sum(data)

    return total % num_buckets

