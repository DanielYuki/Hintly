#!/usr/bin/env python3
"""
Export Google Classroom data to JSON.

Usage:
    python export_data.py --course-id <ID>
    python export_data.py --course-id <ID> --all
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from rich.console import Console
from rich.panel import Panel

from core.classroom_api import ClassroomClient
from core.json_exporter import JSONExporter


console = Console()


def export_data(
    course_id: str,
    include_coursework: bool = False,
    include_materials: bool = False,
    include_announcements: bool = False,
    include_all: bool = False,
    output_path: str = None,
):
    """Export course data to JSON."""
    try:
        client = ClassroomClient()

        if not client.is_authenticated():
            console.print("[red]Not authenticated. Run 'python auth.py --setup' first.[/red]")
            sys.exit(1)

        console.print("[bold]Exporting course data...[/bold]")

        course = client.get_course(course_id)
        console.print(f"Course: [cyan]{course.name}[/cyan]\n")

        # Determine what to include
        if include_all:
            include_coursework = True
            include_materials = True
            include_announcements = True

        coursework = None
        materials = None
        announcements = None

        if include_coursework:
            console.print("  Fetching coursework...")
            coursework = client.list_coursework(course_id)
            console.print(f"  Found {len(coursework)} items")

        if include_materials:
            console.print("  Fetching materials...")
            materials = client.list_materials(course_id)
            console.print(f"  Found {len(materials)} items")

        if include_announcements:
            console.print("  Fetching announcements...")
            announcements = client.list_announcements(course_id)
            console.print(f"  Found {len(announcements)} items")

        console.print()

        # Export
        exporter = JSONExporter()
        output = exporter.export_course(
            course=course,
            coursework=coursework,
            materials=materials,
            announcements=announcements,
            output_path=Path(output_path) if output_path else None,
        )

        console.print(Panel(
            f"[green]✓ Data exported successfully![/green]\n\n"
            f"Output: {output}",
            title="Success",
            border_style="green",
        ))

        return output

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Export Google Classroom data to JSON")
    parser.add_argument(
        "--course-id",
        required=True,
        help="Course ID",
    )
    parser.add_argument(
        "--include-coursework",
        action="store_true",
        help="Include coursework items",
    )
    parser.add_argument(
        "--include-materials",
        action="store_true",
        help="Include materials",
    )
    parser.add_argument(
        "--include-announcements",
        action="store_true",
        help="Include announcements",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="include_all",
        help="Include everything",
    )
    parser.add_argument(
        "--output",
        help="Custom output path",
    )

    args = parser.parse_args()
    export_data(
        course_id=args.course_id,
        include_coursework=args.include_coursework,
        include_materials=args.include_materials,
        include_announcements=args.include_announcements,
        include_all=args.include_all,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
