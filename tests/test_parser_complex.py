import pathlib
import pytest
import fitz  # PyMuPDF
from pdf_parser import parser
from typing import List, Union

# Fixture to create a simple one‑page PDF for basic tests.
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
    """
    Test basic PDF parsing without special options.
    This test creates a single‑page PDF and verifies that the output is a string
    containing the expected text.
    """
    try:
        md_output = parser.parse_pdf_to_markdown(str(test_pdf_path))
        assert isinstance(md_output, str), "Basic parsing should return a string"
        assert "This is a test PDF." in md_output, "Expected text not found in output"
    except Exception as e:
        pytest.fail(f"Basic parsing failed with error: {e}")

def test_multiple_pages_extraction(tmp_path: pathlib.Path):
    """
    Test multi-page PDF extraction.
    This test creates a PDF with two pages with distinct text on each page.
    It verifies that the output Markdown (in non‑chunk mode) contains the text from both pages.
    """
    pdf_path = tmp_path / "multi_page.pdf"
    doc = fitz.open()
    # Create Page 1
    page1 = doc.new_page()
    page1.insert_text((72, 72), "First page: Hello World!")
    # Create Page 2
    page2 = doc.new_page()
    page2.insert_text((72, 72), "Second page: Goodbye World!")
    doc.save(str(pdf_path))
    doc.close()

    md_output = parser.parse_pdf_to_markdown(str(pdf_path), page_chunks=False)
    assert "Hello World!" in md_output, "First page text missing"
    assert "Goodbye World!" in md_output, "Second page text missing"

def test_selective_page_extraction(tmp_path: pathlib.Path):
    """
    Test selective page extraction.
    This test creates a PDF with three pages and extracts only the second page.
    It verifies that the output contains text only from the specified page.
    """
    pdf_path = tmp_path / "selective.pdf"
    doc = fitz.open()
    # Page 1
    page1 = doc.new_page()
    page1.insert_text((72, 72), "Page One Content")
    # Page 2
    page2 = doc.new_page()
    page2.insert_text((72, 72), "Page Two Content")
    # Page 3
    page3 = doc.new_page()
    page3.insert_text((72, 72), "Page Three Content")
    doc.save(str(pdf_path))
    doc.close()

    # Extract only page 1 (i.e. the second page, since pages are 0-indexed)
    md_output = parser.parse_pdf_to_markdown(str(pdf_path), pages=[1], page_chunks=False)
    assert "Page Two Content" in md_output, "Expected page text not found"
    assert "Page One Content" not in md_output, "Unrequested page text found"
    assert "Page Three Content" not in md_output, "Unrequested page text found"

def test_page_chunks_output(tmp_path: pathlib.Path):
    """
    Test the page chunks output mode.
    This test creates a PDF with two pages and parses it with page_chunks=True.
    It verifies that the output is a list of dictionaries where each dictionary
    contains 'text' and 'metadata' (including a 1-based page number).
    """
    pdf_path = tmp_path / "chunks.pdf"
    doc = fitz.open()
    # Page 1
    page1 = doc.new_page()
    page1.insert_text((72, 72), "Chunk Test: Page 1")
    # Page 2
    page2 = doc.new_page()
    page2.insert_text((72, 72), "Chunk Test: Page 2")
    doc.save(str(pdf_path))
    doc.close()

    md_chunks = parser.parse_pdf_to_markdown(str(pdf_path), page_chunks=True)
    assert isinstance(md_chunks, list), "Expected output to be a list when using page_chunks"
    assert len(md_chunks) == 2, "Expected two page chunks"
    for i, chunk in enumerate(md_chunks):
        assert "text" in chunk, f"Chunk {i} missing 'text' key"
        assert "metadata" in chunk, f"Chunk {i} missing 'metadata' key"
        assert chunk["metadata"].get("page") == i + 1, f"Chunk {i} page metadata incorrect"
        if i == 0:
            assert "Page 1" in chunk["text"], "Page 1 text missing in chunk"
        elif i == 1:
            assert "Page 2" in chunk["text"], "Page 2 text missing in chunk"

def test_save_markdown_with_chunks(tmp_path: pathlib.Path):
    """
    Test saving markdown output when provided with page chunks.
    This test supplies a list of page dictionaries to save_markdown() and verifies
    that the resulting file contains headers for each page.
    """
    output_path = tmp_path / "output_chunks.md"
    test_chunks = [
        {"text": "Page 1 content", "metadata": {"page": 1}},
        {"text": "Page 2 content", "metadata": {"page": 2}},
    ]
    parser.save_markdown(test_chunks, str(output_path), page_chunks=True)
    content = output_path.read_text(encoding="utf-8")
    assert "# Page 1" in content, "Output should contain header for page 1"
    assert "# Page 2" in content, "Output should contain header for page 2"