#!/usr/bin/env python3
"""
Script de ingesta: carga los PDFs de pólizas en ChromaDB con embeddings de OpenAI.
Ejecutar una vez antes de usar la aplicación, o cuando se agreguen nuevos documentos.

Uso:
    python ingest.py
"""

import os
import shutil
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_PATH = os.getenv("DB_PATH", "./vector_db/chroma_db")
DOCS_PATH = os.path.join(os.path.dirname(__file__), "vector_db", "documentos")

if not OPENAI_API_KEY:
    raise ValueError("Falta OPENAI_API_KEY en el archivo .env")


def ingest():
    pdf_files = sorted(f for f in os.listdir(DOCS_PATH) if f.endswith(".pdf"))

    if not pdf_files:
        print("No se encontraron PDFs en", DOCS_PATH)
        return

    print(f"Encontrados {len(pdf_files)} PDFs para indexar:")
    for f in pdf_files:
        print(f"  - {f}")

    # Limpiar base de datos existente para re-indexar desde cero
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
        print(f"\nBase de datos anterior eliminada: {DB_PATH}")

    # Cargar todos los PDFs
    all_docs = []
    for pdf_file in pdf_files:
        pdf_path = os.path.join(DOCS_PATH, pdf_file)
        try:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source_file"] = pdf_file
            all_docs.extend(docs)
            print(f"  Cargado: {pdf_file} ({len(docs)} páginas)")
        except Exception as e:
            print(f"  Error cargando {pdf_file}: {e}")

    if not all_docs:
        print("No se pudieron cargar documentos.")
        return

    print(f"\nTotal de páginas cargadas: {len(all_docs)}")

    # Dividir en chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(all_docs)
    print(f"Chunks generados: {len(chunks)}")

    # Crear embeddings e indexar en ChromaDB
    print("\nGenerando embeddings con OpenAI y guardando en ChromaDB...")
    embedding_model = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=OPENAI_API_KEY,
    )

    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=DB_PATH,
    )

    print(f"\nIngesta completada. {len(chunks)} chunks indexados en {DB_PATH}")

    # Verificación rápida
    results = vector_db.similarity_search("seguro de auto", k=3)
    print(f"\nVerificación: búsqueda 'seguro de auto' retornó {len(results)} resultados")
    if results:
        print(f"  Primer resultado ({results[0].metadata.get('source_file', '?')}):")
        print(f"  {results[0].page_content[:150]}...")


if __name__ == "__main__":
    ingest()
