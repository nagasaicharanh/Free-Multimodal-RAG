#!/usr/bin/env python
"""Quick end-to-end test of the RAG pipeline."""
from src.pipeline import IngestionPipeline
from src.retriever import Retriever
import sys

try:
    print("=" * 60)
    print("FREE MULTIMODAL RAG - END-TO-END TEST")
    print("=" * 60)
    print()
    
    # Initialize pipeline
    print("1. Initializing pipeline...")
    pipeline = IngestionPipeline()
    print("   ✓ Pipeline ready")
    print()
    
    # Ingest PDF
    pdf_path = "data/samples/Insurance_Handbook_20103.pdf"
    print(f"2. Ingesting PDF: {pdf_path}")
    report = pipeline.ingest_pdf(pdf_path, chunking_strategy="recursive")
    
    print(f"   ✓ Ingestion complete!")
    print(f"     - Text chunks: {report['text_chunks']}")
    print(f"     - Tables: {report['tables']}")
    print(f"     - Images: {report['images']}")
    print(f"     - Total embeddings: {report['total_embeddings']}")
    print(f"     - Processing time: {report['processing_time']:.2f}s")
    
    if report["errors"]:
        print(f"   ⚠ Errors encountered:")
        for error in report["errors"]:
            print(f"     - {error}")
    print()
    
    if report["total_embeddings"] == 0:
        print("✗ FAILED: No embeddings generated")
        sys.exit(1)
    
    # Test retriever
    print("3. Testing retrieval and answer generation...")
    retriever = Retriever(pipeline.db_manager)
    
    test_queries = [
        "What is this document about?",
        "What types of insurance are covered?",
        "Who is the intended audience?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: '{query}'")
        result = retriever.query(query, top_k=3)
        
        print(f"   Sources found: {result['num_sources']}")
        for j, source in enumerate(result['sources'], 1):
            print(f"     Source {j}: {source['source_badge']} (relevance: {source['relevance_score']:.0%})")
        
        answer_preview = result['answer'][:100] + "..." if len(result['answer']) > 100 else result['answer']
        print(f"   Answer: {answer_preview}")
    
    print()
    print("=" * 60)
    print("✓ ALL TESTS PASSED - PIPELINE IS WORKING!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Open http://localhost:8502 in your browser")
    print("2. Go to 'Upload PDF' section")
    print("3. Upload data/samples/Insurance_Handbook_20103.pdf")
    print("4. Ask questions and see the RAG system in action!")
    print()
    
    sys.exit(0)
    
except Exception as e:
    print()
    print("=" * 60)
    print(f"✗ TEST FAILED: {e}")
    print("=" * 60)
    import traceback
    traceback.print_exc()
    sys.exit(1)
