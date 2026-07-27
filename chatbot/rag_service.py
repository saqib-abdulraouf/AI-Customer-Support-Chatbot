"""
RAG Service: PDF Text Extraction (PyMuPDF), Chunking, Gemini Embeddings,
and ChromaDB Vector Store Integration.
"""

import os
import fitz  # PyMuPDF
from pathlib import Path
import chromadb

# Gemini SDK support for embeddings
genai = None
genai_client = None

try:
    import google.generativeai as genai
except ImportError:
    try:
        from google import genai as genai_new
        genai_client = genai_new
    except ImportError:
        pass


BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "smart_electronics_rag"
EMBEDDING_MODEL = "models/text-embedding-004"


def _get_chroma_client():
    """Returns a persistent ChromaDB client."""
    os.makedirs(CHROMA_DIR, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_chroma_collection():
    """Returns or creates the ChromaDB collection."""
    client = _get_chroma_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """
    Extracts plain text from a PDF file using PyMuPDF (fitz).
    """
    doc = fitz.open(str(pdf_path))
    extracted_pages = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        if text.strip():
            extracted_pages.append(text.strip())
    doc.close()
    return "\n\n".join(extracted_pages)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Splits document text into overlapping text chunks.
    """
    if not text:
        return []

    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i: i + chunk_size]
        chunk_str = " ".join(chunk_words)
        chunks.append(chunk_str)
        i += chunk_size - overlap

    return chunks


def get_embedding(text: str, task_type: str = "retrieval_document") -> list[float] | None:
    """
    Generates embedding vector for a given text using Gemini text-embedding-004 model.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        if genai and hasattr(genai, "configure"):
            genai.configure(api_key=api_key)
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=text,
                task_type=task_type,
            )
            return result["embedding"]
        elif genai_client:
            client = genai_client.Client(api_key=api_key)
            result = client.models.embed_content(
                model=EMBEDDING_MODEL.replace("models/", ""),
                contents=text,
            )
            if hasattr(result, "embedding"):
                return result.embedding.values
            elif isinstance(result, dict) and "embedding" in result:
                return result["embedding"]
    except Exception as exc:
        print(f"[RAG Embedding Error] {exc}")

    return None


def index_pdf_document(doc_id: int | str, title: str, pdf_path: str | Path) -> int:
    """
    Full Pipeline:
    Extract text (PyMuPDF) → Chunk text → Generate embeddings (Gemini) → Store in ChromaDB
    Returns count of chunks indexed.
    """
    full_text = extract_text_from_pdf(pdf_path)
    if not full_text:
        return 0

    chunks = chunk_text(full_text)
    if not chunks:
        return 0

    collection = get_chroma_collection()

    documents = []
    embeddings = []
    ids = []
    metadatas = []

    for idx, chunk in enumerate(chunks):
        embedding = get_embedding(chunk, task_type="retrieval_document")
        if embedding:
            chunk_id = f"doc_{doc_id}_chunk_{idx}"
            ids.append(chunk_id)
            documents.append(chunk)
            embeddings.append(embedding)
            metadatas.append({
                "doc_id": str(doc_id),
                "doc_title": title,
                "chunk_index": idx
            })

    if documents and embeddings:
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    return len(documents)


def delete_document_from_index(doc_id: int | str):
    """Deletes all chunks belonging to a document from ChromaDB."""
    try:
        collection = get_chroma_collection()
        collection.delete(where={"doc_id": str(doc_id)})
    except Exception as exc:
        print(f"[RAG Delete Error] {exc}")


def search_similar_chunks(query_text: str, top_k: int = 3) -> list[str]:
    """
    Customer asks question → Embed query → Vector search in ChromaDB → Return relevant text chunks
    """
    query_embedding = get_embedding(query_text, task_type="retrieval_query")
    if not query_embedding:
        return []

    try:
        collection = get_chroma_collection()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        if results and "documents" in results and results["documents"]:
            # flatten document lists
            matched_docs = [doc for sublist in results["documents"] for doc in sublist]
            return matched_docs
    except Exception as exc:
        print(f"[RAG Search Error] {exc}")

    return []
