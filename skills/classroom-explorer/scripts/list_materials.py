#!/usr/bin/env python3
"""
List materials for a Google Classroom course.

Usage:
    python list_materials.py --course-id <ID>
    python list_materials.py --course-id <ID> --format json
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from rich.console import Console
from rich.table import Table

from core.classroom_api import ClassroomClient
from core.config import get_config


console = Console()


def list_materials(course_id: str, output_format: str = "table"):
    """List materials for a course."""
    try:
        client = ClassroomClient()

        if not client.is_authenticated():
            console.print("[red]Not authenticated. Run 'python auth.py --setup' first.[/red]")
            sys.exit(1)

        # Get course info for context
        course = client.get_course(course_id)
        materials = client.list_materials(course_id)

        if not materials:
            console.print(f"[yellow]No materials found for '{course.name}'.[/yellow]")
            return

        if output_format == "json":
            output = {
                "course": {
                    "id": course.id,
                    "name": course.name,
                },
                "count": len(materials),
                "materials": [
                    {
                        "id": mat.id,
                        "title": mat.title,
                        "description": mat.description,
                        "state": mat.state,
                        "attachments": [
                            {"type": m.type, "title": m.title, "url": m.url}
                            for m in mat.materials
                        ],
                        "creation_time": mat.creation_time,
                        "alternate_link": mat.alternate_link,
                    }
                    for mat in materials
                ],
            }
            print(json.dumps(output, indent=2))
        else:
            # Table format
            table = Table(title=f"Materials for '{course.name}' ({len(materials)})")
            table.add_column("ID", style="cyan")
            table.add_column("Title", style="bold")
            table.add_column("Description", style="dim", max_width=40)
            table.add_column("Attachments", style="green")

            for mat in materials:
                desc = mat.description or ""
                if len(desc) > 40:
                    desc = desc[:37] + "..."

                attachment_count = len(mat.materials)
                attachments = f"{attachment_count} item(s)" if attachment_count > 0 else "-"

                table.add_row(
                    mat.id,
                    mat.title[:40] + ("..." if len(mat.title) > 40 else ""),
                    desc,
                    attachments,
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="List materials for a course")
    parser.add_argument(
        "--course-id",
        required=True,
        help="Course ID (use list_courses.py to find)",
    )
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )

    args = parser.parse_args()
    list_materials(course_id=args.course_id, output_format=args.format)


if __name__ == "__main__":
    main()
