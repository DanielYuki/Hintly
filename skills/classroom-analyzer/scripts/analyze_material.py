#!/usr/bin/env python3
"""
Analyze a Google Classroom material and generate a report.

Usage:
    python analyze_material.py --course-id <ID> --material-id <ID>
    python analyze_material.py --course-id <ID> --material-id <ID> --format pdf
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from rich.console import Console
from rich.panel import Panel

from core.classroom_api import ClassroomClient
from core.pdf_generator import PDFGenerator
from core.markdown_writer import MarkdownWriter
from core.json_exporter import JSONExporter


console = Console()


def analyze_material(
    course_id: str,
    material_id: str,
    output_format: str = "markdown",
    include_analysis: bool = True,
    output_path: str = None,
):
    """Analyze a material and generate a report."""
    try:
        client = ClassroomClient()

        if not client.is_authenticated():
            console.print("[red]Not authenticated. Run 'python auth.py --setup' first.[/red]")
            sys.exit(1)

        console.print("[bold]Fetching material...[/bold]")

        course = client.get_course(course_id)
        material = client.get_material(course_id, material_id)

        console.print(f"Found: [cyan]{material.title}[/cyan] in [green]{course.name}[/green]\n")

        # Generate analysis content
        # In a real implementation, this would call an LLM for analysis
        summary = f"This material '{material.title}' provides educational content for the course."
        if material.description:
            summary += f" {material.description[:200]}"

        key_topics = []
        if material.materials:
            for mat in material.materials:
                if mat.title:
                    key_topics.append(mat.title)

        analysis = ""
        if include_analysis:
            analysis = (
                f"This material contains {len(material.materials)} attached resource(s). "
                "Students should review all attached materials carefully. "
            )
            if material.materials:
                types = set(m.type for m in material.materials)
                analysis += f"Resource types include: {', '.join(types)}."

        # Generate output based on format
        output = None
        if output_format == "pdf":
            generator = PDFGenerator()
            output = generator.generate_material_report(
                material=material,
                course=course,
                analysis=analysis,
                summary=summary,
                key_topics=key_topics if key_topics else None,
                output_path=Path(output_path) if output_path else None,
            )
        elif output_format == "markdown":
            writer = MarkdownWriter()
            output = writer.generate_material_summary(
                material=material,
                course=course,
                analysis=analysis,
                summary=summary,
                key_topics=key_topics if key_topics else None,
                output_path=Path(output_path) if output_path else None,
            )
        elif output_format == "json":
            exporter = JSONExporter()
            output = exporter.export_materials_list(
                course=course,
                materials=[material],
                output_path=Path(output_path) if output_path else None,
            )

        console.print(Panel(
            f"[green]✓ Report generated successfully![/green]\n\n"
            f"Output: {output}\n"
            f"Format: {output_format.upper()}",
            title="Success",
            border_style="green",
        ))

        return output

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Analyze a Google Classroom material")
    parser.add_argument(
        "--course-id",
        required=True,
        help="Course ID",
    )
    parser.add_argument(
        "--material-id",
        required=True,
        help="Material ID",
    )
    parser.add_argument(
        "--format",
        choices=["pdf", "markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--include-analysis",
        action="store_true",
        default=True,
        help="Include AI-generated analysis",
    )
    parser.add_argument(
        "--output",
        help="Custom output path",
    )

    args = parser.parse_args()
    analyze_material(
        course_id=args.course_id,
        material_id=args.material_id,
        output_format=args.format,
        include_analysis=args.include_analysis,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
