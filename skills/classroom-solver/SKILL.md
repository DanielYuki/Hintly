---
name: classroom-solver
description: >
  Solves Google Classroom activities and assignments. Detects problem types
  (PDF, Google Forms, text questions) and generates step-by-step solutions
  in LaTeX format. Only solves when explicitly requested by the user.
  Use when the user asks to solve, complete, or work through an assignment.
  Triggers: "solve this assignment", "help me with this problem",
  "work through this activity", "complete this homework", "solve the questions".
---

# Classroom Solver

Solve Google Classroom activities and assignments with step-by-step LaTeX solutions.

## Important

> ⚠️ **Only solve activities when explicitly requested by the user.**
> If not asked to solve, use the **classroom-analyzer** skill to summarize instead.

## Capabilities

- Detect activity/assignment types
- Generate step-by-step solutions
- Format solutions in LaTeX with proper math notation
- Compile to PDF (if pdflatex is available)

## Commands

### Detect Activity Type

First, analyze what type of activity this is:

```bash
python {baseDir}/scripts/detect_activity.py --course-id <ID> --activity-id <ID>
```

Returns:

- Problem type (math, science, essay, etc.)
- Format (PDF attachment, Google Form, text)
- Solvability score (0-1)

### Solve Activity

Generate a solution for the activity:

```bash
python {baseDir}/scripts/solve_activity.py --course-id <ID> --activity-id <ID>
```

Options:

- `--include-steps` - Show step-by-step work (default: true)
- `--compile-pdf` - Compile to PDF after generating
- `--output <PATH>` - Custom output path

### Format Solution

Format raw solution data as LaTeX:

```bash
python {baseDir}/scripts/format_solution.py --input solution.json --output solution.tex
```

## Workflow

1. **User requests to solve an activity**
2. **Detect type**: Run `detect_activity.py` to understand the problem
3. **Solve**: Run `solve_activity.py` to generate solution
4. **Format**: Solution is saved as LaTeX (.tex file)
5. **Compile** (optional): If pdflatex available, compile to PDF

## Supported Problem Types

| Type | Support | Notes |
|------|---------|-------|
| Math (algebra, calculus) | ✅ Full | Step-by-step with formulas |
| Science (physics, chemistry) | ✅ Full | Includes units and diagrams |
| Multiple choice | ✅ Full | Explains correct answer |
| Short answer | ✅ Full | Concise with reasoning |
| Essays | ⚠️ Partial | Provides outline only |
| Coding | ⚠️ Partial | Algorithm guidance |

## Output Format

Solutions are LaTeX files with:

```latex
\documentclass{article}
\usepackage{amsmath, amssymb}

\begin{document}

\section*{Problem Statement}
[Original problem text]

\section*{Solution}
\subsection*{Step 1: ...}
...

\section*{Final Answer}
\boxed{...}

\end{document}
```

## Output Location

- LaTeX: `outputs/solutions/*.tex`
- PDF: `outputs/solutions/*.pdf` (if compiled)

## Error Handling

| Error | Solution |
|-------|----------|
| "Activity not solvable" | May be essay-type, provide outline instead |
| "PDF compilation failed" | Check pdflatex is installed |
| "Missing content" | Activity may not have attached problems |

## Reference

- [Problem Types Guide](file://reference/problem_types.md)
- [LaTeX Templates](file://reference/latex_templates.md)
