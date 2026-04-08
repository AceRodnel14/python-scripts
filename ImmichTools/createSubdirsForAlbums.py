import os
import argparse
import json
import re
from pathlib import Path
from urllib.request import urlopen, Request

# ---------------------------------------
# ANSI COLORS
# ---------------------------------------
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RESET = "\033[0m"

# ---------------------------------------
# SANITIZATION RULES
# ---------------------------------------
ILLEGAL_CHARS = r'[\\/:*?"<>|]'

def sanitize_folder_name(name: str) -> str:
    cleaned = re.sub(ILLEGAL_CHARS, "", name)
    return cleaned.strip()

# ---------------------------------------
# LIST SUBDIRECTORIES
# ---------------------------------------
def list_folders(path: Path):
    return [p for p in path.iterdir() if p.is_dir()]

# ---------------------------------------
# DELETE EMPTY SUBDIRECTORIES
# ---------------------------------------
def clean_existing_dirs(base_dir: Path, dry_run: bool):
    print("\n[STEP] Checking existing folders in --dir")

    folders = list_folders(base_dir)
    if not folders:
        print("No existing folders found.")
        return

    for folder in folders:
        contents = list(folder.iterdir())

        if len(contents) == 0:
            if dry_run:
                print(f"{RED}DRY RUN → Would delete empty folder:{RESET} {folder}")
            else:
                folder.rmdir()
                print(f"{RED}Deleted empty folder:{RESET} {folder}")
        else:
            print(f"{CYAN}Non-empty folder kept:{RESET} {folder} ({len(contents)} item(s))")

# ---------------------------------------
# FETCH ALBUM LIST (NO requests module)
# ---------------------------------------
def fetch_album_list(url: str):
    print("\n[STEP] Sending HTTP request...")

    req = Request(url, headers={"User-Agent": "Python-urllib"})
    with urlopen(req, timeout=10) as response:
        raw = response.read().decode("utf-8")

    print("[STEP] Parsing JSON response...")
    data = json.loads(raw)

    if not isinstance(data, list):
        raise ValueError("Expected JSON array at top level")

    print(f"[INFO] Received {len(data)} album entries")
    return data

# ---------------------------------------
# CREATE FOLDERS BASED ON ALBUM LIST
# ---------------------------------------
def create_album_folders(base_dir: Path, albums, dry_run: bool):
    print("\n[STEP] Creating album folders")

    for item in albums:
        album_name = item.get("albumName")
        if not album_name:
            continue

        safe_name = sanitize_folder_name(album_name)
        folder_path = base_dir / safe_name

        if folder_path.exists():
            if any(folder_path.iterdir()):
                print(f"{YELLOW}SKIP: Folder exists and is NOT empty{RESET} → {folder_path}")
            else:
                print(f"{YELLOW}EXISTS (empty){RESET}: {folder_path}")
            continue

        if dry_run:
            print(f"{GREEN}DRY RUN → Would create:{RESET} {folder_path}")
        else:
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"{GREEN}Created:{RESET} {folder_path}")

# ---------------------------------------
# MAIN
# ---------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Create album folders from HTTP JSON response.")
    parser.add_argument("--dir", required=True, help="Parent directory where album folders will be created.")
    parser.add_argument("--url", required=True, help="HTTP endpoint returning JSON album list.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without modifying filesystem.")
    args = parser.parse_args()

    base_dir = Path(args.dir)
    url = args.url

    print("\n=== START: Album Folder Sync Utility ===")
    if args.dry_run:
        print(f"{YELLOW}DRY RUN MODE ENABLED — No changes will be made{RESET}")

    base_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Clean empty directories
    clean_existing_dirs(base_dir, args.dry_run)

    # Step 2: Fetch album list
    albums = fetch_album_list(url)

    # Step 3: Create folders
    create_album_folders(base_dir, albums, args.dry_run)

    print("\n=== DONE ===")

if __name__ == "__main__":
    main()