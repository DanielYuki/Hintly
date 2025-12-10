#!/usr/bin/env python3
"""
Download PDF from Google Classroom material.

Uses Google Drive API to download PDFs linked in Classroom materials.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import argparse

from rich.console import Console
from rich.panel import Panel

from core.classroom_api import ClassroomClient
from core.drive_api import DriveClient
from core.config import get_config


console = Console()


def download_pdf(course_id: str, material_id: str, output_path: str = None) -> Path:
    """
    Download a PDF from a Classroom material.
    
    Args:
        course_id: Google Classroom course ID
        material_id: Material ID
        output_path: Optional output path for PDF
        
    Returns:
        Path to downloaded PDF
    """
    config = get_config()
    
    # Get material from Classroom
    console.print(f"[cyan]Fetching material {material_id}...[/cyan]")
    classroom_client = ClassroomClient()
    material = classroom_client.get_material(course_id, material_id)
    
    console.print(f"[green]✓[/green] Material: [bold]{material.title}[/bold]")
    
    # Find PDF attachment
    pdf_resource = None
    for resource in material.materials:
        if resource.type == "driveFile" and resource.url:
            # Check if it's a PDF (you could add more validation)
            if "pdf" in resource.title.lower() or resource.url:
                pdf_resource = resource
                break
    
    if not pdf_resource:
        console.print("[red]No PDF attachment found in this material[/red]")
        sys.exit(1)
    
    console.print(f"[green]✓[/green] Found file: [cyan]{pdf_resource.title}[/cyan]")
    
    # Download from Drive
    console.print("[cyan]Downloading from Google Drive...[/cyan]")
    drive_client = DriveClient()
    
    if output_path:
        output = Path(output_path)
    else:
        output = config.pdfs_dir / pdf_resource.title
    
    pdf_path = drive_client.download_from_url(pdf_resource.url, output)
    
    console.print(Panel.fit(
        f"[green]✓ PDF downloaded successfully![/green]\n\n"
        f"Location: [cyan]{pdf_path}[/cyan]\n"
        f"Size: {pdf_path.stat().st_size / 1024:.1f} KB",
        title="Download Complete",
        border_style="green"
    ))
    
    return pdf_path


def main():
    parser = argparse.ArgumentParser(
        description="Download PDF from Google Classroom material"
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
        "--output",
        "-o",
        help="Output path for PDF (optional)"
    )
    
    args = parser.parse_args()
    
    try:
        download_pdf(args.course_id, args.material_id, args.output)
    except KeyboardInterrupt:
        console.print("\n[yellow]Download cancelled[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
