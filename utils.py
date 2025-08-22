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


# Each parapgrah in the array will be cleaned up and reviewed by the model
def prompt_paragraphByParagraph(cleaned_paragraphs):
    for index in range(len(cleaned_paragraphs)):
        cleaned_paragraphs[index] = prompt_AI(cleaned_paragraphs[index])
        print(f"Finished paragraph {index}")


def prompt_chapterByChapter(cleaned_content_string):
    return prompt_AI(cleaned_content_string)


def verify_arguments():
    if sys.argv[1] == "help":
        print(
            """
                HOW TO RUN:
                Please enter arguments like so: python .\\aiReviewEdit.py EBOOK-NAME line/chapter

                python: This is required to run the program
                .\\aiReviewEdit.py: The program name that you run with the python command
                EBOOK-NAME: The name of the Ebook you wish to edit or translate
                line/chapter: If you wish to edit/translate either line by line or translate the entire chapter at once


                USAGE:
                Open up LMStudio and load the model you want to use. I suggest using at least 4B models and up for consistent results.
              """
        )
        sys.exit(1)

    elif len(sys.argv) < 3:
        print(
            """Please enter arguments like so: python .\\aiReviewEdit.py EBOOK-NAME line/chapter

                python: This is required to run the program
                .\\aiReviewEdit.py: The program name that you run with the python command
                EBOOK-NAME: The name of the Ebook you wish to edit or translate
                line/chapter: If you wish to edit/translate either line by line or translate the entire chapter at once
              """
        )
        sys.exit(1)  # exit code 1 = error
