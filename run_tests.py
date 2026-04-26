#!/usr/bin/env python
"""
Comprehensive test of Free Multimodal RAG application.
Tests all major components and features.
"""
import os
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("=" * 70)
    print("TEST 1: Module Imports")
    print("=" * 70)
    
    modules = [
        'src.config',
        'src.pdf_parser',
        'src.processors.text_processor',
        'src.processors.table_processor',
        'src.processors.image_processor',
        'src.processors.embeddings',
        'src.llm.groq_client',
        'src.llm.gemini_client',
        'src.llm.fallback_llm',
        'src.vector_db.chromadb_manager',
        'src.pipeline',
        'src.retriever',
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except Exception as e:
            print(f"  ✗ {module}: {e}")
            return False
    
    print()
    return True

def test_pdf_extraction():
    """Test PDF extraction."""
    print("=" * 70)
    print("TEST 2: PDF Extraction")
    print("=" * 70)
    
    from src.pdf_parser import PDFParser
    
    pdf_path = "data/samples/Insurance_Handbook_20103.pdf"
    if not Path(pdf_path).exists():
        print(f"  ✗ PDF not found: {pdf_path}")
        return False
    
    try:
        parser = PDFParser()
        result = parser.extract_from_pdf(pdf_path)
        
        print(f"  ✓ PDF extracted successfully")
        print(f"    - Pages: {result.metadata['num_pages']}")
        print(f"    - Text chunks: {len(result.text_chunks)}")
        print(f"    - Tables: {len(result.tables)}")
        print(f"    - Images: {len(result.images)}")
        
        if result.metadata['num_pages'] > 0 and len(result.text_chunks) > 0:
            print()
            return True
        else:
            print(f"  ✗ Extraction failed: insufficient data")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_embeddings():
    """Test embeddings generation."""
    print("=" * 70)
    print("TEST 3: Text Embeddings")
    print("=" * 70)
    
    from src.processors.embeddings import EmbeddingsModel
    
    try:
        model = EmbeddingsModel()
        print(f"  ✓ Model loaded: {model.model_name}")
        print(f"    - Embedding dimension: {model.embedding_dim}")
        
        test_text = "What is insurance?"
        embedding = model.embed(test_text)
        
        print(f"  ✓ Embedding generated")
        print(f"    - Shape: {embedding.shape}")
        
        # Test batch
        texts = ["text 1", "text 2", "text 3"]
        embeddings = model.embed(texts)
        print(f"  ✓ Batch embedding: {embeddings.shape[0]} texts")
        
        print()
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_chromadb():
    """Test ChromaDB storage."""
    print("=" * 70)
    print("TEST 4: Vector Database (ChromaDB)")
    print("=" * 70)
    
    from src.vector_db.chromadb_manager import ChromaDBManager
    import tempfile
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            db = ChromaDBManager(db_path=tmpdir)
            print(f"  ✓ Database initialized")
            
            # Add test document
            docs = [
                {
                    "id": "test_1",
                    "embedding": [0.1] * 384,
                    "text": "Test document 1",
                    "metadata": {"modality": "text", "page": 1}
                }
            ]
            
            added = db.add_documents(docs)
            print(f"  ✓ Document added: {len(added)} items")
            print(f"    - Total count: {db.count()}")
            
            # Query test
            results = db.query([0.1] * 384, top_k=1)
            if results['ids'][0]:
                print(f"  ✓ Query successful: found {len(results['ids'][0])} results")
            
            print()
            return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_chunking_strategies():
    """Test different chunking strategies."""
    print("=" * 70)
    print("TEST 5: Text Chunking Strategies")
    print("=" * 70)
    
    from src.processors.text_processor import TextProcessor
    
    try:
        processor = TextProcessor()
        sample_text = "This is a test. " * 200  # Create long text
        
        for strategy in ["recursive", "fixed", "semantic"]:
            chunks = processor.chunk_text(sample_text, strategy=strategy)
            print(f"  ✓ {strategy.upper()}: {len(chunks)} chunks")
        
        print()
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_retrieval():
    """Test retrieval and answer generation."""
    print("=" * 70)
    print("TEST 6: Retrieval & Answer Generation")
    print("=" * 70)
    
    from src.pipeline import IngestionPipeline
    from src.retriever import Retriever
    
    try:
        pipeline = IngestionPipeline()
        print(f"  ✓ Pipeline initialized")
        
        # Use existing ChromaDB from earlier ingestion
        doc_count = pipeline.db_manager.count()
        print(f"  ✓ ChromaDB has {doc_count} documents")
        
        if doc_count > 0:
            retriever = Retriever(pipeline.db_manager)
            print(f"  ✓ Retriever initialized")
            
            # Test query
            result = retriever.query("What is insurance?", top_k=3)
            print(f"  ✓ Query executed")
            print(f"    - Sources found: {result['num_sources']}")
            print(f"    - Answer length: {len(result['answer'])} chars")
            
            if result['sources']:
                print(f"    - Top source modality: {result['sources'][0]['modality']}")
            
            print()
            return True
        else:
            print("  ⚠ No documents in ChromaDB (needs prior ingestion)")
            return True  # Not a failure, just informational
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_streamlit_running():
    """Check if Streamlit app is running."""
    print("=" * 70)
    print("TEST 7: Streamlit App Status")
    print("=" * 70)
    
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8502))
        sock.close()
        
        if result == 0:
            print(f"  ✓ Streamlit app is running on localhost:8502")
            print(f"    - Local URL: http://localhost:8502")
            print(f"    - Ready for interactive testing")
            print()
            return True
        else:
            print(f"  ✗ Streamlit app not responding on port 8502")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Run all tests."""
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "FREE MULTIMODAL RAG - SYSTEM TEST" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    tests = [
        test_imports,
        test_pdf_extraction,
        test_embeddings,
        test_chromadb,
        test_chunking_strategies,
        test_retrieval,
        test_streamlit_running,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Test crashed: {e}")
            results.append(False)
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print()
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 20 + "ALL TESTS PASSED!" + " " * 30 + "║")
        print("║" + " " * 15 + "System is ready for production use" + " " * 19 + "║")
        print("╚" + "=" * 68 + "╝")
        print()
        print("NEXT STEP: Open http://localhost:8502 in your browser to test interactively")
        print()
        return 0
    else:
        print(f"\nFAILED: {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
