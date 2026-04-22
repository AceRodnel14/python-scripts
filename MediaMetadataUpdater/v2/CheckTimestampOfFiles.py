import os
import argparse
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(description="List key timestamp metadata for files (no recursion)")

    parser.add_argument(
        "--dir",
        required=True,
        help="Comma-separated list of directories to scan (non-recursive)"
    )

    return parser.parse_args()


def get_relevant_timestamps(file_path):
    """
    Return only the timestamp fields that matter for your workflow:
    - DateTimeOriginal
    - CreateDate
    - CreationTime
    - ModifyDate

    Output is parsed into a dict for clean labeled printing.
    NOTE: We DO NOT use -AllDates here because it expands to multiple
    values without clear keys when combined with -s -s -s.
    """
    fields = {
        "DateTimeOriginal": None,
        "CreateDate": None,
        "CreationTime": None,
        "ModifyDate": None,
    }

    try:
        result = subprocess.run(
            [
                "exiftool",
                "-s",  # keep tag names
                "-DateTimeOriginal",
                "-CreateDate",
                "-CreationTime",
                "-ModifyDate",
                file_path
            ],
            capture_output=True,
            text=True
        )

        raw = result.stdout.strip()

        if not raw:
            return fields

        for line in raw.splitlines():
            if ":" not in line:
                continue

            # Example line: "DateTimeOriginal : 2025:12:16 00:00:00"
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            if key in fields:
                fields[key] = value

        return fields

    except Exception:
        return fields


def main():
    args = parse_args()

    parent_dirs = [os.path.abspath(p.strip()) for p in args.dir.split(",") if p.strip()]

    print("Listing key timestamp metadata (single-threaded, safe mode)\n")

    for parent in parent_dirs:
        if not os.path.isdir(parent):
            print(f"Skipping invalid directory: {parent}")
            continue

        print(f"Scanning: {parent}\n")

        for file in os.listdir(parent):
            fpath = os.path.join(parent, file)

            if not os.path.isfile(fpath):
                continue

            print(file)

            timestamps = get_relevant_timestamps(fpath)

            for key, value in timestamps.items():
                if value:
                    print(f"-- {key}: {value}")
                else:
                    print(f"-- {key}: <Unavailable>")

            print()  # blank line between files

    print("Done.")


if __name__ == "__main__":
    main()
