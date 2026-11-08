from pathlib import Path

import subprocess
import typer
from faster_whisper import WhisperModel

from transcription import transcribe_complete
from translation import translate_subtitles


app = typer.Typer()

@app.callback()
def main():
    pass


@app.command()
def create_ru(source: Path):
    transcribe_complete(source)


@app.command()
def create_eng(subtitles: str = "subtitles_ru.srt"):
    translate_subtitles(subtitles, "subtitles_en.srt", model="qwen2.5:3b", batch_size=10)


if __name__ == "__main__":
    app()
