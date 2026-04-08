import os
import argparse

# ANSI color codes
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RESET = "\033[0m"

def list_folders(path):
    """Return a list of folder names (1 level only) inside `path`."""
    return [
        name for name in os.listdir(path)
        if os.path.isdir(os.path.join(path, name))
    ]

def scan_directory(parent):
    """Return (empty_folders, non_empty_folders)."""
    empty = []
    non_empty = []

    folders = list_folders(parent)
    for folder in folders:
        folder_path = os.path.join(parent, folder)
        contents = os.listdir(folder_path)

        if len(contents) == 0:
            empty.append(folder_path)
        else:
            non_empty.append((folder_path, len(contents)))

    return empty, non_empty

def clean_directory(parent, dry_run):
    print("\n[STEP] Scanning subdirectories in --dir")

    empty_folders, non_empty_folders = scan_directory(parent)

    # Log non-empty folders
    for path, count in non_empty_folders:
        print(f"{CYAN}Non-empty folder kept:{RESET} {path} ({count} item(s))")

    # Log empty folders
    for path in empty_folders:
        if dry_run:
            print(f"{RED}DRY RUN → Would delete empty folder:{RESET} {path}")
        else:
            print(f"{RED}Empty folder detected:{RESET} {path}")

    if not empty_folders:
        print("\nNo empty folders found.")
        return

    # If dry-run, stop here
    if dry_run:
        print(f"\n{YELLOW}DRY RUN MODE — No deletions performed{RESET}")
        return

    # Ask for confirmation
    print(f"\n{YELLOW}Found {len(empty_folders)} empty folder(s).{RESET}")
    answer = input("Type 'yes' to delete them: ").strip().lower()

    if answer != "yes":
        print(f"{YELLOW}Aborted — No folders were deleted{RESET}")
        return

    # Perform deletions
    print("\n[STEP] Deleting empty folders")
    for path in empty_folders:
        os.rmdir(path)
        print(f"{RED}Deleted:{RESET} {path}")

def main():
    parser = argparse.ArgumentParser(description="Delete empty subdirectories in a directory.")
    parser.add_argument("--dir", required=True, help="Absolute path to parent directory")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simulate actions without deleting anything")
    args = parser.parse_args()

    print("\n=== START: Empty Folder Cleanup Utility ===")
    if args.dry_run:
        print(f"{YELLOW}DRY RUN MODE ENABLED — No changes will be made{RESET}")

    clean_directory(args.dir, args.dry_run)

    print("\n=== DONE ===")

if __name__ == "__main__":
    main()