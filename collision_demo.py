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



from typing import Dict, List
import hashlib

def demonstrate_pigeonhole_principle(
    sample_items: List[str],
    num_buckets: int = 16
) -> Dict[int, List[str]]:

    buckets = {}

    for item in sample_items:
        bucket_number = sum(ord(char) for char in item) % num_buckets

        if bucket_number not in buckets:
            buckets[bucket_number] = []

        buckets[bucket_number].append(item)

    print("\n--- Hash Bucket Distribution ---")

    for bucket, items in buckets.items():
        print(f"Bucket {bucket}: {items}")
        if len(items) > 1:
            print("  COLLISION! Different items share this bucket.")

    if sample_items:
        minimum_max_size = (
            len(sample_items) + num_buckets - 1
        ) // num_buckets

        largest_bucket = max(len(items) for items in buckets.values())

        print(f"\nNumber of items: {len(sample_items)}")
        print(f"Number of buckets: {num_buckets}")
        print(f"Minimum guaranteed maximum bucket size: {minimum_max_size}")
        print(f"Actual largest bucket size: {largest_bucket}")

        assert largest_bucket >= minimum_max_size

    return buckets


def demonstrate_birthday_paradox(num_buckets: int = 256) -> None:
    print("\nBirthday Paradox:")
    print("With many items and a limited number of buckets,")
    print("collisions can occur even when items < buckets.")
    demonstrate_pigeonhole_principle(
        ["item" + str(i) for i in range(25)],
        num_buckets
    )


def demonstrate_sha256_comparison() -> None:
    print("\nToy hash versus SHA-256")

    first = "hello"
    second = "world"

    toy_first = sum(ord(c) for c in first) % 16
    toy_second = sum(ord(c) for c in second) % 16

    real_first = hashlib.sha256(first.encode()).hexdigest()
    real_second = hashlib.sha256(second.encode()).hexdigest()

    print(f"Toy hash of {first}: {toy_first}")
    print(f"Toy hash of {second}: {toy_second}")
    print(f"SHA-256 of {first}: {real_first}")
    print(f"SHA-256 of {second}: {real_second}")

    print("Hashes help identify candidates, but byte comparison")
    print("confirms whether file contents are exactly equal.")


def run_interactive_demo() -> None:
    print(BANNER)

    while True:
        print("\n1. Pigeonhole Principle and collisions")
        print("2. Birthday Paradox illustration")
        print("3. Toy hash vs SHA-256")
        print("4. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            words = input("Enter words separated by commas: ").split(",")
            words = [word.strip() for word in words if word.strip()]
            demonstrate_pigeonhole_principle(words)

        elif choice == "2":
            demonstrate_birthday_paradox()

        elif choice == "3":
            demonstrate_sha256_comparison()

        elif choice == "4":
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    run_interactive_demo()
