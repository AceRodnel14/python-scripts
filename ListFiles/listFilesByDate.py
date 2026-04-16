#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Lister TUI (Textual)
Python 3.10 / 3.11 compatible
Deterministic, audit-friendly, non-destructive
"""

import argparse
import os
import time
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header, Static
from textual.reactive import reactive
from textual import events


# --- Utility functions ---

def iter_files(base_dir: Path, max_depth: int):
    """
    Recursively yield files up to max_depth.
    """
    stack = [(base_dir, 0)]
    while stack:
        current, depth = stack.pop()
        if depth > max_depth:
            continue

        try:
            for entry in current.iterdir():
                if entry.is_file():
                    yield entry
                elif entry.is_dir():
                    stack.append((entry, depth + 1))
        except PermissionError:
            continue


def get_file_info(path: Path, sort_mode: str):
    """
    Return (name, timestamp_str, timestamp_raw)
    """
    stat = path.stat()

    if sort_mode == "modified":
        ts = stat.st_mtime
    else:
        ts = stat.st_ctime

    dt = datetime.fromtimestamp(ts)
    ts_str = dt.strftime("%Y-%m-%d %H:%M:%S")

    return path.name, ts_str, ts


# --- TUI Application ---

class FileListerApp(App):
    CSS_PATH = None

    sort_mode = reactive("creation")
    file_rows = reactive([])

    BINDINGS = [
        ("^", "jump_top", "Jump to top"),
        ("V", "jump_bottom", "Jump to bottom"),
    ]

    def __init__(self, rows, sort_mode):
        super().__init__()
        self.file_rows = rows
        self.sort_mode = sort_mode

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"Sorting by: {self.sort_mode}", id="sortinfo")
        yield DataTable(id="table")
        yield Footer()

    def on_mount(self):
        table = self.query_one("#table", DataTable)

        table.add_column("Name", key="name", width=None)
        table.add_column("Timestamp", key="timestamp", width=19)  # fixed width

        for row in self.file_rows:
            table.add_row(row[0], row[1])

        table.cursor_type = "row"
        table.focus()

    # --- Key bindings ---

    def action_jump_top(self):
        table = self.query_one("#table", DataTable)
        if table.row_count > 0:
            table.move_cursor(row=0)

    def action_jump_bottom(self):
        table = self.query_one("#table", DataTable)
        if table.row_count > 0:
            table.move_cursor(row=table.row_count - 1)

# --- CLI + Main ---

def main():
    parser = argparse.ArgumentParser(
        description="List files recursively and display in a Textual TUI table."
    )

    parser.add_argument(
        "--dir",
        required=True,
        help="Directory to scan."
    )

    parser.add_argument(
        "-n",
        type=int,
        default=1,
        help="Recursion depth (default: 1)."
    )

    parser.add_argument(
        "--creation",
        action="store_true",
        help="Sort by creation date (oldest → newest)."
    )

    parser.add_argument(
        "--modified",
        action="store_true",
        help="Sort by modified date (oldest → newest)."
    )

    args = parser.parse_args()

    base_dir = Path(args.dir).expanduser().resolve()
    if not base_dir.exists():
        print(f"Directory does not exist: {base_dir}")
        return

    # Determine sort mode
    if args.modified:
        sort_mode = "modified"
    else:
        sort_mode = "creation"

    print(f"Scanning: {base_dir}")
    print(f"Recursion depth: {args.n}")
    print(f"Sorting by: {sort_mode}")
    print("Processing...")

    rows = []
    count = 0

    for file_path in iter_files(base_dir, args.n - 1):
        count += 1
        if count % 50 == 0:
            print(f"Processing... {count} files", end="\r")

        name, ts_str, ts_raw = get_file_info(file_path, sort_mode)
        rows.append((name, ts_str, ts_raw))

    print(f"\nTotal files: {count}")

    # Sort oldest → newest
    rows.sort(key=lambda x: x[2])

    # Launch TUI
    app = FileListerApp(rows, sort_mode)
    app.run()


if __name__ == "__main__":
    main()
