from weaviate.classes.config import DataType, Property

KNOWLEDGE_COLLECTIONS = {
    "devs": "DevsKnowledge",
    "projects": "ProjectsKnowledge",
}

WEAVIATE_COLLECTION_SCHEMAS = {
    collection: [
        Property(name="source_id", data_type=DataType.TEXT),
        Property(name="scope", data_type=DataType.TEXT),
        Property(name="source_heading", data_type=DataType.TEXT),
        Property(name="section_heading", data_type=DataType.TEXT),
        Property(name="chunk_index", data_type=DataType.NUMBER),
        Property(name="section_text", data_type=DataType.TEXT),
        Property(name="embed_text", data_type=DataType.TEXT),
        Property(name="content_hash", data_type=DataType.TEXT),
        Property(name="embedding_model", data_type=DataType.TEXT),
    ]
    for collection in KNOWLEDGE_COLLECTIONS.values()
}
