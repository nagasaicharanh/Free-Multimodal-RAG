"""
Integration tests for the end-to-end RAG pipeline.
"""
import pytest
import tempfile
from pathlib import Path
from src.pipeline import IngestionPipeline
from src.retriever import Retriever
from src.vector_db.chromadb_manager import ChromaDBManager
from src.processors.text_processor import TextProcessor
from src.processors.table_processor import TableProcessor
from src.processors.image_processor import ImageProcessor
from src.processors.embeddings import EmbeddingsModel


class TestEndToEndPipeline:
    """Test complete pipeline from PDF to answer."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary ChromaDB for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ChromaDBManager(db_path=tmpdir)

    def test_text_chunking_strategies(self):
        """Test all text chunking strategies."""
        processor = TextProcessor()
        sample_text = "This is test text. " * 100
        
        strategies = ["recursive", "fixed", "semantic"]
        for strategy in strategies:
            chunks = processor.chunk_text(sample_text, strategy=strategy)
            assert len(chunks) > 0
            assert all("text" in chunk for chunk in chunks)
            assert all("strategy" in chunk for chunk in chunks)

    def test_embeddings_generation(self):
        """Test embedding generation."""
        model = EmbeddingsModel()
        
        # Single text
        embedding = model.embed("Hello world")
        assert embedding.shape[0] == model.embedding_dim
        
        # Multiple texts
        texts = ["Hello", "World", "Test"]
        embeddings = model.embed(texts)
        assert embeddings.shape[0] == 3
        assert embeddings.shape[1] == model.embedding_dim

    def test_chromadb_operations(self, temp_db):
        """Test ChromaDB add and query."""
        # Add documents
        docs = [
            {
                "id": "doc1",
                "embedding": [0.1] * 384,
                "text": "Sample text 1",
                "metadata": {"modality": "text"},
            },
            {
                "id": "doc2",
                "embedding": [0.2] * 384,
                "text": "Sample text 2",
                "metadata": {"modality": "text"},
            },
        ]
        
        added = temp_db.add_documents(docs)
        assert len(added) == 2
        assert temp_db.count() == 2
        
        # Query
        results = temp_db.query([0.1] * 384, top_k=1)
        assert len(results["ids"][0]) == 1

    def test_retriever_fallback(self, temp_db):
        """Test retriever with fallback LLM."""
        retriever = Retriever(temp_db)
        
        # Add a sample document
        embedding = EmbeddingsModel().embed("Sample document content")
        docs = [
            {
                "id": "test1",
                "embedding": embedding.tolist(),
                "text": "Sample document content",
                "metadata": {"modality": "text"},
            }
        ]
        temp_db.add_documents(docs)
        
        # Query should work even if Groq is unavailable
        result = retriever.query("What is this about?")
        assert "question" in result
        assert "answer" in result
        assert "sources" in result

    def test_source_attribution(self, temp_db):
        """Test source attribution formatting."""
        retriever = Retriever(temp_db)
        
        # Add documents with different modalities
        embedding = EmbeddingsModel().embed("Test text")
        
        docs = [
            {
                "id": "text1",
                "embedding": embedding.tolist(),
                "text": "Text content",
                "metadata": {"modality": "text", "page": 1},
            },
            {
                "id": "table1",
                "embedding": embedding.tolist(),
                "text": "Table content",
                "metadata": {"modality": "table", "page": 2, "rows": 5},
            },
            {
                "id": "image1",
                "embedding": embedding.tolist(),
                "text": "Image content",
                "metadata": {"modality": "image", "page": 3},
            },
        ]
        temp_db.add_documents(docs)
        
        # Query and verify source badges
        result = retriever.query("content", top_k=3)
        sources = result["sources"]
        
        assert len(sources) == 3
        assert any("[TEXT]" in s["source_badge"] for s in sources)
        assert any("[TABLE]" in s["source_badge"] for s in sources)
        assert any("[IMAGE]" in s["source_badge"] for s in sources)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
