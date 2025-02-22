# PDF Parser using PyMuPDF4llm

This project extracts text from PDF files and converts it into Markdown using the PyMuPDF4llm library.
It supports:

- Extracting the entire document or selected pages (using 0-based page numbers)
- Optional extraction of images (saved to a specified folder)
- Output as a single Markdown file or as page chunks (each page's text is stored with metadata)

## Setup

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the parser from the console: `python -m pdf_parser.parser input.pdf output.md --pages 0 1 2 --write-images --page-chunks`
4. View all available arguments: `python -m pdf_parser.parser --help`
    This will display details about each option (such as which pages to extract, image extraction options, DPI settings, and more).

For more information, please refer to the code comments in pdf_parser/parser.py.
