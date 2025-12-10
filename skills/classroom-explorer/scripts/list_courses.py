#!/usr/bin/env python3
"""
List Google Classroom courses.

Usage:
    python list_courses.py
    python list_courses.py --state ACTIVE
    python list_courses.py --format json
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


def list_courses(state: str = None, output_format: str = "table"):
    """List all accessible courses."""
    try:
        client = ClassroomClient()

        if not client.is_authenticated():
            console.print("[red]Not authenticated. Run 'python auth.py --setup' first.[/red]")
            sys.exit(1)

        courses = client.list_courses(state=state)

        if not courses:
            console.print("[yellow]No courses found.[/yellow]")
            return

        if output_format == "json":
            output = {
                "count": len(courses),
                "courses": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "section": c.section,
                        "state": c.state,
                        "alternate_link": c.alternate_link,
                    }
                    for c in courses
                ],
            }
            print(json.dumps(output, indent=2))
        else:
            # Table format
            table = Table(title=f"Google Classroom Courses ({len(courses)})")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="bold")
            table.add_column("Section", style="dim")
            table.add_column("State", style="green")

            for course in courses:
                table.add_row(
                    course.id,
                    course.name,
                    course.section or "",
                    course.state,
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="List Google Classroom courses")
    parser.add_argument(
        "--state",
        choices=["ACTIVE", "ARCHIVED", "PROVISIONED", "DECLINED", "SUSPENDED"],
        help="Filter by course state",
    )
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )

    args = parser.parse_args()
    list_courses(state=args.state, output_format=args.format)


if __name__ == "__main__":
    main()
