#!/usr/bin/env python3
"""
Detect the type of a Google Classroom activity.

Usage:
    python detect_activity.py --course-id <ID> --activity-id <ID>
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.classroom_api import ClassroomClient


console = Console()


def detect_activity(course_id: str, activity_id: str, output_format: str = "table"):
    """Detect and analyze an activity's type and solvability."""
    try:
        client = ClassroomClient()

        if not client.is_authenticated():
            console.print("[red]Not authenticated. Run 'python auth.py --setup' first.[/red]")
            sys.exit(1)

        console.print("[bold]Analyzing activity...[/bold]")

        course = client.get_course(course_id)
        activity = client.get_coursework(course_id, activity_id)

        # Analyze the activity
        analysis = analyze_activity_type(activity)

        if output_format == "json":
            output = {
                "course": {"id": course.id, "name": course.name},
                "activity": {
                    "id": activity.id,
                    "title": activity.title,
                    "work_type": activity.work_type,
                },
                "analysis": analysis,
            }
            print(json.dumps(output, indent=2))
        else:
            # Display analysis
            console.print(f"\nActivity: [bold]{activity.title}[/bold]")
            console.print(f"Course: [cyan]{course.name}[/cyan]\n")

            table = Table(title="Activity Analysis")
            table.add_column("Property", style="bold")
            table.add_column("Value")

            table.add_row("Work Type", activity.work_type.replace("_", " ").title())
            table.add_row("Problem Type", analysis["problem_type"])
            table.add_row("Format", analysis["format"])
            table.add_row("Solvability", f"{analysis['solvability']:.0%}")
            table.add_row("Has Attachments", "Yes" if analysis["has_attachments"] else "No")

            if analysis["attachment_types"]:
                table.add_row("Attachment Types", ", ".join(analysis["attachment_types"]))

            console.print(table)

            # Recommendation
            if analysis["solvability"] >= 0.7:
                console.print(Panel(
                    "[green]This activity appears solvable.[/green]\n"
                    "Run solve_activity.py to generate a solution.",
                    title="Recommendation",
                    border_style="green",
                ))
            elif analysis["solvability"] >= 0.4:
                console.print(Panel(
                    "[yellow]This activity may be partially solvable.[/yellow]\n"
                    "An outline or guidance can be provided.",
                    title="Recommendation",
                    border_style="yellow",
                ))
            else:
                console.print(Panel(
                    "[dim]This activity type is not well suited for automated solving.[/dim]\n"
                    "Consider using classroom-analyzer for a summary instead.",
                    title="Recommendation",
                    border_style="dim",
                ))

        return analysis

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def analyze_activity_type(activity) -> dict:
    """Analyze the activity and determine its type and solvability."""
    analysis = {
        "problem_type": "unknown",
        "format": "text",
        "solvability": 0.5,
        "has_attachments": len(activity.materials) > 0,
        "attachment_types": [],
    }

    # Determine attachment types
    for mat in activity.materials:
        if mat.type not in analysis["attachment_types"]:
            analysis["attachment_types"].append(mat.type)

    # Determine format based on attachments
    if any(m.type == "form" for m in activity.materials):
        analysis["format"] = "Google Form"
        analysis["solvability"] = 0.8
    elif any(m.type == "driveFile" for m in activity.materials):
        # Check file types
        for mat in activity.materials:
            if mat.title:
                if mat.title.lower().endswith(".pdf"):
                    analysis["format"] = "PDF"
                    analysis["solvability"] = 0.7
                elif mat.title.lower().endswith((".doc", ".docx")):
                    analysis["format"] = "Document"
                    analysis["solvability"] = 0.6
    else:
        analysis["format"] = "text"
        analysis["solvability"] = 0.9

    # Determine problem type based on work type and description
    work_type = activity.work_type

    if work_type == "SHORT_ANSWER_QUESTION":
        analysis["problem_type"] = "short_answer"
        analysis["solvability"] = 0.85
    elif work_type == "MULTIPLE_CHOICE_QUESTION":
        analysis["problem_type"] = "multiple_choice"
        analysis["solvability"] = 0.95
    elif work_type == "ASSIGNMENT":
        # Try to infer from description
        desc = (activity.description or "").lower()
        title = activity.title.lower()

        if any(kw in desc or kw in title for kw in ["math", "algebra", "calcul", "equation", "solve"]):
            analysis["problem_type"] = "math"
            analysis["solvability"] = 0.9
        elif any(kw in desc or kw in title for kw in ["physics", "chemistry", "science", "experiment"]):
            analysis["problem_type"] = "science"
            analysis["solvability"] = 0.8
        elif any(kw in desc or kw in title for kw in ["essay", "write", "paragraph", "analysis"]):
            analysis["problem_type"] = "essay"
            analysis["solvability"] = 0.3  # Can only provide outline
        elif any(kw in desc or kw in title for kw in ["code", "program", "function", "algorithm"]):
            analysis["problem_type"] = "coding"
            analysis["solvability"] = 0.6
        else:
            analysis["problem_type"] = "general"
            analysis["solvability"] = 0.5

    return analysis


def main():
    parser = argparse.ArgumentParser(description="Detect activity type")
    parser.add_argument(
        "--course-id",
        required=True,
        help="Course ID",
    )
    parser.add_argument(
        "--activity-id",
        required=True,
        help="Activity/coursework ID",
    )
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format",
    )

    args = parser.parse_args()
    detect_activity(
        course_id=args.course_id,
        activity_id=args.activity_id,
        output_format=args.format,
    )


if __name__ == "__main__":
    main()
