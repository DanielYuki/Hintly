# LaTeX Templates

Templates for generating solutions in classroom-solver.

## Base Document Template

```latex
\documentclass[12pt, a4paper]{article}

\usepackage{amsmath, amssymb, amsthm}
\usepackage{geometry}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{hyperref}
\usepackage{xcolor}

\geometry{margin=1in}
\pagestyle{fancy}

\begin{document}
% Content here
\end{document}
```

## Problem Environment

```latex
\begin{problem}{Title Here}
Problem statement text...
\end{problem}
```

## Solution Environment

```latex
\begin{solution}
\subsection*{Step 1: Title}
Content...

\subsection*{Step 2: Title}
Content...
\end{solution}
```

## Math Formatting

### Inline Math

```latex
The answer is $x = 5$.
```

### Display Math

```latex
\begin{equation}
f(x) = x^2 + 2x + 1
\end{equation}
```

### Aligned Equations

```latex
\begin{align*}
x + 2 &= 5 \\
x &= 5 - 2 \\
x &= 3
\end{align*}
```

## Final Answer Box

```latex
\boxed{x = 3}
```

## Common Symbols

| Symbol | LaTeX |
|--------|-------|
| ≤ | `\leq` |
| ≥ | `\geq` |
| ≠ | `\neq` |
| ∞ | `\infty` |
| ∑ | `\sum` |
| ∫ | `\int` |
| √ | `\sqrt{}` |
| π | `\pi` |
| θ | `\theta` |

## Fractions

```latex
\frac{numerator}{denominator}
```

## Greek Letters

| Letter | LaTeX |
|--------|-------|
| α | `\alpha` |
| β | `\beta` |
| γ | `\gamma` |
| δ | `\delta` |
| ε | `\epsilon` |
| λ | `\lambda` |
| μ | `\mu` |
| σ | `\sigma` |
| φ | `\phi` |
| ω | `\omega` |
