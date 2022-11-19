"""Main file."""

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

from rich.console import Console, Prompt
from utils import connect_api

console = Console()
prompt = Prompt()
api = connect_api()


def main():
    """Main."""

    channel_id = prompt.ask(":video_camera: Please enter a channel ID: ")
    request = (
        api.channels()
        .list(
            part="snippet",
            id=channel_id,
        )
        .execute()
    )
    console.print("Channel found...")
    snippet = request["snippet"]
    console.print(snippet)


if __name__ == "__main__":
    main()
