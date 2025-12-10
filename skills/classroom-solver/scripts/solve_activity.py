#!/usr/bin/env python3
"""
Solve a Google Classroom activity and generate LaTeX solution.

Usage:
    python solve_activity.py --course-id <ID> --activity-id <ID>
    python solve_activity.py --course-id <ID> --activity-id <ID> --compile-pdf
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from rich.console import Console
from rich.panel import Panel

from core.classroom_api import ClassroomClient
from core.latex_solver import LaTeXSolver


console = Console()


def solve_activity(
    course_id: str,
    activity_id: str,
    include_steps: bool = True,
    compile_pdf: bool = False,
    output_path: str = None,
):
    """Solve an activity and generate LaTeX solution."""
    try:
        client = ClassroomClient()

        if not client.is_authenticated():
            console.print("[red]Not authenticated. Run 'python auth.py --setup' first.[/red]")
            sys.exit(1)

        console.print("[bold]Fetching activity...[/bold]")

        course = client.get_course(course_id)
        activity = client.get_coursework(course_id, activity_id)

        console.print(f"Activity: [cyan]{activity.title}[/cyan]")
        console.print(f"Course: [green]{course.name}[/green]\n")

        # Generate problem statement from activity
        problem_statement = activity.description or "No problem description provided."

        # In a real implementation, this would analyze the problem and generate actual solutions
        # For now, we generate a template/example solution
        console.print("[bold]Generating solution...[/bold]\n")

        # Determine problem type for solution structure
        work_type = activity.work_type
        solution_steps = []
        final_answer = ""
        explanation = ""

        if work_type == "MULTIPLE_CHOICE_QUESTION":
            explanation = "This is a multiple choice question. We analyze each option to find the correct answer."
            solution_steps = [
                {
                    "title": "Analyze the Question",
                    "content": "We need to carefully read and understand what is being asked.",
                },
                {
                    "title": "Evaluate Each Option",
                    "content": "Let's examine each choice:\n\\begin{itemize}\n\\item Option A: [Analysis]\n\\item Option B: [Analysis]\n\\item Option C: [Analysis]\n\\item Option D: [Analysis]\n\\end{itemize}",
                },
                {
                    "title": "Determine Correct Answer",
                    "content": "Based on our analysis, the correct answer is determined by [reasoning].",
                },
            ]
            final_answer = "\\text{[Selected Option]}"

        elif work_type == "SHORT_ANSWER_QUESTION":
            explanation = "This is a short answer question requiring a concise, accurate response."
            solution_steps = [
                {
                    "title": "Understand the Question",
                    "content": "The question asks us to [identify key requirements].",
                },
                {
                    "title": "Formulate Response",
                    "content": "[Develop the answer with clear reasoning]",
                },
            ]
            final_answer = "\\text{[Your answer here]}"

        else:  # ASSIGNMENT
            # Check for math-related content
            desc_lower = (activity.description or "").lower()
            title_lower = activity.title.lower()

            if any(kw in desc_lower or kw in title_lower for kw in ["math", "equation", "solve", "calcul"]):
                explanation = "This is a mathematical problem. We'll solve it step by step."
                solution_steps = [
                    {
                        "title": "Identify Given Information",
                        "content": "From the problem, we are given:\n\\begin{align*}\n& \\text{[List given values]}\n\\end{align*}",
                    },
                    {
                        "title": "Set Up the Equation",
                        "content": "We can express this as:\n\\begin{equation}\n[\\text{equation here}]\n\\end{equation}",
                    },
                    {
                        "title": "Solve",
                        "content": "Solving step by step:\n\\begin{align*}\n& \\text{Step 1}: \\\\\n& \\text{Step 2}: \\\\\n& \\text{Step 3}:\n\\end{align*}",
                    },
                    {
                        "title": "Verify",
                        "content": "We can verify by substituting back into the original equation.",
                    },
                ]
                final_answer = "x = [\\text{value}]"
            else:
                explanation = "We'll work through this assignment systematically."
                solution_steps = [
                    {
                        "title": "Understand Requirements",
                        "content": "The assignment requires us to [identify tasks].",
                    },
                    {
                        "title": "Develop Solution",
                        "content": "[Work through the problem]",
                    },
                    {
                        "title": "Review and Finalize",
                        "content": "[Check work and prepare final answer]",
                    },
                ]
                final_answer = "\\text{[Complete solution]}"

        # Generate LaTeX
        solver = LaTeXSolver()
        tex_path = solver.generate_solution(
            coursework=activity,
            course=course,
            problem_statement=problem_statement,
            solution_steps=solution_steps,
            final_answer=final_answer,
            explanation=explanation,
            output_path=Path(output_path) if output_path else None,
        )

        console.print(Panel(
            f"[green]✓ Solution generated![/green]\n\n"
            f"LaTeX file: {tex_path}",
            title="Success",
            border_style="green",
        ))

        # Compile to PDF if requested
        if compile_pdf:
            console.print("\n[bold]Compiling to PDF...[/bold]")
            pdf_path = solver.compile_to_pdf(tex_path)
            if pdf_path:
                console.print(f"[green]PDF created: {pdf_path}[/green]")
            else:
                console.print("[yellow]PDF compilation failed. Is pdflatex installed?[/yellow]")

        return tex_path

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Solve a Google Classroom activity")
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
        "--include-steps",
        action="store_true",
        default=True,
        help="Include step-by-step solution",
    )
    parser.add_argument(
        "--compile-pdf",
        action="store_true",
        help="Compile LaTeX to PDF",
    )
    parser.add_argument(
        "--output",
        help="Custom output path",
    )

    args = parser.parse_args()
    solve_activity(
        course_id=args.course_id,
        activity_id=args.activity_id,
        include_steps=args.include_steps,
        compile_pdf=args.compile_pdf,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
