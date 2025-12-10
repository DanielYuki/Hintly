#!/usr/bin/env python3
"""
Test script for Phase 2A features.

Tests Drive API, PDF extraction, and LLM client.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel

from core.classroom_api import ClassroomClient
from core.drive_api import DriveClient
from core.pdf_extractor import PDFExtractor
from core.llm_client import LLMClient, LLMProvider


console = Console()


def test_drive_api():
    """Test Google Drive file download."""
    console.print("\n[bold cyan]Test 1: Google Drive API[/bold cyan]")
    
    try:
        # Test URL parsing
        test_url = "https://drive.google.com/file/d/1ABC123xyz/view"
        file_id = DriveClient.extract_file_id_from_url(test_url)
        console.print(f"✓ URL parsing works: {file_id}")
        
        # Test client initialization
        client = DriveClient()
        console.print("✓ DriveClient initialized")
        
        return True
    except Exception as e:
        console.print(f"[red]✗ Drive API test failed: {e}[/red]")
        return False


def test_pdf_extractor():
    """Test PDF text extraction."""
    console.print("\n[bold cyan]Test 2: PDF Extractor[/bold cyan]")
    
    try:
        # Test with a sample PDF (if exists)
        test_pdf = Path("outputs/pdfs/test.pdf")
        
        if test_pdf.exists():
            text = PDFExtractor.extract_text(test_pdf)
            page_count = PDFExtractor.get_page_count(test_pdf)
            console.print(f"✓ Extracted {len(text)} characters from {page_count} pages")
            
            # Test chunking
            chunks = PDFExtractor.chunk_text(text, max_chunk_size=1000)
            console.print(f"✓ Text chunking works: {len(chunks)} chunks")
        else:
            console.print("[yellow]⚠ No test PDF found, skipping extraction test[/yellow]")
        
        return True
    except Exception as e:
        console.print(f"[red]✗ PDF extraction test failed: {e}[/red]")
        return False


def test_llm_client():
    """Test LLM client initialization."""
    console.print("\n[bold cyan]Test 3: LLM Client[/bold cyan]")
    
    try:
        from core.config import get_config
        config = get_config()
        
        console.print(f"Configured provider: [cyan]{config.llm_provider}[/cyan]")
        
        # Check API keys
        if config.llm_provider == "anthropic":
            if config.anthropic_api_key:
                # Test initialization
                client = LLMClient()
                console.print("✓ Anthropic client initialized")
                
                # Test simple summarization
                test_text = "This is a test. It covers basic concepts."
                summary = client.summarize(test_text, context="Test")
                console.print(f"✓ Summarization works ({len(summary)} chars)")
                console.print(f"Sample: {summary[:100]}...")
                return True
            else:
                console.print("[yellow]⚠ ANTHROPIC_API_KEY not set in .env[/yellow]")
                return False
                
        elif config.llm_provider == "openai":
            if config.openai_api_key:
                # Test initialization
                client = LLMClient()
                console.print("✓ OpenAI client initialized")
                
                # Test simple summarization
                test_text = "This is a test. It covers basic concepts."
                summary = client.summarize(test_text, context="Test")
                console.print(f"✓ Summarization works ({len(summary)} chars)")
                console.print(f"Sample: {summary[:100]}...")
                return True
            else:
                console.print("[yellow]⚠ OPENAI_API_KEY not set in .env[/yellow]")
                return False
        else:
            console.print(f"[yellow]⚠ Unknown provider: {config.llm_provider}[/yellow]")
            return False
            
    except Exception as e:
        console.print(f"[red]✗ LLM client test failed: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False


def test_classroom_integration():
    """Test downloading a PDF from Classroom."""
    console.print("\n[bold cyan]Test 4: Classroom + Drive Integration[/bold cyan]")
    
    try:
        # Get a course with materials
        classroom_client = ClassroomClient()
        
        console.print("Fetching courses...")
        courses = classroom_client.list_courses(state="ACTIVE")
        
        if not courses:
            console.print("[yellow]⚠ No active courses found[/yellow]")
            return False
        
        # Get materials from first course
        course = courses[0]
        console.print(f"Using course: [cyan]{course.name}[/cyan]")
        
        materials = classroom_client.list_materials(course.id)
        
        if not materials:
            console.print("[yellow]⚠ No materials found in course[/yellow]")
            return False
        
        # Find a PDF material
        pdf_material = None
        for mat in materials:
            for resource in mat.materials:
                if resource.type == "driveFile" and resource.url:
                    pdf_material = (mat, resource)
                    break
            if pdf_material:
                break
        
        if not pdf_material:
            console.print("[yellow]⚠ No PDF materials found[/yellow]")
            return False
        
        material, resource = pdf_material
        console.print(f"Found PDF: [cyan]{resource.title}[/cyan]")
        
        # Download it
        drive_client = DriveClient()
        console.print("Downloading...")
        pdf_path = drive_client.download_from_url(resource.url)
        console.print(f"✓ Downloaded to: {pdf_path}")
        
        # Extract text
        console.print("Extracting text...")
        text = PDFExtractor.extract_text(pdf_path)
        console.print(f"✓ Extracted {len(text)} characters")
        console.print(f"Preview: {text[:200]}...")
        
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Integration test failed: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False


def main():
    console.print(Panel.fit(
        "[bold]Phase 2A Feature Tests[/bold]\n\n"
        "Testing Drive API, PDF extraction, and LLM client",
        border_style="cyan"
    ))
    
    results = []
    
    # Run tests
    results.append(("Drive API", test_drive_api()))
    results.append(("PDF Extractor", test_pdf_extractor()))
    results.append(("LLM Client", test_llm_client()))
    results.append(("Classroom Integration", test_classroom_integration()))
    
    # Summary
    console.print("\n" + "="*60)
    console.print("[bold]Test Summary[/bold]\n")
    
    for name, passed in results:
        status = "[green]✓ PASSED[/green]" if passed else "[red]✗ FAILED[/red]"
        console.print(f"{name:.<40} {status}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    console.print(f"\n[bold]Result: {passed_count}/{total_count} tests passed[/bold]")
    
    if passed_count == total_count:
        console.print("\n[green]🎉 All tests passed![/green]")
    else:
        console.print("\n[yellow]⚠ Some tests failed. Check errors above.[/yellow]")


if __name__ == "__main__":
    main()
