from pathlib import Path
from app.core.config import get_settings
from app.services.ingestion import load_file, chunk_documents
from app.rag.vectorstore import add_documents_to_vectorstore

settings = get_settings()

folder_path = Path(settings.sample_kb_dir)
files = [p for p in folder_path.iterdir() if p.is_file() ]

all_docs = []
for file in files:
    print(f"Processing file: {file}")
    all_docs.extend(load_file(file))
    chunks = chunk_documents(all_docs)
    ids = add_documents_to_vectorstore(docs=chunks)
    print(f"Added {len(ids)} chunks from {file} to vectorstore.")
