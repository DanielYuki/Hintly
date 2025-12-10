# Problem Types Guide

Reference documentation for handling different activity types in classroom-solver.

## Problem Categories

### 1. Mathematical Problems

**Identification Keywords**: math, algebra, calculus, equation, solve, derivative, integral

**Solution Structure**:

```latex
\subsection*{Step 1: Identify Given Information}
[List variables, constants, and relationships]

\subsection*{Step 2: Set Up the Equation}
\begin{equation}
[formulation]
\end{equation}

\subsection*{Step 3: Solve}
\begin{align*}
[step-by-step work]
\end{align*}

\subsection*{Step 4: Verify}
[Substitution check]
```

**LaTeX Packages**: amsmath, amssymb

---

### 2. Science Problems

**Identification Keywords**: physics, chemistry, biology, experiment, hypothesis

**Solution Structure**:

- State known quantities with units
- Identify the relevant formula/principle
- Show calculations with unit analysis
- State final answer with proper significant figures

**LaTeX Packages**: siunitx for units

---

### 3. Multiple Choice Questions

**Identification**: `work_type == "MULTIPLE_CHOICE_QUESTION"`

**Solution Structure**:

- Restate the question
- Analyze each option
- Eliminate incorrect choices
- Explain correct answer

**Solvability**: 0.95 (high)

---

### 4. Short Answer Questions

**Identification**: `work_type == "SHORT_ANSWER_QUESTION"`

**Solution Structure**:

- Understand requirements
- Provide concise answer
- Include brief justification

**Solvability**: 0.85

---

### 5. Essay/Writing Assignments

**Identification Keywords**: essay, write, paragraph, analysis, discuss

**Solution Structure**:

- Thesis statement outline
- Key points to cover
- Suggested structure
- NOT a complete essay (outline only)

**Solvability**: 0.3 (can only guide, not solve)

---

### 6. Coding Assignments

**Identification Keywords**: code, program, function, algorithm

**Solution Structure**:

- Problem breakdown
- Algorithm design
- Pseudocode
- Implementation hints

**Solvability**: 0.6 (guidance, not complete code)

---

## Solvability Scoring

| Score | Meaning |
|-------|---------|
| 0.9-1.0 | Fully solvable with step-by-step |
| 0.7-0.9 | Solvable with some assumptions |
| 0.5-0.7 | Partially solvable, guidance provided |
| 0.3-0.5 | Outline/structure only |
| 0.0-0.3 | Not suitable for automated solving |
