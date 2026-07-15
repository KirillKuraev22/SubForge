import subprocess
import typer
from faster_whisper import WhisperModel


app = typer.Typer()

@app.callback()
def main():
    pass


def format_timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)

    hours = milliseconds // 3_600_000
    milliseconds %= 3_600_000

    minutes = milliseconds // 60_000
    milliseconds %= 60_000

    secs = milliseconds // 1000
    millis = milliseconds % 1000

    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


@app.command()
def extract(source: str):
    command = [
        "ffmpeg",
        "-y",
        "-i",
        source,
        "-map",
        "0:a:0",
        "-vn",
        "-af",
        (
            "highpass=f=80,"
            "afftdn=nr=10:nf=-40,"
            "speechnorm=e=6.25:r=0.00001:l=1"
        ),
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        "audio.wav",
    ]

    subprocess.run(command, check=True)


@app.command()
def transcribe(audio: str = "audio.wav"):
    model = WhisperModel(
        "large-v3",
        device="cpu",
        compute_type="int8",
    )

    segments, info = model.transcribe(
        audio,
        beam_size=5,
        language="ru",
        task="transcribe",
        vad_filter=True,
        word_timestamps=True,
    )

    print(f"Detected language: {info.language}")
    print(f"Language probability: {info.language_probability:.2f}")

    with open('subtitles_ru.str', "w", encoding="utf-8") as file:
        for index, segment in enumerate(segments, start=1):
            start = format_timestamp(segment.start)
            end = format_timestamp(segment.end)
            text = segment.text.strip()

            word_probabilities = [
                word.probability
                for word in segment.words or []
            ]

            if word_probabilities:
                segment_probability = sum(word_probabilities) / len(word_probabilities)
                lowest_probability = min(word_probabilities)
            else:
                segment_probability = 0.0
                lowest_probability = 0.0


            file.write(f"{index}\n")
            file.write(f"{start} --> {end}\n")
            file.write(f"{text}\n\n")

            print(
                f"[{start} --> {end}] "
                f"[confidence={segment_probability:.1%}] "
                f"[lowest-word={lowest_probability:.1%}] "
                f"{text}"
            )

@app.command()
def generate(source: str):
    pass


@app.command()
def translate(subtitles: str = "subtitles_ru.str"):
    pass


if __name__ == "__main__":
    app()
