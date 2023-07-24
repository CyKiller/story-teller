import logging
import argparse
from generate_cover import create_cover_image
from book_maker import create_epub
from write_novel_vector import write_novel_milvus, generate_unique_filename

logging.basicConfig(level=logging.INFO)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate a novel with AI.')
    parser.add_argument('--prompt', type=str, required=True,
                        help='The initial plot of the novel')
    parser.add_argument('--chapters', type=int, default=10,
                        help='The number of chapters in the novel')
    parser.add_argument('--style', type=str, default='adventurous',
                        help='The writing style of the novel')
    parser.add_argument('--genre', type=str, default='fantasy',
                        help='The genre of the novel')
    parser.add_argument('--collection', type=str, default='novels',
                        help='The Milvus collection to store the novel')
    parser.add_argument('--length', type=int, default=200,
                        help='The length of the generated content. '
                        'This value determines the number of words in the generated novel. '
                        'The default value is 200.')
    return parser.parse_args()


def main():
    args = parse_arguments()
    novel, title, chapters, chapter_titles = write_novel_milvus(
        args.prompt,
        args.chapters,
        args.collection,
        args.style,
        args.genre,
        args.length)
    if novel is None:
        logging.error("Failed to generate novel")
        return

    chapter_titles = [chapter_titles[i] + "\n" + chapters[i]
                      for i in range(len(chapters))]

    cover_image_path = create_cover_image(chapter_titles)

    filename = generate_unique_filename(title)
    create_epub(title, "Ramal Naron", chapter_titles,
                cover_image_path, filename)


if __name__ == "__main__":
    main()
