import requests
from bs4 import BeautifulSoup
import sys

from prompts import EDIT_PROMPT, TRANSLATION_PROMPT


# Verifies if the user entered the correct arguments and if not, how to enter them
def verify_arguments():
    if len(sys.argv) > 1 and sys.argv[1] == "help":
        print(
            """
                HOW TO RUN:
                Please enter arguments like so: python .\\aiReviewEdit.py translate/edit EBOOK-NAME line/chapter

                python: This is required to run the program
                .\\aiReviewEdit.py: The program name that you run with the python command
                translate/edit: Choose to either edit the novel or translate it from another language to English
                EBOOK-NAME: The name of the Ebook you wish to edit or translate
                line/chapter: If you wish to edit/translate either line by line or translate the entire chapter at once


                USAGE:
                Open up LMStudio and load the model you want to use. I suggest using at least 4B models and up for consistent results.
                1B models can still work for editing and fixing the grammar, but the output will be unstable.
                4B and up is the best for editing and translation.

                Gemma 3 and Qwen3 models are reccommended due to their low cost and highly effective outputs.
              """
        )
        sys.exit(1)

    elif len(sys.argv) < 4:
        print(
            """
                Please enter arguments like so: python .\\aiReviewEdit.py translate/edit EBOOK-NAME line/chapter

                python: This is required to run the program
                .\\aiReviewEdit.py: The program name that you run with the python command
                translate/edit: Choose to either "edit" the novel or "translate" it from another language to English
                EBOOK-NAME: The name of the Ebook you wish to edit or translate
                line/chapter: If you wish to edit/translate either line by line or translate the entire chapter at once

                COMMANDS:
                help: Will show the above text along side with USAGE text.
              """
        )
        sys.exit(1)  # exit code 1 = error


# Decides the prompt based on the user given argument
def _define_prompt():
    verify_arguments()
    if sys.argv[2] == "translate":
        PROMPT = EDIT_PROMPT
    elif sys.argv[2] == "edit":
        PROMPT = TRANSLATION_PROMPT
    else:
        print("Please enter a valid process. Either 'translate' or 'edit'.")
        sys.exit(1)

    return PROMPT


URL = "http://127.0.0.1:1234/v1/chat/completions"
HEADERS = {"Content-Type": "application/json"}
CHAT_REQUEST = {
    "messages": [
        {"role": "system", "content": f"{_define_prompt()}"},
        {"role": "user", "content": ""},
    ],
    "temperature": 0.5,
    "max_tokens": -1,
}


# Function to remove tags
def _remove_tags(html):
    soup = BeautifulSoup(html, "html.parser")
    for data in soup(["style", "script"]):
        data.decompose()
    return " ".join(soup.stripped_strings)


# Send a request to the backend AI Model with the text input to edit/translate
def _prompt_AI(novel_input):
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
        cleaned_paragraphs[index] = _prompt_AI(cleaned_paragraphs[index])
        print(f"Finished paragraph {index}")


# The prompt will process the chapter whole instead of by paragraph
def prompt_chapterByChapter(cleaned_content_string):
    return _prompt_AI(cleaned_content_string)
