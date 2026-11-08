import srt
import requests
import json
import sys


def validate_id(original, translated):
    original_ids = sorted([sub["id"] for sub in original])
    translated_ids = sorted([item["id"] for item in translated])

    if original_ids != translated_ids:
        raise ValueError("Mismatch between original and translated subtitle IDs.")


with open("subtitles.srt", encoding="utf-8-sig") as f:
    subtitles = list(srt.parse(f.read()))

data = [{"id": sub.index, "text": sub.content} for sub in subtitles]
user_prompt = json.dumps(data, ensure_ascii=False)


url = "http://localhost:11434/api/chat"
system_prompt = """
You are a professional Russian-to-English subtitle translator.

Your task is to translate ALL Russian subtitle text into natural English.

STRICT RULES:
1. The input language is Russian.
2. The output language MUST be English.
3. NEVER copy Russian text into the output.
4. Translate the "text" field of every object.
5. Preserve every subtitle ID exactly.
6. Do not add, remove, merge, or split subtitles.
7. Preserve meaning, tone, and dialogue context.
8. Return valid JSON matching this structure:

{
  "translations": [
    {"id": 1, "text": "English translation"}
  ]
}
"""

schema = {
    "type": "object",
    "properties": {
        "translations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "text": {"type": "string"}
                },
                "required": ["id", "text"],
                "additionalProperties": False
            }
        }
    },
    "required": ["translations"],
    "additionalProperties": False
}

translated = {}
for i in range(0, len(data), 10):
    batch = data[i:i + 10]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(batch, ensure_ascii=False)}
    ]
    response = requests.post(
    url=url,
    json={
        "model": "qwen2.5:3b",
        "messages": messages,
        "stream": False,
        "format": schema,
        "options": {
            "temperature": 0
            }
        }
    )   
    print(response.status_code, response.text)
    response.raise_for_status()

    result = json.loads(response.json()["message"]["content"])["translations"]
    validate_id(batch, result)

    translated.update({result[x]["id"]: result[x]["text"] for x in range(len(result))})


for sub in subtitles:
    sub.content = translated[int(sub.index)]

with open("subtitles_en.srt", "w", encoding="utf-8") as f:
    f.write(srt.compose(subtitles))
