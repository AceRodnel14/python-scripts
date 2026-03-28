import os
import sys

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Vertical


def list_files(folder: str):
    try:
        return sorted(
            [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        )
    except Exception:
        return []


def merge_lists(left, right):
    return sorted(set(left) | set(right))


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

    def __init__(self, folder1, folder2, **kwargs):
        super().__init__(**kwargs)
        self.folder1 = folder1
        self.folder2 = folder2

        self.left_files = list_files(folder1)
        self.right_files = list_files(folder2)
        self.merged = merge_lists(self.left_files, self.right_files)

    def compose(self) -> ComposeResult:
        yield Header()

        yield Vertical(
            Static(f"Folder 1: {self.folder1}\nFolder 2: {self.folder2}", id="title"),
            DataTable(id="table"),
        )

        yield Footer()

    def on_mount(self):
        table = self.query_one("#table", DataTable)

        table.add_column("Folder 1", width=40)
        table.add_column("Folder 2", width=40)

        for name in self.merged:
            left = name if name in self.left_files else ""
            right = name if name in self.right_files else ""
            table.add_row(left, right)

        table.cursor_type = "row"
        table.show_cursor = False
        table.show_header = True
        table.zebra_stripes = True


def main():
    if len(sys.argv) != 3:
        print("Usage: python compare.py <folder1> <folder2>")
        sys.exit(1)

    folder1 = os.path.abspath(sys.argv[1])
    folder2 = os.path.abspath(sys.argv[2])

    if not os.path.isdir(folder1):
        print(f"Folder not found: {folder1}")
        sys.exit(1)

    if not os.path.isdir(folder2):
        print(f"Folder not found: {folder2}")
        sys.exit(1)

    app = DirCompare(folder1, folder2)
    app.run()


if __name__ == "__main__":
    main()