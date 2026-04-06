import os
import argparse

# ANSI color codes
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"      # used as "orange" replacement
RESET = "\033[0m"

def list_folders(path):
    """Return a list of folder names (1 level only) inside `path`."""
    return [
        name for name in os.listdir(path)
        if os.path.isdir(os.path.join(path, name))
    ]

def clean_dst(dst, dry_run):
    """Delete only empty subdirectories in dst. Log non-empty ones."""
    print("\n[STEP] Checking existing folders in --dst")
    folders = list_folders(dst)

    if not folders:
        print("No existing folders found in dst.")
        return

    for folder in folders:
        folder_path = os.path.join(dst, folder)
        contents = os.listdir(folder_path)

        if len(contents) == 0:
            if dry_run:
                print(f"{RED}DRY RUN → Would delete empty folder:{RESET} {folder_path}")
            else:
                print(f"{RED}Deleted empty folder:{RESET} {folder_path}")
                os.rmdir(folder_path)
        else:
            print(f"{CYAN}Non-empty folder kept:{RESET} {folder_path} "
                  f"({len(contents)} item(s))")

def mirror_folders(src, dst, dry_run):
    """Create empty folders in dst that mirror the top-level folders in src."""
    print("\n[STEP] Reading folders from --src")
    folders = list_folders(src)

    print(f"Found {len(folders)} folder(s) in source:")
    for f in folders:
        print(f"  - {f}")

    print("\n[STEP] Creating folders in --dst")
    for folder in folders:
        dst_path = os.path.join(dst, folder)

        if os.path.exists(dst_path):
            if os.listdir(dst_path):
                print(f"{YELLOW}SKIP: Folder already exists and is NOT empty{RESET} → {dst_path}")
            else:
                print(f"{YELLOW}EXISTS (empty){RESET}: {dst_path}")
            continue

        if dry_run:
            print(f"{GREEN}DRY RUN → Would create:{RESET} {dst_path}")
        else:
            os.makedirs(dst_path)
            print(f"{GREEN}Created:{RESET} {dst_path}")

def main():
    parser = argparse.ArgumentParser(description="Mirror top-level folders from src to dst.")
    parser.add_argument("--src", required=True, help="Absolute path to source directory")
    parser.add_argument("--dst", required=True, help="Absolute path to destination directory")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simulate actions without deleting or creating anything")
    args = parser.parse_args()

    print("\n=== START: Folder Mirror Utility ===")
    if args.dry_run:
        print(f"{YELLOW}DRY RUN MODE ENABLED — No changes will be made{RESET}")

    clean_dst(args.dst, args.dry_run)
    mirror_folders(args.src, args.dst, args.dry_run)

    print("\n=== DONE ===")

if __name__ == "__main__":
    main()