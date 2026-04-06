#!/usr/bin/env python3
import argparse
import os
import re
from pathlib import Path

EM_DASH = "—"
DATE_PATTERN = re.compile(r"-\d{8}_\d{6}$")  # matches -yyyymmdd_hhmmss at end


def replace_first_three_spaces(name: str) -> str:
    """Replace the first three whitespace occurrences with em-dash."""
    parts = name.split(" ")
    if len(parts) <= 1:
        return name

    new_name = ""
    replacements = 0

    for i, part in enumerate(parts):
        if i == 0:
            new_name = part
            continue

        if replacements < 3:
            new_name += EM_DASH + part
            replacements += 1
        else:
            new_name += " " + part

    return new_name


def remove_date_suffix(name: str) -> str:
    """Remove -yyyymmdd_hhmmss at the end of the folder name."""
    return DATE_PATTERN.sub("", name)


def process_directory(base_dir: Path, dry_run: bool):
    # Only operate on immediate subdirectories of base_dir
    for entry in base_dir.iterdir():
        if not entry.is_dir():
            continue

        original_name = entry.name
        new_name = original_name

        # Step 1: Replace first 3 spaces
        new_name = replace_first_three_spaces(new_name)

        # Step 2: Remove trailing date pattern
        new_name = remove_date_suffix(new_name)

        # Skip if no change
        if new_name == original_name:
            print(f"[SKIP] {original_name} → (no change)")
            continue

        print(f"[RENAME] {original_name} → {new_name}")

        if not dry_run:
            target_path = entry.parent / new_name
            entry.rename(target_path)


def main():
    parser = argparse.ArgumentParser(description="Rename subdirectories safely.")
    parser.add_argument("--dir", required=True, help="Directory whose immediate subdirectories will be renamed.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be renamed without applying changes.")
    args = parser.parse_args()

    base_dir = Path(args.dir).expanduser().resolve()

    if not base_dir.exists() or not base_dir.is_dir():
        print(f"ERROR: '{base_dir}' is not a valid directory.")
        return

    print(f"Target directory: {base_dir}")
    print(f"Dry-run mode: {args.dry_run}")
    print("-" * 60)

    process_directory(base_dir, args.dry_run)

    print("-" * 60)
    print("Completed.")


if __name__ == "__main__":
    main()