import os
import re
import argparse
import math
import subprocess
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

# Regex for subdirectory names: YYMMDD
DIR_PATTERN = re.compile(r"^(\d{2})(\d{2})(\d{2})$")

MEDIA_EXT = {
    ".jpg", ".jpeg", ".png", ".heic",
    ".mp4", ".mov", ".avi", ".mkv"
}


def parse_args():
    parser = argparse.ArgumentParser(description="Update timestamps based on YYMMDD folder names")

    parser.add_argument(
        "--dir",
        required=True,
        help="Comma-separated list of directories to scan (non-recursive)"
    )

    parser.add_argument(
        "--workers",
        default="80",
        help="Percentage of CPU threads to use (e.g., 50, 80, 100) or 'all'"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without modifying files"
    )

    return parser.parse_args()


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


def process_file(task):
    """Worker function for multiprocessing."""
    file_path, dt_string, dry_run = task

    if dry_run:
        return ("dry", os.path.basename(file_path))

    try:
        update_timestamp(file_path, dt_string)
        return ("ok", os.path.basename(file_path))
    except Exception:
        return ("error", os.path.basename(file_path))


def main():
    args = parse_args()

    # Determine worker count
    total_threads = os.cpu_count() or 1
    if args.workers.lower() == "all":
        workers = total_threads
    else:
        try:
            pct = int(args.workers)
            pct = max(1, min(pct, 100))
            workers = max(1, math.floor(total_threads * (pct / 100)))
        except ValueError:
            workers = max(1, math.floor(total_threads * 0.8))

    print(f"Using {workers} worker processes out of {total_threads} available threads.\n")

    # Parse directories
    parent_dirs = [os.path.abspath(p.strip()) for p in args.dir.split(",") if p.strip()]

    tasks = []
    skipped_files = []

    for parent in parent_dirs:
        if not os.path.isdir(parent):
            print(f"Skipping invalid directory: {parent}")
            continue

        print(f"Scanning: {parent}")

        for entry in os.listdir(parent):
            subdir = os.path.join(parent, entry)

            if not os.path.isdir(subdir):
                continue

            m = DIR_PATTERN.match(entry)
            if not m:
                print(f"  Skipping (not YYMMDD): {entry}")
                continue

            yy, mm, dd = m.groups()
            year = int("20" + yy)

            try:
                dt = datetime(year, int(mm), int(dd), 0, 0, 0)
            except ValueError:
                print(f"  Invalid date folder: {entry}")
                continue

            dt_string = dt.strftime("%Y:%m:%d %H:%M:%S")
            print(f"  Folder {entry} → timestamp {dt_string}")

            # Collect tasks
            for file in os.listdir(subdir):
                fpath = os.path.join(subdir, file)

                if not os.path.isfile(fpath):
                    continue

                ext = os.path.splitext(file)[1].lower()
                if ext not in MEDIA_EXT:
                    skipped_files.append(file)
                    continue

                tasks.append((fpath, dt_string, args.dry_run))

    print(f"\nTotal files to process: {len(tasks)}")
    print(f"Skipped (not media): {len(skipped_files)}\n")

    converted = []
    errors = []
    dryrun_list = []

    # Run updates in parallel with live logs
    if tasks:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(process_file, t) for t in tasks]

            for future in as_completed(futures):
                status, fname = future.result()

                if status == "ok":
                    print(f"Converted: {fname}")
                    converted.append(fname)

                elif status == "error":
                    print(f"Error: {fname}")
                    errors.append(fname)

                elif status == "dry":
                    print(f"Dry-run: {fname}")
                    dryrun_list.append(fname)

    # Summary
    print("\nSummary:")
    print("--------")
    if args.dry_run:
        print(f"Dry-run only (no changes made): {len(dryrun_list)}")
    else:
        print(f"Converted: {len(converted)}")
        print(f"Errors: {len(errors)}")
    print(f"Skipped: {len(skipped_files)}")

    if args.dry_run and dryrun_list:
        print("\nDry-run files:")
        for f in dryrun_list:
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