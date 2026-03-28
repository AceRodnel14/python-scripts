import os
import sys

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, RichLog, Static
from textual.containers import Horizontal, Vertical, VerticalScroll


def list_files(folder: str):
    try:
        return sorted(
            [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        )
    except Exception:
        return []


def merge_lists(left, right):
    """Return sorted union of filenames."""
    return sorted(set(left) | set(right))


class DirCompare(App):

    CSS = """
    #left_area, #right_area {
        height: 1fr;
        border: solid green;
    }

    #left_log, #right_log {
        padding: 1;
    }

    #title_left, #title_right {
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

        yield Horizontal(

            Vertical(
                Static(f"Folder 1:\n{self.folder1}", id="title_left"),
                VerticalScroll(
                    RichLog(id="left_log", markup=True, wrap=False),
                    id="left_area",
                ),
            ),

            Vertical(
                Static(f"Folder 2:\n{self.folder2}", id="title_right"),
                VerticalScroll(
                    RichLog(id="right_log", markup=True, wrap=False),
                    id="right_area",
                ),
            ),
        )

        yield Footer()

    def on_mount(self):
        left_log = self.query_one("#left_log", RichLog)
        right_log = self.query_one("#right_log", RichLog)

        for name in self.merged:
            left_exists = name in self.left_files
            right_exists = name in self.right_files

            if left_exists:
                left_log.write(f"[green]{name}[/green]")
            else:
                left_log.write("")

            if right_exists:
                right_log.write(f"[green]{name}[/green]")
            else:
                right_log.write("")


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