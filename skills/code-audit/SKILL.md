---
name: code-audit
description: Audit student code submissions for correctness, style, and reproducibility. Only invoke when code files are detected in the submission.
---

# Code Audit Skill

## When to Use

This skill is invoked **only when code files are detected** in the submission:
- Python files (`.py`)
- R files (`.R`, `.Rmd`)
- Stata files (`.do`)
- Excel files with formulas (`.xlsx` containing non-trivial formulas)
- Jupyter notebooks (`.ipynb`)

If no code files are present, skip this skill entirely.

---

## Code Audit Checklists

Run through these checklists when evaluating student code. Check items silently—they guide your evaluation but don't appear in output.

### Correctness Checklist
- [ ] **Logic errors**: Does the code do what the comments/documentation claim?
- [ ] **Edge cases**: Are boundary conditions handled (empty data, missing values, zeros)?
- [ ] **Output verification**: Do outputs match what the student claims in their writeup?
- [ ] **Calculation accuracy**: Are formulas and computations correct?

### Data Handling Checklist
- [ ] **Missing values**: How are NAs/missing values treated? Is this documented?
- [ ] **Data types**: Are variables the expected type (numeric vs. string, dates, etc.)?
- [ ] **Filtering**: Do subset/filter conditions correctly implement stated restrictions?
- [ ] **Merges/joins**: If data is combined, are there checks for expected results?

### Reproducibility Checklist
- [ ] **Relative paths**: Are file paths relative to the project, not absolute (`C:\Users\...` or `/Users/...`)?
- [ ] **Seeds set**: Are random seeds set for any stochastic procedures?
- [ ] **Dependencies**: Are required packages/libraries documented or loaded at the top?
- [ ] **Self-contained**: Can someone else run this code without your machine's setup?

### Style & Clarity Checklist
- [ ] **Variable names**: Are names informative (`total_revenue` not `x1`)?
- [ ] **Comments**: Is complex logic explained? (But not over-commented with obvious statements)
- [ ] **Organization**: Is the code structured logically (data loading → cleaning → analysis → output)?
- [ ] **Readability**: Is the code reasonably formatted and easy to follow?

*Adapted from the Code Audit and Replication Package Audit in Scott Cunningham's Referee 2 protocol.*

---

## Evaluation Approach

### What to Look For

**Correctness over style:** Prioritize whether the code produces correct results. Style issues matter less than logic errors.

**Match claims to code:** Verify that what the student claims in their writeup matches what the code actually does. Discrepancies are major concerns.

**Reproducibility matters:** Code that only runs on the student's machine isn't useful. Flag absolute paths, missing dependencies, and undocumented requirements.

### Severity Guidelines

**Major Concerns:**
- Code produces incorrect results
- Output doesn't match writeup claims
- Critical logic error that changes conclusions
- Code cannot run due to missing files or dependencies

**Minor Concerns:**
- Missing value handling not documented
- Variable names unclear but code is correct
- Minor inefficiencies that don't affect results
- Missing comments on complex logic

**Suggestions:**
- Style improvements that would help readability
- Better organization patterns
- More robust error handling

---

## Output Format

Add a "Code Review" section to the grading feedback:

```markdown
## Code Review

### What Works Well
[Specific strengths in the code—good practices, clear logic, proper handling of edge cases, well-organized structure]

### Issues Found

**[Issue 1 - e.g., "Missing Value Handling Undocumented"]**
- **Location:** `analysis.py`, lines 23-25 (or `Sheet1!B2:B50` for Excel)
- **Problem:** Missing values are silently dropped without documentation
- **Why it matters:** Reader can't verify if sample size changes are intentional or a bug
- **Suggested fix:** Add a comment explaining the handling, or print the count of dropped rows

**[Issue 2 - e.g., "Absolute Path Will Break on Other Machines"]**
- **Location:** `data_load.R`, line 5
- **Problem:** `read.csv("C:/Users/student/Desktop/data.csv")` uses an absolute path
- **Why it matters:** This code will fail on any other computer
- **Suggested fix:** Use a relative path like `read.csv("data/data.csv")` and include the data file

### Reproducibility Assessment

| Criterion | Status | Notes |
|-----------|--------|-------|
| Relative paths | ✓ / ✗ | [Brief note if needed] |
| Seeds set (if applicable) | ✓ / ✗ / N/A | [Brief note if needed] |
| Dependencies documented | ✓ / ✗ | [Brief note if needed] |
| Runs without modification | ✓ / ✗ | [Brief note if needed] |

**Reproducibility Score:** X/4 criteria met
```

---

## Excel-Specific Guidance

For Excel submissions with formulas:

### What to Check
- **Formula correctness**: Do formulas calculate what they claim?
- **Cell references**: Are references correct (absolute vs. relative, correct ranges)?
- **Error handling**: Are there `#REF!`, `#VALUE!`, `#DIV/0!` or other errors?
- **Hard-coded values**: Are numbers that should be cell references hard-coded instead?
- **Named ranges**: Are complex formulas using named ranges for clarity?

### Common Issues
- SUM/AVERAGE ranges that don't include all data
- VLOOKUP with incorrect match type (exact vs. approximate)
- Circular references
- Formulas that reference deleted cells
- Mixed absolute/relative references that break when copied

### Location Format for Excel
Use `SheetName!CellRange` format:
- "In `Analysis!D15`, the VLOOKUP..."
- "The SUM formula in `Summary!B20:B25` excludes..."

---

## Notes

- **Don't rewrite the code:** Your job is to identify issues, not fix them. Point to problems and explain why they matter.
- **Be specific:** Vague feedback ("code could be cleaner") isn't helpful. Point to exact locations and explain the issue.
- **Connect to the writeup:** If the code produces results that appear in the paper, verify they match.
- **Acknowledge good practices:** If the student did something well (good variable names, proper error handling, clear organization), mention it briefly.
