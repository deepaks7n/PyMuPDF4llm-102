#!/usr/bin/env python
from typing import List, Union
import pathlib
import fitz
import pymupdf4llm
import argparse
import sys

def parse_pdf_to_markdown(
    pdf_path: str,
    pages: Union[List[int], None] = None,
    write_images: bool = False,
    image_path: str = "images",
    dpi: int = 150,
    image_format: str = "png",
    page_chunks: bool = False
) -> Union[str, List[dict]]:
    """
    Convert a PDF file to Markdown using PyMuPDF4llm.
    """
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    if pages:
        pages = [p for p in pages if 0 <= p < total_pages]
        if not pages:
            raise ValueError(f"No valid pages specified. Document has {total_pages} pages.")
    else:
        pages = list(range(total_pages))
    
    md_output = pymupdf4llm.to_markdown(
        doc,
        pages=pages,
        write_images=write_images,
        image_path=image_path,
        dpi=dpi,
        image_format=image_format,
        page_chunks=page_chunks
    )
    
    return md_output

def save_markdown(md_output: Union[str, List[dict]], output_path: str, page_chunks: bool = False) -> None:
    """
    Save the Markdown output to a file.
    """
    output_file = pathlib.Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if page_chunks and isinstance(md_output, list):
        full_md = ""
        for page_dict in md_output:
            page_number = page_dict.get("metadata", {}).get("page", "unknown")
            full_md += f"# Page {page_number}\n\n{page_dict.get('text', '')}\n\n"
        md_output = full_md

    output_file.write_text(md_output, encoding="utf-8")

def main() -> None:
    parser_cli = argparse.ArgumentParser(
        description="Parse a PDF file into Markdown using PyMuPDF4llm."
    )
    parser_cli.add_argument("input", help="Input PDF file path")
    parser_cli.add_argument("output", help="Output Markdown file path")
    parser_cli.add_argument(
        "--pages",
        nargs="+",
        type=int,
        help="List of 0-based page numbers to extract (e.g. --pages 0 1 2)"
    )
    parser_cli.add_argument(
        "--write-images",
        action="store_true",
        help="Extract images from the PDF and save them to disk"
    )
    parser_cli.add_argument(
        "--page-chunks",
        action="store_true",
        help="Output the Markdown as page chunks (each page as a separate dictionary)"
    )
    parser_cli.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="Resolution (dpi) for extracted images (default: 150)"
    )
    parser_cli.add_argument(
        "--image-path",
        default="images",
        help="Directory to store extracted images (default: 'images')"
    )
    parser_cli.add_argument(
        "--image-format",
        default="png",
        help="Format for extracted images (default: 'png')"
    )
    args = parser_cli.parse_args()

    try:
        md_output = parse_pdf_to_markdown(
            pdf_path=args.input,
            pages=args.pages,
            write_images=args.write_images,
            image_path=args.image_path,
            dpi=args.dpi,
            image_format=args.image_format,
            page_chunks=args.page_chunks
        )
        save_markdown(md_output, args.output, page_chunks=args.page_chunks)
        print(f"Successfully processed '{args.input}'.")
        print(f"Output saved to '{args.output}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()