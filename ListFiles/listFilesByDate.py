#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Lister TUI (Textual)
Python 3.10 / 3.11 compatible
Deterministic, audit-friendly, non-destructive
"""

import argparse
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header, Static
from textual.reactive import reactive


# --- Utility functions ---

def iter_files(base_dir: Path, max_depth: int):
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
    Return (full_path_str, timestamp_str, timestamp_raw)
    sort_mode: "creation" or "modified"
    """
    stat = path.stat()

    # --------------------------------------------------------
    # Birth time (true creation time)
    # --------------------------------------------------------
    try:
        birth_ts = stat.st_birthtime
    except AttributeError:
        # Filesystem does not support birth time → fallback to mtime
        birth_ts = stat.st_mtime

    # --------------------------------------------------------
    # Modified time
    # --------------------------------------------------------
    modify_ts = stat.st_mtime

    # --------------------------------------------------------
    # Choose timestamp based on sort mode
    # --------------------------------------------------------
    ts = birth_ts if sort_mode == "creation" else modify_ts

    dt = datetime.fromtimestamp(ts)
    ts_str = dt.strftime("%Y-%m-%d %H:%M:%S")

    return str(path), ts_str, ts


# ------------------------------------------------------------
# TUI Application
# ------------------------------------------------------------

class FileListerApp(App):
    CSS_PATH = None

    sort_mode = reactive("creation")
    file_rows = reactive([])
    path_width = reactive(40)   # default width

    BINDINGS = [
        ("^", "jump_top", "Jump to top"),
        ("V", "jump_bottom", "Jump to bottom"),
        ("[", "shrink_path", "Shrink path column"),
        ("]", "expand_path", "Expand path column"),
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
        self.build_table()

    # --------------------------------------------------------
    # Table builder (rebuilds when width changes)
    # --------------------------------------------------------

    def build_table(self):
        table = self.query_one("#table", DataTable)
        table.clear(columns=True)

        # Path column: manually sized
        table.add_column("Path", key="path", width=self.path_width)

        # Timestamp column: fixed width
        table.add_column("Timestamp", key="timestamp", width=19)

        for row in self.file_rows:
            table.add_row(row[0], row[1])

        table.cursor_type = "row"
        table.focus()

    # --------------------------------------------------------
    # Key bindings
    # --------------------------------------------------------

    def action_jump_top(self):
        table = self.query_one("#table", DataTable)
        if table.row_count > 0:
            table.move_cursor(row=0)

    def action_jump_bottom(self):
        table = self.query_one("#table", DataTable)
        if table.row_count > 0:
            table.move_cursor(row=table.row_count - 1)

    def action_shrink_path(self):
        self.path_width = max(10, self.path_width - 5)
        self.build_table()

    def action_expand_path(self):
        self.path_width = min(500, self.path_width + 5)
        self.build_table()


# ------------------------------------------------------------
# CLI + Main
# ------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="List files recursively and display in a Textual TUI table."
    )

    parser.add_argument("--dir", required=True, help="Directory to scan.")
    parser.add_argument("-n", type=int, default=1,
                        help="Recursion depth (1 = current folder only).")
    parser.add_argument("--creation", action="store_true",
                        help="Sort by creation date (default).")
    parser.add_argument("--modified", action="store_true",
                        help="Sort by modified date.")

    args = parser.parse_args()

    base_dir = Path(args.dir).expanduser().resolve()
    if not base_dir.exists():
        print(f"Directory does not exist: {base_dir}")
        return

    sort_mode = "modified" if args.modified else "creation"

    print(f"Scanning: {base_dir}")
    print(f"Recursion depth: {args.n}")
    print(f"Sorting by: {sort_mode}")
    print("Processing...")

    rows = []
    count = 0
    max_depth = max(args.n - 1, 0)

    for file_path in iter_files(base_dir, max_depth):
        count += 1
        if count % 50 == 0:
            print(f"Processing... {count} files", end="\r")

        full_path, ts_str, ts_raw = get_file_info(file_path, sort_mode)
        rows.append((full_path, ts_str, ts_raw))

    print(f"\nTotal files: {count}")

    rows.sort(key=lambda x: x[2])
    display_rows = [(r[0], r[1]) for r in rows]

    app = FileListerApp(display_rows, sort_mode)
    app.run()


if __name__ == "__main__":
    main()