from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

class TestApp(App):
    CSS = """
    #messages {
        height: 1fr;
        overflow-y: scroll;
        scrollbar-gutter: stable;
    }
    """
    def compose(self) -> ComposeResult:
        yield Vertical(Static("Msg 1\n" * 20), id="messages")

if __name__ == "__main__":
    # Just checking if we can add CSS to the main file
    pass
