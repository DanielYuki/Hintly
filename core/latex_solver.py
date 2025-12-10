"""
LaTeX solution generation.

Creates LaTeX documents for step-by-step solutions to activities.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional
import subprocess
import shutil

from core.config import Config, get_config
from core.classroom_api import CourseWork, Course


class LaTeXSolver:
    """
    Generates LaTeX solution documents for coursework.

    Creates professional LaTeX files with step-by-step solutions.
    """

    # Base LaTeX template
    TEMPLATE = r"""
\documentclass[12pt, a4paper]{article}

% Packages
\usepackage{amsmath, amssymb, amsthm}
\usepackage{geometry}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{hyperref}
\usepackage{xcolor}

% Page setup
\geometry{margin=1in}
\pagestyle{fancy}
\fancyhf{}
\rhead{Hintly Solution}
\lhead{<<COURSE>>}
\rfoot{Page \thepage}

% Colors
\definecolor{problemcolor}{RGB}{26, 26, 46}
\definecolor{solutioncolor}{RGB}{22, 33, 62}

% Custom environments
\newenvironment{problem}[1]{
    \noindent\textbf{\color{problemcolor}Problem: #1}
    \vspace{0.5em}
    
    \noindent
}{
    \vspace{1em}
}

\newenvironment{solution}{
    \noindent\textbf{\color{solutioncolor}Solution:}
    \vspace{0.5em}
    
    \noindent
}{
    \vspace{1em}
}

\begin{document}

% Title
\begin{center}
    {\Large\textbf{<<TITLE>>}}\\[0.5em]
    {\normalsize <<COURSE>> <<SECTION>>}\\[0.3em]
    {\small Generated: <<DATE>>}
\end{center}

\vspace{1em}

<<CONTENT>>

\end{document}
"""

    STEP_TEMPLATE = r"""
\subsection*{Step <<NUM>>: <<TITLE>>}
<<CONTENT>>
"""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize LaTeX solver.

        Args:
            config: Configuration instance
        """
        self.config = config or get_config()

    def generate_solution(
        self,
        coursework: CourseWork,
        course: Course,
        problem_statement: str,
        solution_steps: list[dict],
        final_answer: str,
        explanation: str = "",
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate a LaTeX solution document.

        Args:
            coursework: The CourseWork being solved
            course: The parent Course
            problem_statement: The problem text
            solution_steps: List of dicts with 'title' and 'content'
            final_answer: The final answer
            explanation: Optional explanation of the approach
            output_path: Optional custom output path

        Returns:
            Path to generated .tex file
        """
        if output_path is None:
            safe_title = "".join(
                c if c.isalnum() or c in " -_" else "_"
                for c in coursework.title
            )[:50]
            filename = f"solution_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tex"
            output_path = self.config.solutions_dir / filename

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build content
        content_parts = []

        # Problem statement
        content_parts.append(r"\begin{problem}{" + self._escape_latex(coursework.title) + "}")
        content_parts.append(self._escape_latex(problem_statement))
        content_parts.append(r"\end{problem}")

        # Explanation (if provided)
        if explanation:
            content_parts.append(r"\subsection*{Approach}")
            content_parts.append(self._escape_latex(explanation))
            content_parts.append("")

        # Solution steps
        content_parts.append(r"\begin{solution}")
        for i, step in enumerate(solution_steps, 1):
            step_content = self.STEP_TEMPLATE.replace("<<NUM>>", str(i))
            step_content = step_content.replace("<<TITLE>>", self._escape_latex(step.get("title", "")))
            step_content = step_content.replace("<<CONTENT>>", step.get("content", ""))  # Allow raw LaTeX
            content_parts.append(step_content)

        # Final answer
        content_parts.append(r"\subsection*{Final Answer}")
        content_parts.append(r"\begin{center}")
        content_parts.append(r"\boxed{" + final_answer + "}")  # Allow raw LaTeX
        content_parts.append(r"\end{center}")
        content_parts.append(r"\end{solution}")

        # Build document
        content = "\n".join(content_parts)

        document = self.TEMPLATE
        document = document.replace("<<TITLE>>", self._escape_latex(coursework.title))
        document = document.replace("<<COURSE>>", self._escape_latex(course.name))
        document = document.replace("<<SECTION>>", self._escape_latex(course.section or ""))
        document = document.replace("<<DATE>>", datetime.now().strftime("%Y-%m-%d"))
        document = document.replace("<<CONTENT>>", content)

        # Write file
        output_path.write_text(document)

        return output_path

    def generate_empty_solution(
        self,
        coursework: CourseWork,
        course: Course,
        problem_statement: str,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate a solution template without steps filled in.

        Useful for manual solving or review.

        Args:
            coursework: The CourseWork
            course: The parent Course
            problem_statement: The problem text
            output_path: Optional custom output path

        Returns:
            Path to generated .tex file
        """
        return self.generate_solution(
            coursework=coursework,
            course=course,
            problem_statement=problem_statement,
            solution_steps=[
                {"title": "Identify Given Information", "content": "% Add your analysis here"},
                {"title": "Apply Method/Formula", "content": "% Add your work here"},
                {"title": "Calculate Result", "content": "% Add calculations here"},
            ],
            final_answer="\\text{Your answer here}",
            explanation="",
            output_path=output_path,
        )

    def compile_to_pdf(self, tex_path: Path) -> Optional[Path]:
        """
        Compile a .tex file to PDF using pdflatex.

        Requires pdflatex to be installed.

        Args:
            tex_path: Path to the .tex file

        Returns:
            Path to generated PDF, or None if compilation failed
        """
        # Check if pdflatex is available
        if not shutil.which("pdflatex"):
            print("pdflatex not found. Cannot compile to PDF.")
            return None

        try:
            # Run pdflatex twice for proper references
            for _ in range(2):
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", tex_path.name],
                    cwd=tex_path.parent,
                    capture_output=True,
                    text=True,
                )

            pdf_path = tex_path.with_suffix(".pdf")
            if pdf_path.exists():
                # Clean up auxiliary files
                for ext in [".aux", ".log", ".out"]:
                    aux_file = tex_path.with_suffix(ext)
                    if aux_file.exists():
                        aux_file.unlink()
                return pdf_path
            else:
                print(f"PDF compilation failed: {result.stderr}")
                return None

        except Exception as e:
            print(f"Error compiling PDF: {e}")
            return None

    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters."""
        if not text:
            return ""

        # Characters that need escaping
        replacements = [
            ("\\", r"\textbackslash{}"),
            ("&", r"\&"),
            ("%", r"\%"),
            ("$", r"\$"),
            ("#", r"\#"),
            ("_", r"\_"),
            ("{", r"\{"),
            ("}", r"\}"),
            ("~", r"\textasciitilde{}"),
            ("^", r"\textasciicircum{}"),
        ]

        for old, new in replacements:
            text = text.replace(old, new)

        return text
