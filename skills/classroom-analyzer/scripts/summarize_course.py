#!/usr/bin/env python3
"""
Summarize an entire Google Classroom course.

Usage:
    python summarize_course.py --course-id <ID>
    python summarize_course.py --course-id <ID> --format pdf
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


console = Console()


def summarize_course(
    course_id: str,
    output_format: str = "markdown",
    include_stats: bool = True,
    output_path: str = None,
):
    """Generate a summary of an entire course."""
    try:
        client = ClassroomClient()

        if not client.is_authenticated():
            console.print("[red]Not authenticated. Run 'python auth.py --setup' first.[/red]")
            sys.exit(1)

        console.print("[bold]Fetching course data...[/bold]")

        course = client.get_course(course_id)
        console.print(f"Course: [cyan]{course.name}[/cyan]\n")

        # Fetch all content
        console.print("  Fetching coursework...")
        coursework = client.list_coursework(course_id)
        console.print(f"  Found {len(coursework)} coursework items")

        console.print("  Fetching materials...")
        materials = client.list_materials(course_id)
        console.print(f"  Found {len(materials)} materials\n")

        # Generate summary
        summary_parts = []
        summary_parts.append(f"This course has {len(coursework)} assignments/activities and {len(materials)} study materials.")

        if coursework:
            types = {}
            for cw in coursework:
                t = cw.work_type.replace("_", " ").title()
                types[t] = types.get(t, 0) + 1
            type_str = ", ".join(f"{count} {name}" for name, count in types.items())
            summary_parts.append(f"Coursework includes: {type_str}.")

        summary = " ".join(summary_parts)

        # Generate output
        output = None
        if output_format == "pdf":
            generator = PDFGenerator()
            output = generator.generate_course_summary(
                course=course,
                coursework_count=len(coursework),
                materials_count=len(materials),
                summary=summary,
                output_path=Path(output_path) if output_path else None,
            )
        else:  # markdown
            writer = MarkdownWriter()
            output = writer.generate_course_overview(
                course=course,
                coursework=coursework if include_stats else None,
                materials=materials if include_stats else None,
                summary=summary,
                output_path=Path(output_path) if output_path else None,
            )

        console.print(Panel(
            f"[green]✓ Course summary generated![/green]\n\n"
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
    parser = argparse.ArgumentParser(description="Summarize a Google Classroom course")
    parser.add_argument(
        "--course-id",
        required=True,
        help="Course ID",
    )
    parser.add_argument(
        "--format",
        choices=["pdf", "markdown"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--include-stats",
        action="store_true",
        default=True,
        help="Include detailed statistics",
    )
    parser.add_argument(
        "--output",
        help="Custom output path",
    )

    args = parser.parse_args()
    summarize_course(
        course_id=args.course_id,
        output_format=args.format,
        include_stats=args.include_stats,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
