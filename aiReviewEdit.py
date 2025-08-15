from ebooklib import epub
from bs4 import BeautifulSoup
import ebooklib


# Function to remove tags
def remove_tags(html):
    soup = BeautifulSoup(html, "html.parser")
    for data in soup(["style", "script"]):
        data.decompose()
    return " ".join(soup.stripped_strings)


# Read the original book
original_book = epub.read_epub("./testNovels/MachineEnglish.epub")

# Create a new book for the stripped content
stripped_book = epub.EpubBook()

# Copy metadata from the original book
stripped_book.set_title(original_book.title)
stripped_book.add_author(original_book.get_metadata("DC", "creator")[0][0])
stripped_book.set_language("en")

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

        # Join the cleaned paragraphs with newlines
        cleaned_content_string = "\n\n".join(cleaned_paragraphs)

        # Create a new EpubHtml item with the cleaned content
        # Note: HTML needs paragraph tags to render correctly
        html_content = f'<html><body><p>{cleaned_content_string.replace("\n\n", "</p><p>")}</p></body></html>'

        new_chapter = epub.EpubHtml(
            title=item.title, file_name=item.file_name, lang="en"
        )
        new_chapter.content = html_content

        # Add the new chapter to the book
        stripped_book.add_item(new_chapter)
        new_chapters.append(new_chapter)

    else:
        # Copy non-document items directly (e.g., images, CSS)
        stripped_book.add_item(item)

# Set the spine and table of contents
stripped_book.toc = new_chapters
stripped_book.spine = ["nav"] + new_chapters

# Write the new EPUB file
epub.write_epub("stripped_novel.epub", stripped_book, {})

print("Stripped EPUB created successfully at 'stripped_novel.epub'")
