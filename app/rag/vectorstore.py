import time
from pinecone import Pinecone, ServerlessSpec
#from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from app.core.config import get_settings


settings = get_settings()

_embeddings = None
_vectorstore = None

EMBEDDINGS_DIMENSION = {
    
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
    "all-MiniLM-L6-v2": 384,
}

def get_embeddings_dimension(model_name: str | None = None) -> int:
    name = (model_name or settings.embedding_model or "").strip()
    if not name:
        raise RuntimeError("Embedding model name is not specified.")

    normalized_name = name.lower()
    if normalized_name in EMBEDDINGS_DIMENSION:
        return EMBEDDINGS_DIMENSION[normalized_name]
    if "text-embedding-3-small" in normalized_name:
        return 1536
    if "text-embedding-3-large" in normalized_name:
        return 3072
    if "text-embedding-ada-002" in normalized_name:
        return 1536
    if "all-minilm-l6-v2" in normalized_name:
        return 384

    raise RuntimeError(f"Unknown embedding model: {model_name}")

# def get_embeddings() -> OpenAIEmbeddings:
#     global _embeddings
#     if _embeddings is None:
#         if not settings.openai_api_key:
#             raise RuntimeError("Embedding model or OpenAI API key is not specified.")
#         _embeddings = OpenAIEmbeddings(
#             model=settings.embedding_model,
#             openai_api_key=settings.openai_api_key,
#         )
#     return _embeddings

def get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        if not settings.embedding_model:
            raise RuntimeError("Embedding model name is not specified.")
        _embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
        )
    return _embeddings

def ensure_index():
    if not settings.pinecone_api_key:
        raise RuntimeError("PINECONE_API_KEY is missing")

    desired_dimension = get_embeddings_dimension()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    names = [x["name"] for x in pc.list_indexes()]

    if settings.pinecone_index_name in names:
        index_info = pc.describe_index(settings.pinecone_index_name)
        current_dimension = getattr(index_info, "dimension", None)
        if current_dimension is None and isinstance(index_info, dict):
            current_dimension = index_info.get("dimension")

        if current_dimension is not None and current_dimension != desired_dimension:
            pc.delete_index(name=settings.pinecone_index_name)
            while settings.pinecone_index_name in [x["name"] for x in pc.list_indexes()]:
                time.sleep(1)

    if settings.pinecone_index_name not in [x["name"] for x in pc.list_indexes()]:
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=desired_dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(settings.pinecone_index_name).status["ready"]:
            time.sleep(1)

    return pc.Index(settings.pinecone_index_name)

def get_vectorstore() :
    global _vectorstore
    if _vectorstore is None:
        index = ensure_index()
        embeddings = get_embeddings()
        namespace = settings.pinecone_namespace
        _vectorstore = PineconeVectorStore(index=index, embedding=embeddings, namespace=namespace)
    return _vectorstore

def get_retriever():
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(search_kwargs={"k": settings.top_k})

def add_documents_to_vectorstore(docs):
    vectorstore = get_vectorstore()
    vectorstore.add_documents(docs)