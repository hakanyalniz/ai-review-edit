from ebooklib import epub
from bs4 import BeautifulSoup
import ebooklib
import sys

from utils import prompt_AI


if len(sys.argv) < 2:
    print("Please enter arguments like so: python .\\aiReviewEdit.py EBOOK-NAME")
    sys.exit(1)  # exit code 1 = error

# Short_MachineTranslation.epub
EBOOK_NAME = sys.argv[1]

# Read the original book
original_book = epub.read_epub(f"./testNovels/{EBOOK_NAME}")

# Create a new book for the stripped content
edited_new_book = epub.EpubBook()

# Copy metadata from the original book
edited_new_book.set_title(original_book.title)
edited_new_book.add_author(original_book.get_metadata("DC", "creator")[0][0])
edited_new_book.set_language("en")

# Lists to hold new items and chapters
new_chapters = []

# Process content items
for item in original_book.get_items():
    if item.get_type() == ebooklib.ITEM_DOCUMENT:
        # Parse the content of the current chapter
        soup = BeautifulSoup(item.get_content(), "html.parser")

        # Find all paragraph tags and extract their text
        paragraphs = soup.find_all("p")
        cleaned_paragraphs = []
        for p in paragraphs:
            # Use get_text() for individual paragraphs, then strip whitespace
            # and append with a newline
            cleaned_text = p.get_text(strip=True)

            if cleaned_text:  # Avoid empty paragraphs
                cleaned_paragraphs.append(cleaned_text)

        # Each parapgrah in the array will be cleaned up and reviewed by the model
        for index in range(len(cleaned_paragraphs)):
            cleaned_paragraphs[index] = prompt_AI(cleaned_paragraphs[index])
            print(f"Finished paragraph {index}")

        # Join the cleaned and reviewed paragraphs with newlines
        cleaned_content_string = "\n\n".join(cleaned_paragraphs)

        # Create a new EpubHtml item with the cleaned content
        # Note: HTML needs paragraph tags to render correctly
        html_content = f'<html><body><p>{cleaned_content_string.replace("\n\n", "</p><p>")}</p></body></html>'

        new_chapter = epub.EpubHtml(
            title=item.title, file_name=item.file_name, lang="en"
        )
        new_chapter.content = html_content

        # Add the new chapter to the book
        edited_new_book.add_item(new_chapter)
        new_chapters.append(new_chapter)

    else:
        # Copy non-document items directly (e.g., images, CSS)
        edited_new_book.add_item(item)

# Set the spine and table of contents
edited_new_book.toc = new_chapters
edited_new_book.spine = ["nav"] + new_chapters

# Write the new EPUB file
epub.write_epub(f"edited_{EBOOK_NAME}", edited_new_book, {})

print(f"Edited/Translated EPUB created successfully at 'edited_{EBOOK_NAME}'")
