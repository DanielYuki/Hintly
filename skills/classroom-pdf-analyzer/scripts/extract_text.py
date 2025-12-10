#!/usr/bin/env python3
"""
Extract text from PDF file.

Supports multiple extraction methods with fallback.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import argparse

from rich.console import Console
from rich.panel import Panel

from core.pdf_extractor import PDFExtractor


console = Console()


def extract_text_from_pdf(pdf_path: str, method: str = "pdfplumber", output: str = None):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path: Path to PDF file
        method: Extraction method ('pdfplumber' or 'pypdf2')
        output: Optional output file path for extracted text
    """
    pdf = Path(pdf_path)
    
    if not pdf.exists():
        console.print(f"[red]PDF not found: {pdf}[/red]")
        sys.exit(1)
    
    console.print(f"[cyan]Extracting text from: {pdf.name}[/cyan]")
    console.print(f"Method: [yellow]{method}[/yellow]")
    
    # Extract text
    text = PDFExtractor.extract_text(pdf, method=method)
    page_count = PDFExtractor.get_page_count(pdf)
    
    console.print(f"[green]✓[/green] Extracted from [cyan]{page_count}[/cyan] pages")
    console.print(f"[green]✓[/green] Total characters: [cyan]{len(text):,}[/cyan]")
    
    # Save or display
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding='utf-8')
        console.print(f"[green]✓[/green] Saved to: [cyan]{output_path}[/cyan]")
    else:
        # Display preview
        console.print("\n" + "="*60)
        console.print("[bold]Text Preview (first 500 characters):[/bold]\n")
        console.print(text[:500])
        if len(text) > 500:
            console.print("\n[dim]... (truncated)[/dim]")
        console.print("="*60)
    
    # Show text statistics
    lines = text.split('\n')
    words = len(text.split())
    
    console.print(Panel.fit(
        f"[bold]Extraction Statistics[/bold]\n\n"
        f"Pages: [cyan]{page_count}[/cyan]\n"
        f"Characters: [cyan]{len(text):,}[/cyan]\n"
        f"Words (approx): [cyan]{words:,}[/cyan]\n"
        f"Lines: [cyan]{len(lines):,}[/cyan]",
        border_style="green"
    ))


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from PDF file"
    )
    parser.add_argument(
        "pdf_path",
        help="Path to PDF file"
    )
    parser.add_argument(
        "--method",
        choices=["pdfplumber", "pypdf2"],
        default="pdfplumber",
        help="Extraction method (default: pdfplumber)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path for extracted text (optional)"
    )
    
    args = parser.parse_args()
    
    try:
        extract_text_from_pdf(args.pdf_path, args.method, args.output)
    except KeyboardInterrupt:
        console.print("\n[yellow]Extraction cancelled[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
