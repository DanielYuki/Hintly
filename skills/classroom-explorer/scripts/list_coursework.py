#!/usr/bin/env python3
"""
List coursework (assignments) for a Google Classroom course.

Usage:
    python list_coursework.py --course-id <ID>
    python list_coursework.py --course-id <ID> --format json
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


def list_coursework(course_id: str, output_format: str = "table"):
    """List coursework for a course."""
    try:
        client = ClassroomClient()

        if not client.is_authenticated():
            console.print("[red]Not authenticated. Run 'python auth.py --setup' first.[/red]")
            sys.exit(1)

        # Get course info for context
        course = client.get_course(course_id)
        coursework = client.list_coursework(course_id)

        if not coursework:
            console.print(f"[yellow]No coursework found for '{course.name}'.[/yellow]")
            return

        if output_format == "json":
            output = {
                "course": {
                    "id": course.id,
                    "name": course.name,
                },
                "count": len(coursework),
                "coursework": [
                    {
                        "id": cw.id,
                        "title": cw.title,
                        "type": cw.work_type,
                        "description": cw.description,
                        "max_points": cw.max_points,
                        "due_date": cw.due_date,
                        "due_time": cw.due_time,
                        "state": cw.state,
                        "materials": [
                            {"type": m.type, "title": m.title, "url": m.url}
                            for m in cw.materials
                        ],
                        "alternate_link": cw.alternate_link,
                    }
                    for cw in coursework
                ],
            }
            print(json.dumps(output, indent=2))
        else:
            # Table format
            table = Table(title=f"Coursework for '{course.name}' ({len(coursework)})")
            table.add_column("ID", style="cyan")
            table.add_column("Title", style="bold")
            table.add_column("Type", style="dim")
            table.add_column("Due Date", style="yellow")
            table.add_column("Points", style="green")

            for cw in coursework:
                due = cw.due_date or "No due date"
                if cw.due_time:
                    due += f" {cw.due_time}"
                points = str(cw.max_points) if cw.max_points else "-"

                table.add_row(
                    cw.id,
                    cw.title[:40] + ("..." if len(cw.title) > 40 else ""),
                    cw.work_type.replace("_", " ").title(),
                    due,
                    points,
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="List coursework for a course")
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
    list_coursework(course_id=args.course_id, output_format=args.format)


if __name__ == "__main__":
    main()
