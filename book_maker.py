import os
import time
from datetime import datetime
from ebooklib import epub

CSS_PATH = 'styles.css'


def generate_unique_id():
    return f"id{int(time.time())}"


def create_epub(title, author, chapters, cover_image_path=None):
    book = epub.EpubBook()

    # set metadata
    book.set_identifier(generate_unique_id())
    book.set_title(title)
    book.set_language('en')
    book.add_author(author)

    if cover_image_path:
        # add cover image
        book.set_cover("image.jpg", open(cover_image_path, 'rb').read())

    # create chapters
    epub_chapters = []
    for idx, chapter in enumerate(chapters, start=1):
        c = epub.EpubHtml(
            title=f'Chapter {idx}', file_name=f'chap_{idx}.xhtml', lang='en')
        c.content = chapter
        epub_chapters.append(c)
        book.add_item(c)

    # define Table Of Contents
    book.toc = tuple(epub_chapters)

    # add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define CSS style
    with open(CSS_PATH, 'r') as f:
        css_content = f.read()

    style = epub.EpubItem(uid="style_nav", file_name="style/nav.css",
                          media_type="text/css", content=css_content)
    book.add_item(style)

    # create book spine
    book.spine = ['nav'] + epub_chapters

    # save the book to file
    filename = f"{title}_{datetime.now().strftime('%Y%m%d%H%M%S')}.epub"
    epub.write_epub(filename, book, {})

    print(f"EPUB file saved as {filename}")
