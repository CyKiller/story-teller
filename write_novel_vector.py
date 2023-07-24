import os
import requests
from fpdf import FPDF
from datetime import datetime
import subprocess
import time
import logging
import fpdf
from tqdm import tqdm
from pymilvus import connections, DataType, Collection, CollectionSchema, FieldSchema
import fablely.embed_vecs as embed_vecs
import fablely.fable_func as fable_func


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", 19530)

headers_openai = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}",
}

def check_argument(arg, expected_type):
    if not isinstance(arg, expected_type):
        raise TypeError(f"Expected argument of type {expected_type}, but got {type(arg)}")

def connect_to_milvus():
    try:
        client = connections.connect(host='127.0.0.1', port=27017)
        logging.info("Connected to Milvus server.")
        return client
    except Exception as e:
        logging.error(f"Failed to connect to Milvus server: {e}")
        return None


def generate_unique_filename(prefix):
    return f"{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S')}"


def write_novel_milvus(prompt, num_chapters, collection_name, writing_style, genre, auto_generate_next_chapter=True):
    check_argument(prompt, str)
    check_argument(num_chapters, int)
    check_argument(collection_name, str)
    check_argument(writing_style, str)
    check_argument(genre, str)
    check_argument(auto_generate_next_chapter, bool)

try:
        # Generate plots based on the prompt and genre
        logging.info('Generating plots...')
        import fablely.fable_func as fable_func

        plots = fable_func.generate_plots(prompt="Your prompt goes here", genre="Your genre goes here")

        # Select the most engaging plot
        logging.info('Selecting most engaging plot...')
        best_plot = fable_func.select_most_engaging(plots, genre)

        # Improve the selected plot
        logging.info('Improving plot...')
        improved_plot = fable_func.improve_plot(best_plot)

        # Get the title of the novel
        logging.info('Generating title...')
        title = get_title(improved_plot)

        # Generate the storyline of the novel
        logging.info('Generating storyline...')
        storyline = generate_storyline(improved_plot, num_chapters, genre)
        chapter_titles = storyline
        novel = f"Storyline:\n{storyline}\n\n"

        # Write the first chapter of the novel
        logging.info('Writing first chapter...')
        first_chapter = write_first_chapter(
            genre, storyline, chapter_titles[0], writing_style.strip())
        novel += f"Chapter 1:\n{first_chapter}\n"
        chapters = [first_chapter]

        logging.info('Connecting to Milvus...')
        # Try to connect to Milvus a few times before giving up
        for _ in tqdm(range(3), desc='Connecting to Milvus'):
            try:
                milvus_pod = subprocess.getoutput(
                    'kubectl get pod -l app=milvus -n milvus -o jsonpath="{.items[0].metadata.name}"')
                milvus_port = subprocess.getoutput(
                    f'kubectl get pod {milvus_pod} --template="{{(index (index .spec.containers 0).ports 0).containerPort}}{{"\n"}}"')
                break
            except Exception as e:
                logging.error(f'Error connecting to Milvus: {e}')
                time.sleep(1)
        else:
            logging.error('Failed to connect to Milvus after 3 attempts.')
            return

        logging.info('Generating novel...')
        novel = 'Once upon a time...'
        chapters = novel.split('Chapter ')

        chapter_names = ['Chapter ' + str(i) for i in range(1, len(chapters))]

        logging.info('Embedding text with OpenAI...')
        chapter_embeddings = [embed_vecs.embed_text_with_openai(
            chapter) for chapter in tqdm(chapters, desc='Embedding text')]

        fields = [
            FieldSchema(name="book_id", dtype=DataType.INT64,
                        is_primary=True, auto_id=True),
            FieldSchema(name="book_title",
                        dtype=DataType.VARCHAR, max_length=200),
            FieldSchema(name="author", dtype=DataType.VARCHAR, max_length=200),
            FieldSchema(name="genre", dtype=DataType.VARCHAR, max_length=200),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)
        ]

        schema = CollectionSchema(fields=fields, primary_field="book_id",
                                  description="Books collection", enable_dynamic_field=True)
        logging.info('Creating collection in Milvus...')
        embed_vecs.create_collection('novel_chapters', schema)

        logging.info('Storing vectors in Milvus...')
        embed_vecs.store_vectors_with_milvus(
            chapter_embeddings, chapter_names, 'novel_chapters')

        param = {'metric_type': 'L2'}
        logging.info('Searching vectors in Milvus...')
        results = embed_vecs.search_vectors_with_milvus(
            chapter_embeddings, 'novel_chapters', param)
        if results is None:
            logging.error("An error occurred while searching for vectors.")
        else:
            for result in results:
                logging.info(result)

        prompt = 'The story so far: ' + novel
        logging.info('Generating options for next chapter...')
        options = embed_vecs.generate_options_for_next_chapter(prompt, num_options=7)

        if auto_generate_next_chapter:
            chosen_option = options[0]
        else:
            chosen_option = input('Enter your input for the next chapter: ')

        chapter_name = 'Chapter ' + str(len(chapters) + 1)
        logging.info('Updating chapter in Milvus...')
        embed_vecs.update_chapter_in_milvus(chapter_name, chosen_option, collection_name)

        query = 'Once upon a time'
        logging.info('Searching text in Milvus...')
        search_results = embed_vecs.search_text_in_milvus(query)
        logging.info(search_results)

        state = 'The story so far: ' + novel + ' ' + chosen_option
        logging.info('Saving story state...')
        embed_vecs.save_story_state(state, 'story_state.txt')

        loaded_state = embed_vecs.load_story_state('story_state.txt')
        logging.info(loaded_state)

        try:
            logging.info('Saving story as PDF...')
            pdf = fpdf.FPDF(format='letter')
            pdf.add_page()
            pdf.set_font('Arial', size=12)
            pdf.multi_cell(0, 10, loaded_state)
            filename = generate_unique_filename("novel")
            pdf.output(f"{filename}.pdf")
            logging.info('Story saved as PDF.')
            
        except Exception as e:
                logging.error(f'An error occurred: {e}')
                return