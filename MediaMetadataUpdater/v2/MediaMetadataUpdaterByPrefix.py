import os
import re
import argparse
import math
import subprocess
from datetime import datetime

# Regex for filename prefix: YYMMDDxxxx.ext
FILE_PREFIX_PATTERN = re.compile(r"^(\d{2})(\d{2})(\d{2})")

MEDIA_EXT = {
    ".jpg", ".jpeg", ".png", ".heic",
    ".mp4", ".mov", ".avi", ".mkv"
}


def parse_args():
    parser = argparse.ArgumentParser(description="Update timestamps based on YYMMDD filename prefixes (no subfolders, single-threaded)")

    parser.add_argument(
        "--dir",
        required=True,
        help="Comma-separated list of directories to scan (non-recursive)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without modifying files"
    )

    return parser.parse_args()


def get_existing_timestamp(file_path):
    """Return existing DateTimeOriginal as datetime object, or None."""
    try:
        result = subprocess.run(
            ["exiftool", "-s", "-s", "-s", "-DateTimeOriginal", file_path],
            capture_output=True,
            text=True
        )
        value = result.stdout.strip()
        if not value:
            return None
        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        return None


def update_timestamp(file_path, dt_string):
    """Run exiftool to update timestamps."""
    subprocess.run([
        "exiftool",
        "-overwrite_original",
        f"-DateTimeOriginal={dt_string}",
        f"-AllDates={dt_string}",
        f"-CreationTime={dt_string}",
        f"-ModifyDate={dt_string}",
        file_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    args = parse_args()

    # Parse directories
    parent_dirs = [os.path.abspath(p.strip()) for p in args.dir.split(",") if p.strip()]

    tasks = []
    skipped_files = []

    print("Running in SAFE MODE (single-threaded, one file at a time)\n")

    for parent in parent_dirs:
        if not os.path.isdir(parent):
            print(f"Skipping invalid directory: {parent}")
            continue

        print(f"Scanning: {parent}")

        for file in os.listdir(parent):
            fpath = os.path.join(parent, file)

            if not os.path.isfile(fpath):
                continue

            ext = os.path.splitext(file)[1].lower()
            if ext not in MEDIA_EXT:
                skipped_files.append(file)
                continue

            # Extract YYMMDD from filename prefix
            m = FILE_PREFIX_PATTERN.match(file)
            if not m:
                print(f"  Skipping (no YYMMDD prefix): {file}")
                skipped_files.append(file)
                continue

            yy, mm, dd = m.groups()
            year = int("20" + yy)

            try:
                dt = datetime(year, int(mm), int(dd), 0, 0, 0)
            except ValueError:
                print(f"  Invalid date in filename prefix: {file}")
                skipped_files.append(file)
                continue

            dt_string = dt.strftime("%Y:%m:%d %H:%M:%S")

            tasks.append((fpath, file, dt, dt_string))

    print(f"\nTotal files to process: {len(tasks)}")
    print(f"Skipped (not media or invalid prefix): {len(skipped_files)}\n")

    converted = []
    errors = []
    dryrun_list = []
    skipped_correct = []

    # SAFE MODE: process files sequentially
    for fpath, fname, dt_target, dt_string in tasks:

        print(f"Processing: {fname}")

        # Read existing timestamp
        existing = get_existing_timestamp(fpath)

        # Skip if timestamp already matches
        if existing and existing == dt_target:
            print(f"Skipped (already correct): {fname}")
            skipped_correct.append(fname)
            continue

        if args.dry_run:
            print(f"Dry-run: {fname}")
            dryrun_list.append(fname)
            continue

        try:
            update_timestamp(fpath, dt_string)
            print(f"Converted: {fname}")
            converted.append(fname)
        except Exception:
            print(f"Error: {fname}")
            errors.append(fname)

    # Summary
    print("\nSummary:")
    print("--------")
    if args.dry_run:
        print(f"Dry-run only (no changes made): {len(dryrun_list)}")
    else:
        print(f"Converted: {len(converted)}")
        print(f"Already correct: {len(skipped_correct)}")
        print(f"Errors: {len(errors)}")
    print(f"Skipped (invalid or non-media): {len(skipped_files)}")

    if args.dry_run and dryrun_list:
        print("\nDry-run files:")
        for f in dryrun_list:
            print(f"  {f}")

    if skipped_correct:
        print("\nAlready correct:")
        for f in skipped_correct:
            print(f"  {f}")

    if converted:
        print("\nConverted files:")
        for f in converted:
            print(f"  {f}")

    if errors:
        print("\nErrors:")
        for f in errors:
            print(f"  {f}")

    print("\nDone.")


if __name__ == "__main__":
    main()
