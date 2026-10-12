# Duplicate File Detector

A command-line application built in Python to identify duplicate files in a directory using file sizes, hashing, and content comparison. The project demonstrates how **hashing and the Pigeonhole Principle** can be applied to a practical computer science problem.

## Overview

Duplicate files can waste storage space and make file management difficult. This application scans a directory and its subdirectories to identify files that contain identical data.

It first groups files by size to reduce unnecessary comparisons, then uses cryptographic hashing to identify potential duplicates. Matching files can be checked by comparing their contents to ensure that they are truly identical.

The project also includes a demonstration of hash collisions to illustrate the Pigeonhole Principle.

## Features

- **Directory Scanning:** Scan a selected directory and its subdirectories for files.
- **Duplicate Detection:** Identify files with identical contents.
- **Hash-Based Comparison:** Use SHA-256 hashing to efficiently find potential matches.
- **Content Verification:** Compare file contents before classifying files as duplicates.
- **Storage Savings Report:** Estimate how much storage could be saved by removing redundant copies.
- **Hash Collision Demonstration:** Use a simple custom hash function to demonstrate how different inputs can produce the same hash value.
- **Command-Line Interface:** Interact with the application through a simple terminal menu.

> Note: Features will be marked as available once they have been implemented and tested.

## Mathematical Concepts Used

### 1. Hashing

A hash function maps input data to a hash value. In this project, SHA-256 is used to generate a hash for each candidate file.

Files with different sizes can be separated immediately. Files with the same size can then be compared using their hashes, reducing the number of expensive content comparisons.

### 2. Pigeonhole Principle

The Pigeonhole Principle states that if more objects are placed into fewer containers, at least one container must contain more than one object.

In the collision demonstration, multiple inputs are mapped into a limited number of possible hash values. If there are more inputs than possible hash values, at least two inputs must share a hash value.

This demonstrates why a hash match alone is not a mathematical guarantee that two files are identical.

## Technologies Used

- **Language:** Python
- **Hashing:** Python's `hashlib` module
- **File Handling:** Python's `pathlib` module
- **Data Processing:** Python standard library

The core application is designed to work without external Python packages.

## Project Structure

```text
duplicate-file-detector/
├── main.py                 # Application entry point and CLI menu
├── scanner.py              # Directory and file scanning
├── duplicate_finder.py     # Duplicate detection logic
├── hash_utils.py           # Hashing utilities
├── collision_demo.py       # Pigeonhole Principle demonstration
├── tests/
│   └── test_duplicates.py  # Tests for duplicate detection
├── README.md               # Project documentation
├── .gitignore              # Files excluded from Git
└── requirements.txt        # External dependencies, if any
```

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- Git
- A terminal or command prompt

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/duplicate-file-detector.git
cd duplicate-file-detector
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Run the application

Once the implementation is complete, run:

```bash
python main.py
```

Follow the instructions displayed in the terminal.

## How It Works

1. The user selects a directory to scan.
2. The application discovers files in that directory and its subdirectories.
3. Files are grouped by size, since files with different sizes cannot have identical contents.
4. Candidate files are hashed using SHA-256.
5. Files with matching hashes are verified by comparing their contents.
6. The application displays groups of duplicate files and estimates potential storage savings.
7. The user can run the collision demonstration to explore the Pigeonhole Principle.

## Testing

Testing will include:

- Directories containing no duplicate files.
- Directories containing multiple copies of the same file.
- Files with the same name but different contents.
- Files with different sizes.
- Empty files.
- Hash collision examples using the custom demonstration function.

Tests should be run on sample directories created specifically for testing.

## Safety and Limitations

- The application identifies duplicates but does not automatically delete files.
- Files that cannot be accessed may need to be skipped or reported.
- Hashing helps identify candidates, while content comparison provides an additional verification step.
- The custom collision demonstration uses a simplified hash function for educational purposes; it is not intended for real-world security.
- Potential storage savings are estimates based on duplicate file groups.

## Project Objective

The objective of this project is to apply discrete mathematics concepts to a real-world computing problem while developing practical skills in Python programming, file handling, hashing, testing, and software development.

## 👥 Contributors

- **[Shloke Ghoshal]**
- **[Prasit Raithatha]**
