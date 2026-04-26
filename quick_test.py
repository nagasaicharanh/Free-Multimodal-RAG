#!/usr/bin/env python
"""Quick test of RAG with one simple query."""
from src.pipeline import IngestionPipeline
from src.retriever import Retriever

pipeline = IngestionPipeline()
pdf_path = "data/samples/Insurance_Handbook_20103.pdf"

print("Ingesting PDF...")
report = pipeline.ingest_pdf(pdf_path)
print(f"Done! Embeddings: {report['total_embeddings']}")

if report['total_embeddings'] > 0:
    retriever = Retriever(pipeline.db_manager)
    result = retriever.query("What is insurance?")
    print(f"\nQuery: 'What is insurance?'")
    print(f"Sources: {result['num_sources']}")
    print(f"Answer: {result['answer'][:200]}")
    print("\nSUCCESS: RAG pipeline is working!")
else:
    print("FAILED: No embeddings generated")
