#!/usr/bin/env python3
import argparse
import os
import shutil


# ==========================
# ARGUMENT PARSER
# ==========================
def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract files from first-level subdirectories back to the parent directory."
    )
    parser.add_argument("--dir", required=True, help="Parent directory to scan.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simulate actions without moving any files.")
    return parser.parse_args()


# ==========================
# SCANNING LOGIC
# ==========================
def scan_subdirectories(base_dir: str):
    """
    Scan only the first-level subdirectories and count files.
    """
    print(f"[INFO] Scanning subdirectories in: {base_dir}")

    try:
        entries = os.listdir(base_dir)
    except Exception as e:
        print(f"[ERROR] Unable to list directory: {e}")
        return {}, 0

    subdirs = [
        d for d in entries
        if os.path.isdir(os.path.join(base_dir, d))
    ]

    file_map = {}
    total_files = 0

    for sub in sorted(subdirs):
        sub_path = os.path.join(base_dir, sub)

        try:
            files = [
                f for f in os.listdir(sub_path)
                if os.path.isfile(os.path.join(sub_path, f))
            ]
        except Exception as e:
            print(f"[WARN] Unable to read {sub_path}: {e}")
            continue

        file_map[sub] = files
        total_files += len(files)

        print(f"[SCAN] {sub}: {len(files)} files")

    print(f"\n[INFO] Total subdirectories: {len(subdirs)}")
    print(f"[INFO] Total files found: {total_files}\n")

    return file_map, total_files


# ==========================
# SUMMARY OUTPUT
# ==========================
def print_summary(file_map: dict, total_files: int):
    print("===== SUMMARY =====\n")

    for sub, files in sorted(file_map.items()):
        print(f"Directory: {sub}")
        print(f"Files: {len(files)}\n")

    print(f"TOTAL FILES TO MOVE: {total_files}\n")


# ==========================
# MOVE LOGIC (LINEAR)
# ==========================
def move_files(base_dir: str, file_map: dict, total_files: int, dry_run: bool):
    """
    Move files from subdirectories to the parent directory.
    Linear, safe, one-by-one.
    """
    if dry_run:
        print("[INFO] DRY RUN ENABLED — No files will be moved.\n")
    else:
        print("[INFO] Starting move operation...\n")

    moved = 0

    for sub, files in sorted(file_map.items()):
        sub_path = os.path.join(base_dir, sub)

        for f in files:
            src = os.path.join(sub_path, f)
            dst = os.path.join(base_dir, f)

            moved += 1

            if dry_run:
                print(f"[DRY-RUN] Would move {moved}/{total_files}: {f}")
            else:
                shutil.move(src, dst)
                print(f"[MOVE] Moving {moved}/{total_files}: {f}")

    print("\n===== MOVE REPORT =====\n")

    if dry_run:
        print(f"[DRY-RUN] {moved} files would have been moved to {base_dir}")
    else:
        print(f"{moved} files have been moved to {base_dir}")


# ==========================
# MAIN
# ==========================
def main():
    args = parse_args()
    base_dir = args.dir

    file_map, total_files = scan_subdirectories(base_dir)

    if total_files == 0:
        print("[INFO] No files found in subdirectories. Nothing to move.")
        return

    print_summary(file_map, total_files)

    confirm = input("Proceed with moving files? Type 'yes' to continue: ").strip()
    if confirm != "yes":
        print("[INFO] Move operation aborted.")
        return

    move_files(base_dir, file_map, total_files, args.dry_run)


if __name__ == "__main__":
    main()