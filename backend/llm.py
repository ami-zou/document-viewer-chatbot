from haystack.indexing.cleaning import clean_wiki_text
from haystack.indexing.io import write_documents_to_db

# Index documents
documents = [
    {"text": clean_wiki_text("Document A content"), "meta": {"name": "Document A"}},
    {"text": clean_wiki_text("Document B content"), "meta": {"name": "Document B"}},
    # Add more documents
]

write_documents_to_db(documents, db, index="documents")
