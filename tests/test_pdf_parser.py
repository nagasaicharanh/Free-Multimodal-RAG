"""
Unit tests for PDF parser module.
"""
import pytest
from pathlib import Path
from src.pdf_parser import PDFParser


class TestPDFParser:
    """Test PDF parsing functionality."""

    @pytest.fixture
    def parser(self):
        """Create a PDFParser instance."""
        return PDFParser()

    def test_table_to_markdown(self, parser):
        """Test table to markdown conversion."""
        table = [
            ["Header 1", "Header 2", "Header 3"],
            ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
            ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"],
        ]
        
        markdown = PDFParser._table_to_markdown(table)
        
        assert "Header 1" in markdown
        assert "---" in markdown
        assert "Row 1 Col 1" in markdown
        assert markdown.startswith("|")

    def test_table_to_markdown_empty(self, parser):
        """Test markdown conversion with empty table."""
        markdown = PDFParser._table_to_markdown([])
        assert markdown == ""

    def test_extract_from_nonexistent_file(self, parser):
        """Test extraction from non-existent PDF."""
        with pytest.raises(FileNotFoundError):
            parser.extract_from_pdf("nonexistent.pdf")

    def test_extract_from_valid_pdf(self, parser):
        """Test extraction from a valid PDF file."""
        # This test requires a sample PDF in data/samples/
        sample_path = Path("data/samples/sample.pdf")
        if sample_path.exists():
            result = parser.extract_from_pdf(str(sample_path))
            
            assert result.metadata["filename"] == "sample.pdf"
            assert result.metadata["num_pages"] > 0
            assert isinstance(result.text_chunks, list)
            assert isinstance(result.tables, list)
            assert isinstance(result.images, list)
        else:
            pytest.skip("Sample PDF not found in data/samples/")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
