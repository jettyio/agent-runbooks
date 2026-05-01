---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/anthropics/skills/pptx"
  source_host: "skills.sh"
  source_title: "PPTX Skill"
  imported_at: "2026-05-01T03:50:07Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "anthropics"
    skill_name: "pptx"
    confidence: "high"
secrets: {}
---

# PPTX Skill — Agent Runbook

## Objective

Use this skill any time a `.pptx` file is involved in any way — as input, output, or both. This includes creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any `.pptx` file; editing, modifying, or updating existing presentations; combining or splitting slide files; and working with templates, layouts, speaker notes, or comments. This runbook provides structured workflows for reading content, editing via template unpacking, creating from scratch using PptxGenJS, applying design guidance, and running mandatory QA checks.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/output.pptx` | The generated or modified PowerPoint file (when creating/editing) |
| `/app/results/thumbnails.jpg` | JPEG thumbnails of all slides for visual QA |
| `/app/results/extracted_text.md` | Extracted text content from the PPTX (when reading/parsing) |
| `/app/results/qa_report.md` | QA verification results from the mandatory QA process |
| `/app/results/summary.md` | Executive summary of the task performed and QA outcome |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Input PPTX | *(optional)* | Path to an existing `.pptx` file to read or edit |
| Output PPTX | `/app/results/output.pptx` | Path for the generated or modified presentation |
| Workflow | `create` | One of: `read`, `edit`, `create` |
| Theme | *(optional)* | Color palette name from the curated list below |
| Max QA rounds | `3` | Maximum number of max 3 round QA iteration cycles before aborting |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `python-pptx` | Python package | Yes | Create and manipulate PPTX files programmatically |
| `pptxgenjs` | npm package | Yes (create workflow) | JavaScript library for generating presentations |
| `markitdown` | Python package | Yes (read workflow) | Extract text from PPTX files |
| `LibreOffice` (`soffice`) | System CLI | Yes (thumbnails) | Convert PPTX to PDF for thumbnail generation |
| `pdftoppm` | System CLI | Yes (thumbnails) | Convert PDF pages to JPEG images |
| `pillow` | Python package | Optional | Image processing for thumbnail collation |

## Step 1: Environment Setup

```bash
# Install Python dependencies
pip install python-pptx markitdown pillow

# Install Node.js dependencies (for create workflow)
npm install pptxgenjs

# Verify system dependencies
command -v soffice >/dev/null || echo "WARNING: LibreOffice not found — thumbnail generation will fail"
command -v pdftoppm >/dev/null || echo "WARNING: pdftoppm not found — thumbnail generation will fail"

# Create output directory
mkdir -p /app/results
```

Verify that the workflow parameter is one of `read`, `edit`, or `create` before proceeding.

## Step 2: Read / Extract Content

*Run this step when `workflow=read` or when you need to inspect an existing PPTX before editing.*

```bash
# Text extraction
python -m markitdown "$INPUT_PPTX" > /app/results/extracted_text.md

# Visual overview
python scripts/thumbnail.py "$INPUT_PPTX"

# Raw XML (for advanced inspection)
python scripts/office/unpack.py "$INPUT_PPTX" unpacked/
```

Review `thumbnails.jpg` to understand existing layouts. Review `extracted_text.md` to understand the slide content structure.

## Step 3: Edit Existing Presentation

*Run this step when `workflow=edit`.*

### Template-Based Workflow

When using an existing presentation as a template:

1. **Analyze existing slides**:
   ```bash
   python scripts/thumbnail.py template.pptx
   python -m markitdown template.pptx
   ```
   Review `thumbnails.jpg` to see layouts, and markitdown output to see placeholder names.

2. **Unpack the template**:
   ```bash
   python scripts/office/unpack.py template.pptx unpacked/
   ```

3. **Inspect slide XML** to understand structure before editing:
   ```bash
   ls unpacked/ppt/slides/
   cat unpacked/ppt/slides/slide1.xml
   ```

4. **Make targeted edits** using `python-pptx` to modify text, images, or layouts.

5. **Verify edits** by generating thumbnails:
   ```bash
   python scripts/thumbnail.py output.pptx
   python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
   ```

## Step 4: Create from Scratch with PptxGenJS

*Run this step when `workflow=create`.*

```javascript
const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'Agent';
pres.title = 'Presentation Title';

// Add slides
let slide = pres.addSlide();
slide.addText("Title Text", {
    x: 0.5, y: 0.5, w: "90%", h: 1.5,
    fontSize: 36, bold: true, color: "363636"
});

// Save
pres.writeFile({ fileName: "/app/results/output.pptx" });
```

For complex layouts, create one slide per section with structured content before moving on.

## Step 5: Apply Design Guidance

### Before Starting

Do NOT start designing until you have reviewed this section. Avoid generic AI aesthetics.

### Color Palettes (use one consistently per deck)

Use one of these curated palettes — do not mix palettes between slides:

| Palette | Background | Text | Accent |
|---------|-----------|------|--------|
| Slate Professional | `#1E293B` | `#F8FAFC` | `#38BDF8` |
| Forest Executive | `#14532D` | `#F0FDF4` | `#86EFAC` |
| Terracotta Warm | `#7C2D12` | `#FFF7ED` | `#FB923C` |
| Ocean Depth | `#0C4A6E` | `#F0F9FF` | `#7DD3FC` |
| Graphite Clean | `#18181B` | `#FAFAFA` | `#A78BFA` |

### Typography

- Title: 36–44pt, Bold
- Subtitle/H2: 24–32pt, Semi-Bold
- Body: 18–22pt, Regular
- Caption: 14–16pt, Regular or Light
- Never use fewer than 3 font sizes per deck; never more than 3 typefaces

### Spacing

- Minimum 40px padding from slide edges
- Line height: 1.3–1.6x font size
- Consistent vertical rhythm across slides

### Layout Patterns

Prefer these proven layouts:
- **Two-column**: 45/55 or 40/60 split for text + visual
- **Icon rows**: 3–4 equally spaced icons with captions
- **Half-bleed image**: Full-height image on one side, text on the other
- **Grid**: 2×2 or 3×2 card grids for comparison slides

### Avoid (Common Mistakes)

- Drop shadows on text (use bold or color contrast instead)
- More than 3 bullet levels
- Inconsistent alignment (always left-align or center, not both)
- Low-contrast color combinations (ensure ≥4.5:1 contrast ratio)
- Generic clip art or stock icons that look AI-generated
- Centering body text (only center titles/headings)

## Step 6: Run QA (Required)

QA is mandatory for every PPTX task. Use subagents for visual inspection.

### Content QA

Check for placeholder artifacts:
```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout|placeholder|todo|tbd|sample"
```

Also verify:
- All slides have actual content (no empty slides unless intentional)
- Speaker notes added where useful
- File opens without errors in python-pptx

### Visual QA

```bash
# Generate thumbnails
python scripts/thumbnail.py output.pptx
```

Then use a subagent to inspect `thumbnails.jpg` and verify:
- [ ] No overlapping text or elements
- [ ] No text overflow beyond slide boundaries
- [ ] Consistent fonts, sizes, and colors across slides
- [ ] Color palette applied consistently
- [ ] Contrast ratios are adequate (light text on dark bg, or vice versa)
- [ ] No generic AI aesthetics (clip art, default Office themes)
- [ ] Layout patterns match the design guide (no random positioning)

### Verification Loop (max 3 rounds)

Iterate fixes until QA passes or 3 rounds are exhausted:

1. Review visual QA findings
2. Fix identified issues (overlaps, contrast, placeholder text)
3. Regenerate thumbnails and re-inspect
4. Repeat up to max 3 round limit

If issues remain after 3 rounds, document them in `qa_report.md` and proceed.

## Step 7: Convert to Images

For detailed inspection or delivery, convert slides to JPEG:

```bash
# Convert PPTX to PDF
soffice --headless --convert-to pdf output.pptx --outdir /app/results/

# Convert PDF pages to JPEG
pdftoppm -jpeg -r 150 /app/results/output.pdf /app/results/slide

# Combine into single contact sheet
python scripts/thumbnail.py output.pptx  # uses soffice + pdftoppm internally
```

Images will be saved as `/app/results/slide-000001.jpg`, etc.

## Step 8: Write QA Report

Write `/app/results/qa_report.md`:

```markdown
# PPTX QA Report

## Task Summary
- Workflow: <read|edit|create>
- Input: <path or "none">
- Output: /app/results/output.pptx

## Content QA
- Placeholder artifacts found: <yes/no, list if yes>
- Empty slides: <yes/no>
- Speaker notes: <added/not applicable>

## Visual QA
| Check | Status | Notes |
|-------|--------|-------|
| No overlapping elements | PASS/FAIL | ... |
| No text overflow | PASS/FAIL | ... |
| Consistent design | PASS/FAIL | ... |
| Color palette applied | PASS/FAIL | ... |
| Adequate contrast | PASS/FAIL | ... |

## QA Rounds
- Round 1: <issues found and fixed>
- Round 2: <issues found and fixed, if applicable>
- Round 3: <issues found and fixed, if applicable>

## Overall: PASS / FAIL
```

## Step 9: Write Executive Summary

Write `/app/results/summary.md`:

```markdown
# PPTX Skill Run — Results

## Overview
- **Date**: <run date>
- **Workflow**: <read|edit|create>
- **Input**: <input path or "none">
- **Output**: /app/results/output.pptx
- **Slides generated**: <N>

## QA Outcome
<Overall PASS or FAIL with brief explanation>

## Issues / Manual Follow-up
- <Any design issues that required more than 1 QA round>
- <Any remaining issues after 3 QA rounds>

## Provenance
- Runbook: skill-to-runbook-converter v1.0.0
- Origin: https://skills.sh/anthropics/skills/pptx
```

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"

# Check required files based on workflow
for f in \
  "$RESULTS_DIR/qa_report.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Check workflow-specific outputs
case "$WORKFLOW" in
  read)
    [ -s "$RESULTS_DIR/extracted_text.md" ] && echo "PASS: extracted_text.md" || echo "FAIL: extracted_text.md missing"
    ;;
  edit|create)
    [ -s "$RESULTS_DIR/output.pptx" ] && echo "PASS: output.pptx" || echo "FAIL: output.pptx missing"
    [ -s "$RESULTS_DIR/thumbnails.jpg" ] && echo "PASS: thumbnails.jpg" || echo "FAIL: thumbnails.jpg missing"
    ;;
esac
```

### Checklist

- [ ] QA was run and `qa_report.md` documents results
- [ ] All required output files exist and are non-empty
- [ ] No placeholder text (`xxxx`, `lorem`, `todo`, `sample`) remains in the output
- [ ] Thumbnails reviewed (visually or via subagent)
- [ ] Color palette applied consistently across all slides
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Always generate thumbnails.** Even for simple edits, visual inspection catches layout regressions that text inspection misses.
- **Use subagents for visual QA.** Delegate thumbnail review to a subagent to keep the main context focused on generation.
- **PptxGenJS coordinates are in inches.** Default slide is 10" × 7.5" (16:9). Plan your layout in inches before coding.
- **Markitdown for rapid inspection.** Run `python -m markitdown` first to understand the structure before unpacking XML — it is much faster.
- **LibreOffice headless for conversion.** `soffice --headless` is the most reliable way to convert PPTX to images; ensure it is installed before starting.
- **One palette per deck.** Do not mix color palettes between slides — it makes decks look unprofessional and AI-generated.
- **Keep QA notes in `qa_report.md`.** Document what was found and fixed in each round so reviewers can audit the process.
