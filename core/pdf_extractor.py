"""
PDF text extraction utilities for Hintly.

Supports multiple PDF libraries for robust extraction.
"""

from pathlib import Path
from typing import Optional

import pdfplumber
from PyPDF2 import PdfReader


class PDFExtractor:
    """
    Extract text from PDF files.
    
    Uses pdfplumber as primary method (better formatting)
    with PyPDF2 as fallback.
    """
    
    @staticmethod
    def extract_text(pdf_path: Path, method: str = "pdfplumber") -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            method: Extraction method ("pdfplumber" or "pypdf2")
            
        Returns:
            Extracted text as string
        """
        if method == "pdfplumber":
            try:
                return PDFExtractor._extract_with_pdfplumber(pdf_path)
            except Exception as e:
                print(f"pdfplumber failed: {e}, trying PyPDF2")
                return PDFExtractor._extract_with_pypdf2(pdf_path)
        else:
            return PDFExtractor._extract_with_pypdf2(pdf_path)
    
    @staticmethod
    def _extract_with_pdfplumber(pdf_path: Path) -> str:
        """Extract text using pdfplumber (preferred method)."""
        text_parts = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
    @staticmethod
    def _extract_with_pypdf2(pdf_path: Path) -> str:
        """Extract text using PyPDF2 (fallback method)."""
        text_parts = []
        
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
    @staticmethod
    def extract_text_by_pages(pdf_path: Path) -> list[str]:
        """
        Extract text page by page.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of strings, one per page
        """
        pages = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    pages.append(text or "")
        except Exception:
            # Fallback to PyPDF2
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                text = page.extract_text()
                pages.append(text or "")
        
        return pages
    
    @staticmethod
    def get_page_count(pdf_path: Path) -> int:
        """
        Get number of pages in PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Number of pages
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                return len(pdf.pages)
        except Exception:
            reader = PdfReader(pdf_path)
            return len(reader.pages)
    
    @staticmethod
    def chunk_text(text: str, max_chunk_size: int = 100000) -> list[str]:
        """
        Split text into chunks for LLM processing.
        
        Args:
            text: Text to split
            max_chunk_size: Maximum characters per chunk
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        # Split by paragraphs (double newline)
        paragraphs = text.split("\n\n")
        
        for para in paragraphs:
            para_size = len(para)
            
            if current_size + para_size > max_chunk_size:
                # Save current chunk
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size
        
        # Add final chunk
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        
        return chunks
