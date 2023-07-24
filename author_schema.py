from pymilvus import DataType, CollectionSchema, FieldSchema, Collection
from pymilvus import connections
import logging


def connect_to_milvus():
    try:
        client = connections.connect(host='127.0.0.1', port=27017)
        logging.info("Connected to Milvus server.")
        return client
    except Exception as e:
        logging.error(f"Failed to connect to Milvus server: {e}")
        return None


def create_books_collection(collection_name):
    book_schema = CollectionSchema(
        fields=[
            FieldSchema(name="book_id", dtype=DataType.INT64,
                        is_primary=True, auto_id=True),
            FieldSchema(name="book_title", dtype=DataType.STRING),
            FieldSchema(name="author", dtype=DataType.STRING),
            FieldSchema(name="genre", dtype=DataType.STRING),
            FieldSchema(name="book_vector",
                        dtype=DataType.FLOAT_VECTOR, dim=768),
        ],
        description="Book collection",
        auto_id=False
    )
    books_collection = Collection(collection_name, schema=book_schema)
    return books_collection


def create_users_collection(collection_name):
    user_schema = CollectionSchema(
        fields=[
            FieldSchema(name="user_id", dtype=DataType.INT64,
                        is_primary=True, auto_id=True),
            FieldSchema(name="user_name", dtype=DataType.STRING),
        ],
        description="User collection",
        auto_id=False
    )
    users_collection = Collection(collection_name, schema=user_schema)
    return users_collection


def create_chapters_collection(collection_name):
    chapter_schema = CollectionSchema(
        fields=[
            FieldSchema(name="chapter_id", dtype=DataType.INT64,
                        is_primary=True, auto_id=True),
            FieldSchema(name="chapter_title", dtype=DataType.STRING),
            FieldSchema(name="book_id", dtype=DataType.INT64),
        ],
        description="Chapter collection",
        auto_id=False
    )
    chapters_collection = Collection(collection_name, schema=chapter_schema)
    return chapters_collection
