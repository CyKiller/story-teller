import requests
import base64
from datetime import datetime
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
OPENAI_ENGINE_ID = "text-davinci-003"
STABILITY_MODEL = "DALL-E"
COVERS_DIRECTORY = "covers"

headers_openai = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}",
}

headers_stability = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {STABILITY_API_KEY}",
}


def generate_cover_prompt(plot):
    data = {
        "engine": OPENAI_ENGINE_ID,
        "prompt": f"Create a cover description for a book with the following plot: {plot}",
        "max_tokens": 100,
    }
    response = requests.post(
        "https://api.openai.com/v1/engines/davinci-codex/completions", headers=headers_openai, json=data)
    return response.json()['choices'][0]['text']


def create_cover_image(plot):
    cover_description = generate_cover_prompt(plot)
    data = {
        "engine": STABILITY_MODEL,
        "prompt": cover_description,
        "max_tokens": 100,
    }
    response = requests.post(
        "https://api.openai.com/v1/engines/davinci-codex/completions", headers=headers_stability, json=data)
    if response.status_code != 200:
        raise Exception(
            f"Request to Stability API failed with status code {response.status_code}")
    image_data = base64.b64decode(response.json()['image'])
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".png"
    filepath = os.path.join(COVERS_DIRECTORY, filename)
    with open(filepath, 'wb') as f:
        f.write(image_data)
    return filepath
