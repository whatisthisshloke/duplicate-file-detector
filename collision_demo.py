"""
collision_demo.py - Pigeonhole Principle & Hash Collision Demonstration
=======================================================================
MFCS (Mathematical Foundations of Computer Science) Educational Module

Demonstrates the Pigeonhole Principle (Dirichlet's Box Principle) through
finite hash spaces, visual bucket distributions, and collision generation.

Theorem:
If N items (pigeons) are placed into K buckets (pigeonholes) where N > K,
at least one bucket must contain >= ceil(N / K) items.
"""


BANNER = """
========================================================================
        MATHEMATICAL FOUNDATIONS OF COMPUTER SCIENCE (MFCS)
            THE PIGEONHOLE PRINCIPLE & HASH COLLISIONS
========================================================================
"""



from typing import Dict, List, Optional
from pathlib import Path
import hashlib

from hash_utils import toy_hash, compute_file_sha256, compare_files_byte_by_byte


def demonstrate_pigeonhole_principle(
    sample_items: List[str],
    num_buckets: int = 16
) -> Dict[int, List[str]]:
    """
    Map sample items to finite buckets using toy_hash and display collisions.
    Verifies Dirichlet's Box Principle: max items in any bucket >= ceil(N / K).
    """
    if num_buckets <= 0:
        raise ValueError("Number of buckets must be greater than zero")

    if not sample_items:
        print("\nNo items provided for Pigeonhole Principle demonstration.")
        return {}

    buckets: Dict[int, List[str]] = {}

    for item in sample_items:
        bucket_number = toy_hash(item, num_buckets)

        if bucket_number not in buckets:
            buckets[bucket_number] = []

        buckets[bucket_number].append(item)

    print("\n--- Hash Bucket Distribution ---")
    collision_count = 0
    for bucket in sorted(buckets.keys()):
        items = buckets[bucket]
        collision_note = ""
        if len(items) > 1:
            collision_note = f" <- COLLISION! ({len(items)} items share bucket {bucket})"
            collision_count += 1
        print(f"Bucket {bucket:2d}: {items}{collision_note}")

    minimum_max_size = (len(sample_items) + num_buckets - 1) // num_buckets
    largest_bucket = max(len(items) for items in buckets.values())

    print(f"\n--- Pigeonhole Principle Verification ---")
    print(f"Number of items (pigeons N): {len(sample_items)}")
    print(f"Number of buckets (pigeonholes K): {num_buckets}")
    print(f"Minimum guaranteed maximum bucket size (ceil(N / K)): {minimum_max_size}")
    print(f"Actual largest bucket size: {largest_bucket}")
    print(f"Total collided buckets: {collision_count}")

    assert largest_bucket >= minimum_max_size, (
        f"Pigeonhole Principle violation: {largest_bucket} < {minimum_max_size}"
    )

    return buckets


def demonstrate_sha256_comparison(first: str = "listen", second: str = "silent") -> None:
    """
    Compare toy hash with SHA-256 using colliding inputs.
    Explains why Stage 4 byte-verification is required.
    """
    print("\n========== TOY HASH VS SHA-256 COMPARISON ==========")
    print(f"Comparing inputs: '{first}' and '{second}'")

    toy_first = toy_hash(first, 16)
    toy_second = toy_hash(second, 16)

    real_first = hashlib.sha256(first.encode("utf-8")).hexdigest()
    real_second = hashlib.sha256(second.encode("utf-8")).hexdigest()

    print(f"\n1. Toy Hash (16 buckets):")
    print(f"   toy_hash('{first}')  = {toy_first}")
    print(f"   toy_hash('{second}') = {toy_second}")

    if toy_first == toy_second and first != second:
        print("   -> COLLISION DETECTED! Two distinct strings produced the identical toy hash.")
    else:
        print(f"   -> Toy hashes are: {toy_first} and {toy_second}")

    print(f"\n2. Cryptographic SHA-256 (2^256 states):")
    print(f"   sha256('{first}')  = {real_first}")
    print(f"   sha256('{second}') = {real_second}")

    if real_first == real_second:
        print("   -> SHA-256 Collision!")
    else:
        print("   -> Distinct SHA-256 digests.")

    print("\n3. Mathematical Insight (Pigeonhole Principle):")
    print("   The input domain of arbitrary files is INFINITE, but the SHA-256 output space")
    print("   is FINITE (2^256 values). By the Pigeonhole Principle, collisions mathematically")
    print("   MUST exist for SHA-256 as well.")
    print("   Therefore, our detector performs Stage 4 byte-by-byte exact verification")
    print("   to guarantee 100% precision and zero false positives.")


def demonstrate_files_collision(file1: Path, file2: Path) -> None:
    """
    Demonstrate toy hash, SHA-256, and byte comparison on actual files.
    """
    file1 = Path(file1)
    file2 = Path(file2)

    if not file1.is_file() or not file2.is_file():
        print(f"Error: One or both files do not exist: {file1}, {file2}")
        return

    print("\n========== FILE COMPARISON & COLLISION TEST ==========")
    print(f"File 1: {file1.name} ({file1.stat().st_size} bytes)")
    print(f"File 2: {file2.name} ({file2.stat().st_size} bytes)")

    toy1 = toy_hash(file1, 16)
    toy2 = toy_hash(file2, 16)

    sha1 = compute_file_sha256(file1)
    sha2 = compute_file_sha256(file2)

    identical = compare_files_byte_by_byte(file1, file2)

    print(f"\n- Toy Hash (16 buckets):")
    print(f"    File 1: {toy1}")
    print(f"    File 2: {toy2}")
    if toy1 == toy2:
        print("    -> TOY HASH COLLISION (Identical bucket)")

    print(f"\n- Cryptographic SHA-256:")
    print(f"    File 1: {sha1}")
    print(f"    File 2: {sha2}")
    if sha1 == sha2:
        print("    -> SHA-256 MATCH")
    else:
        print("    -> SHA-256 MISMATCH")

    print(f"\n- Stage 4 Byte-by-Byte Verification:")
    print(f"    Identical content: {identical}")


def run_interactive_demo() -> None:
    print(BANNER)

    default_words = [
        "apple", "banana", "cherry", "date", "fig", "grape",
        "kiwi", "lemon", "mango", "orange", "peach", "pear",
        "plum", "berry", "melon", "papaya", "lime", "coconut"
    ]

    while True:
        print("\n1. Pigeonhole Principle and collisions")
        print("2. Toy hash vs SHA-256 collision comparison")
        print("3. Compare files in test_folder")
        print("4. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            user_input = input("Enter words separated by commas (press Enter for default 18 words): ").strip()
            if user_input:
                words = [w.strip() for w in user_input.split(",") if w.strip()]
            else:
                words = default_words
                print(f"Using {len(words)} default words.")
            demonstrate_pigeonhole_principle(words)


        elif choice == "2":
            user_pair = input("Enter 2 words separated by comma (press Enter for 'listen, silent'): ").strip()
            if user_pair and "," in user_pair:
                w1, w2 = [w.strip() for w in user_pair.split(",", 1)]
                demonstrate_sha256_comparison(w1, w2)
            else:
                demonstrate_sha256_comparison("listen", "silent")

        elif choice == "3":
            test_dir = Path("test_folder")
            files = [f for f in test_dir.iterdir() if f.is_file()] if test_dir.is_dir() else []
            if len(files) >= 2:
                demonstrate_files_collision(files[0], files[1])
            else:
                print("test_folder needs at least 2 files to compare.")

        elif choice == "4":
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    run_interactive_demo()

