import os
import sys

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Vertical


def list_folders(folder: str):
    try:
        return sorted(
            [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]
        )
    except Exception:
        return []


def list_files(folder: str):
    try:
        return sorted(
            [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        )
    except Exception:
        return []


class DirCompare(App):

    CSS = """
    #table {
        height: 1fr;
        border: solid green;
    }

    #title {
        padding: 1;
        text-style: bold;
    }
    """

    TITLE = "Directory Compare"
    SUB_TITLE = "Side-by-side file comparison"

    def __init__(self, folders, **kwargs):
        super().__init__(**kwargs)

        # List of folder paths
        self.folders = folders
        self.num_dirs = len(folders)

        # Per-directory folder + file lists
        self.folder_lists = [list_folders(f) for f in folders]
        self.file_lists = [list_files(f) for f in folders]

        # Merged lists (folders first, then files)
        all_folders = set().union(*self.folder_lists)
        all_files = set().union(*self.file_lists)

        self.merged_folders = sorted(all_folders)
        self.merged_files = sorted(all_files)

    def compose(self) -> ComposeResult:
        yield Header()

        title_text = "\n".join([f"Folder {i+1}: {path}" for i, path in enumerate(self.folders)])

        yield Vertical(
            Static(title_text, id="title"),
            DataTable(id="table"),
        )

        yield Footer()

    def on_mount(self):
        table = self.query_one("#table", DataTable)

        # Dynamic columns
        for i in range(self.num_dirs):
            table.add_column(f"Folder {i+1}", width=40)

        # --- FOLDERS FIRST ---
        for name in self.merged_folders:
            row = []
            for i in range(self.num_dirs):
                if name in self.folder_lists[i]:
                    row.append(f"[bold blue]{name}/[/bold blue]")
                else:
                    row.append("")
            table.add_row(*row)

        # --- SEPARATOR ROW ---
        sep = "[dim]────────────────────[/dim]"
        table.add_row(*([sep] * self.num_dirs))

        # --- FILES AFTER ---
        for name in self.merged_files:
            row = []
            for i in range(self.num_dirs):
                if name in self.file_lists[i]:
                    row.append(f"[white]{name}[/white]")
                else:
                    row.append("")
            table.add_row(*row)

        table.cursor_type = "row"
        table.show_cursor = False
        table.show_header = True
        table.zebra_stripes = True


def main():
    # Require 2–4 directories
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print("Usage: python compare.py <folder1> <folder2> [folder3] [folder4]")
        print("You must provide at least 2 and at most 4 directories.")
        sys.exit(1)

    folders = [os.path.abspath(arg) for arg in sys.argv[1:]]

    # Validate directories
    for f in folders:
        if not os.path.isdir(f):
            print(f"Folder not found: {f}")
            sys.exit(1)

    app = DirCompare(folders)
    app.run()


if __name__ == "__main__":
    main()