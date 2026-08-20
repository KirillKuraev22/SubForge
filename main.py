from pathlib import Path

import subprocess
import typer
from faster_whisper import WhisperModel

from transcription import transcribe_complete


app = typer.Typer()

@app.callback()
def main():
    pass


@app.command()
def create_ru(source: Path):
    transcribe_complete(source)


@app.command()
def create_eng(subtitles: str = "subtitles_ru.srt"):
    pass


if __name__ == "__main__":
    app()
