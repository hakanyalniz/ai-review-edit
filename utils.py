import requests
from bs4 import BeautifulSoup
import sys


URL = "http://127.0.0.1:1234/v1/chat/completions"
PROMPT = (
    "Revise the provided text to correct grammar, improve flow, and naturalize unnatural phrasing. "
    "Only reply in the edited text and nothing else."
)
HEADERS = {"Content-Type": "application/json"}
CHAT_REQUEST = {
    "model": "google/gemma-3-1b",
    "messages": [
        {"role": "system", "content": f"{PROMPT}"},
        {"role": "user", "content": ""},
    ],
    "temperature": 0.5,
    "max_tokens": -1,
}


# Function to remove tags
def remove_tags(html):
    soup = BeautifulSoup(html, "html.parser")
    for data in soup(["style", "script"]):
        data.decompose()
    return " ".join(soup.stripped_strings)


# Send a request to the backend AI Model with the text input to edit/translate
def prompt_AI(novel_input):
    CHAT_REQUEST["messages"][1][
        "content"
    ] = f"The text is given below:\n\n{novel_input}"
    response = requests.post(URL, json=CHAT_REQUEST, headers=HEADERS)

    # Return only the edited message content
    # print(response.json()["choices"][0]["message"]["content"])
    return response.json()["choices"][0]["message"]["content"]


def verify_arguments():
    if len(sys.argv) < 2:
        print("Please enter arguments like so: python .\\aiReviewEdit.py EBOOK-NAME")
        sys.exit(1)  # exit code 1 = error

    # Short_MachineTranslation.epub
    EBOOK_NAME = sys.argv[1]
    return EBOOK_NAME
