from app.core.config import get_settings
from app.services.ingestion import load_file, chunk_documents
from pathlib import Path
from app.rag.vectorstore import ensure_index, get_embeddings, add_documents_to_vectorstore

settings = get_settings()

print(f"App Name: {settings.app_name}")

docs = load_file(Path("data/sample_kb/Nexora_Technologies_Incident_Priority_SLA_Policy.pdf"))
chunks = chunk_documents(docs)

add_documents_to_vectorstore(docs=chunks)
