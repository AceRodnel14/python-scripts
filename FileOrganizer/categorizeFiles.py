#!/usr/bin/env python3
import argparse
import os
import json
import math
import shutil
import threading
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

# ==========================
# CONFIGURABLE PREFIX
# ==========================
SUBDIR_PREFIX = "AUTO "


# ANSI colors
COLOR_NAME = "\033[96m"
COLOR_RESET = "\033[0m"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Categorize files by <name><separator><random> prefix (no recursion)."
    )
    parser.add_argument("--dir", required=True, help="Directory to scan (non-recursive).")
    parser.add_argument("--separator", required=True, help="Separator string.")
    parser.add_argument("--create-json", help="Write JSON summary to this file.")
    parser.add_argument("--detailed", action="store_true",
                        help="Include list of files in JSON output.")
    parser.add_argument("--parallel-scan", action="store_true",
                        help="Enable parallel scanning of filenames.")
    parser.add_argument(
        "--workers",
        default="80",
        help="Percentage of CPU threads to use (e.g., 50, 80, 100) or 'all'"
    )
    parser.add_argument("--move", action="store_true",
                        help="Move files into categorized subdirectories.")
    return parser.parse_args()


def compute_workers(arg_workers: str):
    total_threads = os.cpu_count() or 1

    if arg_workers.lower() == "all":
        workers = total_threads
    else:
        try:
            pct = int(arg_workers)
            pct = max(1, min(pct, 100))
            workers = max(1, math.floor(total_threads * (pct / 100)))
        except ValueError:
            workers = max(1, math.floor(total_threads * 0.8))

    print(f"[INFO] Using {workers} worker processes out of {total_threads} available threads.")
    return workers


def extract_name_from_filename(filename: str, separator: str):
    if separator not in filename:
        return None

    name = filename.split(separator, 1)[0]

    # <name> must not be empty
    if not name.strip():
        return None

    return (name, filename)


def progress_bar(processed, total):
    print(f"[PROGRESS] Processed {processed}/{total} files")


def crawl_directory(directory: str, separator: str, parallel: bool, workers: int):
    print(f"[INFO] Scanning directory: {directory}")
    print(f"[INFO] Using separator: '{separator}'")

    try:
        entries = os.listdir(directory)
    except Exception as e:
        print(f"[ERROR] Unable to list directory: {e}")
        return defaultdict(list)

    files = [
        entry for entry in entries
        if os.path.isfile(os.path.join(directory, entry))
    ]

    total = len(files)
    processed = 0
    lock = threading.Lock()

    name_map = defaultdict(list)

    if not parallel:
        for f in files:
            result = extract_name_from_filename(f, separator)
            if result:
                name, filename = result
                name_map[name].append(filename)

            with lock:
                processed += 1
                progress_bar(processed, total)

        return name_map

    print("[INFO] Parallel scan enabled.")

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(extract_name_from_filename, f, separator): f
            for f in files
        }

        for future in as_completed(futures):
            result = future.result()
            if result:
                name, filename = result
                name_map[name].append(filename)

            with lock:
                processed += 1
                progress_bar(processed, total)

    return name_map


def shorten_path(path: str):
    parts = path.replace("\\", "/").split("/")
    if len(parts) <= 3:
        return path
    return ".../" + "/".join(parts[-3:])


def determine_destination_dirs(base_dir: str, names: list):
    subdirs = [
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d))
    ]

    result = {}

    for name in names:
        matches = [d for d in subdirs if name in d]

        if matches:
            matches.sort()
            chosen = matches[0]
            result[name] = os.path.join(base_dir, chosen)
        else:
            new_dir = os.path.join(base_dir, f"{SUBDIR_PREFIX}{name}")
            result[name] = new_dir

    return result


def print_move_summary(separator: str, name_map: dict, dest_map: dict):
    print("\n===== SUMMARY =====")
    print(f"Separator: {separator}\n")

    for name, files in sorted(name_map.items()):
        colored_name = f"{COLOR_NAME}{name}{COLOR_RESET}"
        dest = dest_map[name]
        short_dest = shorten_path(dest)

        print(f"Name: {colored_name}")
        print(f"Count: {len(files)}")
        print(f"Will be moved to: {short_dest}\n")


def move_files(base_dir: str, name_map: dict, dest_map: dict):
    final_report = {}

    for name, files in sorted(name_map.items()):
        dest = dest_map[name]

        if not os.path.exists(dest):
            os.makedirs(dest, exist_ok=True)

        total = len(files)
        moved = 0

        for f in files:
            src = os.path.join(base_dir, f)
            dst = os.path.join(dest, f)

            shutil.move(src, dst)
            moved += 1
            print(f"[MOVE] Moving {moved}/{total}: {f}")

        final_report[name] = (moved, dest)

    return final_report


def print_final_report(report: dict):
    print("\n===== MOVE REPORT =====\n")

    for name, (count, dest) in sorted(report.items()):
        short_dest = shorten_path(dest)
        print(f"{name}: {count} files have been moved to {short_dest}")


def build_json_summary(separator: str, name_map: dict, detailed: bool):
    matches = []

    for name, files in sorted(name_map.items()):
        entry = {
            "name": name,
            "count": len(files)
        }
        if detailed:
            entry["files"] = sorted(files)

        matches.append(entry)

    return {
        "separator": separator,
        "matches": matches
    }


def write_json_file(path: str, data: dict):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[INFO] JSON summary written to: {path}")
    except Exception as e:
        print(f"[ERROR] Failed to write JSON file: {e}")


def main():
    args = parse_args()

    workers = compute_workers(args.workers) if args.parallel_scan else 1

    print("[INFO] Starting analysis...")
    name_map = crawl_directory(
        args.dir,
        args.separator,
        args.parallel_scan,
        workers
    )

    print("[INFO] Analysis complete.")

    # MOVE MODE
    if args.move:
        names = sorted(name_map.keys())
        dest_map = determine_destination_dirs(args.dir, names)

        print_move_summary(args.separator, name_map, dest_map)

        confirm = input("Proceed with moving files? Type 'yes' to continue: ").strip()
        if confirm != "yes":
            print("[INFO] Move operation aborted.")
            return

        report = move_files(args.dir, name_map, dest_map)
        print_final_report(report)
        return

    # JSON MODE (only if --move is NOT present)
    print("\n===== SUMMARY =====")
    print(f"Separator: {args.separator}\n")

    for name, files in sorted(name_map.items()):
        colored_name = f"{COLOR_NAME}{name}{COLOR_RESET}"
        print(f"Name: {colored_name}")
        print(f"Count: {len(files)}\n")

    summary = build_json_summary(args.separator, name_map, args.detailed)

    if args.create_json:
        write_json_file(args.create_json, summary)


if __name__ == "__main__":
    main()