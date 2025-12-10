#!/usr/bin/env python3
"""
Summarize PDF from Google Classroom material.

Downloads PDF, extracts text, and generates AI-powered summary.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import argparse
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from core.classroom_api import ClassroomClient
from core.drive_api import DriveClient
from core.pdf_extractor import PDFExtractor
from core.llm_client import LLMClient, LLMProvider
from core.config import get_config


console = Console()


def summarize_pdf(
    course_id: str,
    material_id: str,
    provider: str = None,
    no_ai: bool = False,
    output_format: str = "markdown"
):
    """
    Summarize a PDF from Classroom material.
    
    Args:
        course_id: Google Classroom course ID
        material_id: Material ID
        provider: LLM provider ('anthropic' or 'openai'), defaults to config
        no_ai: Skip AI summarization, just extract text
        output_format: Output format ('markdown' or 'text')
    """
    config = get_config()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Step 1: Get material info
        task = progress.add_task("Fetching material...", total=None)
        classroom_client = ClassroomClient()
        material = classroom_client.get_material(course_id, material_id)
        course = classroom_client.get_course(course_id)
        progress.update(task, description=f"✓ Material: {material.title}")
        progress.stop_task(task)
        
        # Step 2: Download PDF
        task = progress.add_task("Downloading PDF...", total=None)
        
        # Find PDF attachment
        pdf_resource = None
        for resource in material.materials:
            if resource.type == "driveFile" and resource.url:
                pdf_resource = resource
                break
        
        if not pdf_resource:
            console.print("[red]No PDF attachment found[/red]")
            sys.exit(1)
        
        drive_client = DriveClient()
        pdf_path = drive_client.download_from_url(pdf_resource.url)
        progress.update(task, description=f"✓ Downloaded: {pdf_path.name}")
        progress.stop_task(task)
        
        # Step 3: Extract text
        task = progress.add_task("Extracting text...", total=None)
        text = PDFExtractor.extract_text(pdf_path)
        page_count = PDFExtractor.get_page_count(pdf_path)
        progress.update(task, description=f"✓ Extracted {len(text):,} characters from {page_count} pages")
        progress.stop_task(task)
        
        # Step 4: Generate summary
        if no_ai:
            summary = f"# {material.title}\n\n"
            summary += f"**Course**: {course.name}\n\n"
            summary += f"**Pages**: {page_count}\n\n"
            summary += f"## Extracted Text\n\n{text[:2000]}\n\n"
            summary += "[Summary truncated - run with AI to get full analysis]"
        else:
            task = progress.add_task("Generating AI summary...", total=None)
            
            # Select provider
            if provider:
                llm_provider = LLMProvider(provider)
                llm_client = LLMClient(llm_provider)
            else:
                llm_client = LLMClient()
            
            # Create context
            context = f"Course: {course.name} | Material: {material.title}"
            
            # Chunk text if too long
            chunks = PDFExtractor.chunk_text(text, max_chunk_size=100000)
            
            if len(chunks) == 1:
                summary = llm_client.summarize(text, context=context)
            else:
                # Multiple chunks - summarize each then combine
                console.print(f"[yellow]Large PDF: Summarizing in {len(chunks)} chunks[/yellow]")
                chunk_summaries = []
                for i, chunk in enumerate(chunks, 1):
                    progress.update(task, description=f"Summarizing chunk {i}/{len(chunks)}...")
                    chunk_summary = llm_client.summarize(chunk, context=context)
                    chunk_summaries.append(chunk_summary)
                
                # Combine summaries
                combined = "\n\n---\n\n".join(chunk_summaries)
                progress.update(task, description="Generating final summary...")
                summary = llm_client.summarize(
                    combined,
                    prompt="Consolidate these summaries into a single comprehensive summary",
                    context=context
                )
            
            progress.update(task, description="✓ Summary generated")
            progress.stop_task(task)
    
    # Add header
    header = f"# {material.title}\n\n"
    header += f"**Course**: {course.name}\n"
    header += f"**Date**: {datetime.now().strftime('%Y-%m-%d')}\n"
    header += f"**Pages**: {page_count}\n"
    header += f"**Source**: Google Classroom\n\n"
    header += "---\n\n"
    
    full_summary = header + summary
    
    # Save to file
    output_dir = config.reports_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean filename
    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in material.title)
    filename = f"{safe_title}_summary.md"
    output_path = output_dir / filename
    
    output_path.write_text(full_summary, encoding='utf-8')
    
    console.print(Panel.fit(
        f"[green]✓ Summary complete![/green]\n\n"
        f"Material: [cyan]{material.title}[/cyan]\n"
        f"Course: [cyan]{course.name}[/cyan]\n"
        f"Pages analyzed: [cyan]{page_count}[/cyan]\n"
        f"Summary saved to:\n[cyan]{output_path}[/cyan]",
        title="PDF Analysis Complete",
        border_style="green"
    ))
    
    # Display preview
    console.print("\n[bold]Summary Preview:[/bold]\n")
    console.print(full_summary[:500] + "..." if len(full_summary) > 500 else full_summary)
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Summarize PDF from Google Classroom material"
    )
    parser.add_argument(
        "--course-id",
        required=True,
        help="Google Classroom course ID"
    )
    parser.add_argument(
        "--material-id",
        required=True,
        help="Material ID"
    )
    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai"],
        help="LLM provider (overrides .env setting)"
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Skip AI summarization, just extract text"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "text"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    args = parser.parse_args()
    
    try:
        summarize_pdf(
            args.course_id,
            args.material_id,
            provider=args.provider,
            no_ai=args.no_ai,
            output_format=args.format
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Summarization cancelled[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
