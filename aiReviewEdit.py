from ebooklib import epub
from bs4 import BeautifulSoup
import ebooklib
import sys

from utils import prompt_paragraphByParagraph, prompt_chapterByChapter, verify_arguments

# Verify that the number of arguments matches
verify_arguments()
# Short_MachineTranslation.epub
EBOOK_NAME = sys.argv[2]
EDIT_TYPE = sys.argv[3]

try:
    # Read the original book
    original_book = epub.read_epub(f"{EBOOK_NAME}")
except FileNotFoundError:
    print("Please enter a valid file name.")
    sys.exit(1)


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
    # Temporarily disabled reviewing TOC or translating it
    if item.get_type() == ebooklib.ITEM_DOCUMENT and "toc" not in item.file_name.lower():
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
        # Or, they will be translated whole as a text
        if EDIT_TYPE == "line":
            # This changes cleaned_paragraphs over in the function
            prompt_paragraphByParagraph(cleaned_paragraphs)
            # Join the cleaned and reviewed paragraphs with newlines
            cleaned_content_string = "\n\n".join(cleaned_paragraphs)

        elif EDIT_TYPE == "chapter":
            cleaned_content_string = prompt_chapterByChapter(
                "\n\n".join(cleaned_paragraphs)
            )
        else:
            # If either of the edit types are not caught, then exit
            print("Please enter a valid process type, either 'line' or 'chapter'.")
            sys.exit(1)

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
