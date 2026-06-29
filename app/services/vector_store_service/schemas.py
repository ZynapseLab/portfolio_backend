from langsmith.utils import P
from weaviate.classes.config import DataType, Property

WEAVIATE_COLLECTION_SCHEMAS = {
    "devs": [
        Property(name="source_id", data_type=DataType.TEXT),
        Property(name="scope", data_type=DataType.TEXT),
        Property(name="source_heading", data_type=DataType.TEXT),
        Property(name="section_heading", data_type=DataType.TEXT),
        Property(name="chunk_index", data_type=DataType.NUMBER),
        Property(name="section_text", data_type=DataType.TEXT),
        Property(name="embed_text", data_type=DataType.TEXT),
    ],
}
