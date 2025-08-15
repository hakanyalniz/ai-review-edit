from ebooklib import epub
from bs4 import BeautifulSoup
import ebooklib

BOOK = epub.read_epub("./testNovels/MachineEnglish.epub")
STRIPPED_BOOK = BOOK


# Function to remove tags
def remove_tags(html):
    # parse html content
    soup = BeautifulSoup(html, "html.parser")

    for data in soup(["style", "script"]):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return " ".join(soup.stripped_strings)


for item in BOOK.get_items():
    if item.get_type() == ebooklib.ITEM_DOCUMENT:
        STRIPPED_BOOK = remove_tags(item.get_content())

print(STRIPPED_BOOK)
