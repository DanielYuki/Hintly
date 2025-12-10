#!/usr/bin/env python3
"""
Format a solution as LaTeX from JSON input.

Usage:
    python format_solution.py --input solution.json --output solution.tex
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from rich.console import Console
from rich.panel import Panel

from core.latex_solver import LaTeXSolver
from core.classroom_api import CourseWork, Course


console = Console()


def format_solution(input_path: str, output_path: str):
    """Format a JSON solution as LaTeX."""
    try:
        # Load JSON
        with open(input_path, "r") as f:
            data = json.load(f)

        # Create mock objects from JSON
        course = Course(
            id=data.get("course", {}).get("id", ""),
            name=data.get("course", {}).get("name", "Unknown Course"),
            section=data.get("course", {}).get("section"),
        )

        activity_data = data.get("activity", {})
        activity = CourseWork(
            id=activity_data.get("id", ""),
            course_id=course.id,
            title=activity_data.get("title", "Unknown Activity"),
            work_type=activity_data.get("type", "ASSIGNMENT"),
            description=activity_data.get("description"),
        )

        # Get solution content
        problem_statement = data.get("problem_statement", "")
        solution_steps = data.get("solution_steps", [])
        final_answer = data.get("final_answer", "")
        explanation = data.get("explanation", "")

        # Generate LaTeX
        solver = LaTeXSolver()
        tex_path = solver.generate_solution(
            coursework=activity,
            course=course,
            problem_statement=problem_statement,
            solution_steps=solution_steps,
            final_answer=final_answer,
            explanation=explanation,
            output_path=Path(output_path),
        )

        console.print(Panel(
            f"[green]✓ LaTeX file generated![/green]\n\nOutput: {tex_path}",
            title="Success",
            border_style="green",
        ))

        return tex_path

    except FileNotFoundError:
        console.print(f"[red]Error: Input file not found: {input_path}[/red]")
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Format solution as LaTeX")
    parser.add_argument(
        "--input",
        required=True,
        help="Input JSON file with solution data",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output LaTeX file path",
    )

    args = parser.parse_args()
    format_solution(input_path=args.input, output_path=args.output)


if __name__ == "__main__":
    main()
