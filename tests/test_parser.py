import pathlib
import pytest
import fitz  # PyMuPDF
from pdf_parser import parser
from typing import List, Union

# Fixture to create a valid test PDF with one page.
@pytest.fixture
def test_pdf_path(tmp_path: pathlib.Path) -> pathlib.Path:
    pdf_path = tmp_path / "test.pdf"
    doc = fitz.open()  # Create a new PDF document
    page = doc.new_page()  # Add a page
    page.insert_text((72, 72), "This is a test PDF.")
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path

def test_parse_pdf_to_markdown_basic(test_pdf_path: pathlib.Path):
    """Test basic PDF parsing without special options."""
    try:
        md_output = parser.parse_pdf_to_markdown(str(test_pdf_path))
        assert isinstance(md_output, str), "Basic parsing should return a string"
        assert "This is a test PDF." in md_output, "Expected text not found in output"
    except Exception as e:
        pytest.fail(f"Basic parsing failed with error: {e}")

def test_parse_pdf_with_page_chunks(test_pdf_path: pathlib.Path):
    """Test PDF parsing with page chunks enabled."""
    try:
        md_output = parser.parse_pdf_to_markdown(
            str(test_pdf_path),
            page_chunks=True
        )
        assert isinstance(md_output, list), "Page chunks output should be a list"
        # Check that each chunk has the necessary keys.
        for chunk in md_output:
            assert "text" in chunk, "Page chunk should contain a 'text' key"
            assert "metadata" in chunk, "Page chunk should contain a 'metadata' key"
            assert "page" in chunk["metadata"], "Metadata must include a 'page' number"
    except Exception as e:
        pytest.fail(f"Page chunks parsing failed with error: {e}")

def test_save_markdown(tmp_path: pathlib.Path):
    """Test saving markdown output to a file."""
    output_path = tmp_path / "output.md"
    test_content = "# Test Markdown\nThis is a test."
    parser.save_markdown(test_content, str(output_path))
    assert output_path.exists(), "Output file should exist"
    assert output_path.read_text(encoding="utf-8") == test_content, "File content should match input"

def test_save_markdown_with_chunks(tmp_path: pathlib.Path):
    """Test saving markdown with page chunks."""
    output_path = tmp_path / "output_chunks.md"
    test_chunks = [
        {"text": "Page 1 content", "metadata": {"page": 1}},
        {"text": "Page 2 content", "metadata": {"page": 2}},
    ]
    parser.save_markdown(test_chunks, str(output_path), page_chunks=True)
    content = output_path.read_text(encoding="utf-8")
    assert "# Page 1" in content, "Output should contain page 1 header"
    assert "# Page 2" in content, "Output should contain page 2 header"