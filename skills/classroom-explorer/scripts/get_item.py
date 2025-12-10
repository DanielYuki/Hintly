#!/usr/bin/env python3
"""
Get specific item details from Google Classroom.

Usage:
    python get_item.py --course-id <ID> --item-id <ID> --type coursework
    python get_item.py --course-id <ID> --item-id <ID> --type material
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from core.classroom_api import ClassroomClient
from core.config import get_config


console = Console()


def get_coursework(client: ClassroomClient, course_id: str, item_id: str, output_format: str):
    """Get coursework details."""
    course = client.get_course(course_id)
    cw = client.get_coursework(course_id, item_id)

    if output_format == "json":
        output = {
            "course": {"id": course.id, "name": course.name},
            "coursework": {
                "id": cw.id,
                "title": cw.title,
                "type": cw.work_type,
                "description": cw.description,
                "max_points": cw.max_points,
                "due_date": cw.due_date,
                "due_time": cw.due_time,
                "state": cw.state,
                "creation_time": cw.creation_time,
                "materials": [
                    {"type": m.type, "title": m.title, "url": m.url}
                    for m in cw.materials
                ],
                "alternate_link": cw.alternate_link,
            },
        }
        print(json.dumps(output, indent=2))
    else:
        # Rich formatted output
        content = []
        content.append(f"**Course**: {course.name}")
        content.append(f"**Type**: {cw.work_type.replace('_', ' ').title()}")

        if cw.max_points:
            content.append(f"**Points**: {cw.max_points}")

        if cw.due_date:
            due = cw.due_date
            if cw.due_time:
                due += f" at {cw.due_time}"
            content.append(f"**Due**: {due}")

        if cw.description:
            content.append(f"\n**Description**:\n{cw.description}")

        if cw.materials:
            content.append("\n**Attached Materials**:")
            for mat in cw.materials:
                mat_type = mat.type.replace("_", " ").title()
                content.append(f"  • {mat_type}: {mat.title or 'Untitled'}")
                if mat.url:
                    content.append(f"    URL: {mat.url}")

        if cw.alternate_link:
            content.append(f"\n**Classroom Link**: {cw.alternate_link}")

        console.print(Panel(
            Markdown("\n".join(content)),
            title=f"[bold]{cw.title}[/bold]",
            border_style="blue",
        ))


def get_material(client: ClassroomClient, course_id: str, item_id: str, output_format: str):
    """Get material details."""
    course = client.get_course(course_id)
    mat = client.get_material(course_id, item_id)

    if output_format == "json":
        output = {
            "course": {"id": course.id, "name": course.name},
            "material": {
                "id": mat.id,
                "title": mat.title,
                "description": mat.description,
                "state": mat.state,
                "creation_time": mat.creation_time,
                "attachments": [
                    {"type": m.type, "title": m.title, "url": m.url}
                    for m in mat.materials
                ],
                "alternate_link": mat.alternate_link,
            },
        }
        print(json.dumps(output, indent=2))
    else:
        # Rich formatted output
        content = []
        content.append(f"**Course**: {course.name}")
        content.append(f"**State**: {mat.state}")

        if mat.creation_time:
            content.append(f"**Created**: {mat.creation_time[:10]}")

        if mat.description:
            content.append(f"\n**Description**:\n{mat.description}")

        if mat.materials:
            content.append("\n**Attached Resources**:")
            for m in mat.materials:
                m_type = m.type.replace("_", " ").title()
                content.append(f"  • {m_type}: {m.title or 'Untitled'}")
                if m.url:
                    content.append(f"    URL: {m.url}")

        if mat.alternate_link:
            content.append(f"\n**Classroom Link**: {mat.alternate_link}")

        console.print(Panel(
            Markdown("\n".join(content)),
            title=f"[bold]{mat.title}[/bold]",
            border_style="green",
        ))


def main():
    parser = argparse.ArgumentParser(description="Get specific item from Google Classroom")
    parser.add_argument(
        "--course-id",
        required=True,
        help="Course ID",
    )
    parser.add_argument(
        "--item-id",
        required=True,
        help="Item ID (coursework or material)",
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["coursework", "material"],
        help="Type of item to retrieve",
    )
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )

    args = parser.parse_args()

    try:
        client = ClassroomClient()

        if not client.is_authenticated():
            console.print("[red]Not authenticated. Run 'python auth.py --setup' first.[/red]")
            sys.exit(1)

        if args.type == "coursework":
            get_coursework(client, args.course_id, args.item_id, args.format)
        else:
            get_material(client, args.course_id, args.item_id, args.format)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
