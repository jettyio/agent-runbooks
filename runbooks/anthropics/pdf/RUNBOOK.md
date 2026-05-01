---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/anthropics/skills/pdf"
  source_host: "skills.sh"
  source_title: "PDF Processing Guide"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "anthropics"
    skill_name: "pdf"
    confidence: "high"
secrets: {}
---

# PDF Processing Guide — Agent Runbook

## Objective

Process PDF files using Python libraries and command-line tools to perform operations such as reading, extracting text and tables, merging, splitting, rotating pages, adding watermarks, creating new PDFs, filling forms, encrypting/decrypting, extracting images, and performing OCR on scanned documents. This runbook covers the full lifecycle of PDF manipulation: from initial environment setup and dependency installation through execution of the requested operation to final verification of outputs. Use this runbook whenever the user references a `.pdf` file or requests any PDF-related transformation. For advanced features, JavaScript libraries, and detailed examples, see REFERENCE.md; for form-filling workflows, see FORMS.md.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/output.pdf` | The primary output PDF (merged, split page, rotated, watermarked, encrypted, or newly created) — omit if the task is text/table extraction only |
| `/app/results/extracted_text.txt` | Extracted text content (for text-extraction tasks) |
| `/app/results/extracted_tables.xlsx` | Extracted tables as Excel workbook (for table-extraction tasks) |
| `/app/results/summary.md` | Executive summary: operation performed, input files, output files, any warnings |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

If a task only produces a subset of the above (e.g., only a merged PDF with no text extraction), mark inapplicable files as skipped in `validation_report.json` and note them in `summary.md`.

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Input PDF(s) | *(required)* | One or more input PDF file paths |
| Operation | *(required)* | One of: `merge`, `split`, `extract-text`, `extract-tables`, `rotate`, `watermark`, `create`, `encrypt`, `decrypt`, `ocr`, `extract-images`, `fill-form` |
| Output filename | `output.pdf` | Name for the primary output file |
| Password | *(optional)* | Password for encrypt/decrypt operations |
| Rotation degrees | `90` | Degrees to rotate pages (for `rotate` operation) |
| Page range | *(optional)* | Page range for split/extract operations (e.g., `1-5`) |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `pypdf` | Python package | Yes | Basic PDF operations: merge, split, rotate, metadata, password protection |
| `pdfplumber` | Python package | Yes | Text and table extraction with layout preservation |
| `reportlab` | Python package | Yes | PDF creation using canvas or Platypus document templates |
| `pytesseract` | Python package | Conditional | OCR on scanned PDFs (required for `ocr` operation) |
| `pdf2image` | Python package | Conditional | Convert PDF pages to images for OCR (required for `ocr` operation) |
| `pandas` | Python package | Conditional | Advanced table export to Excel (required for `extract-tables` operation) |
| `openpyxl` | Python package | Conditional | Excel writer backend for pandas (required for `extract-tables` operation) |
| `poppler-utils` | System package | Conditional | Provides `pdftotext` and `pdfimages` CLI tools |
| `qpdf` | System package | Conditional | CLI-based merge, split, rotate, decrypt |
| `pdftk` | System package | Optional | Alternative CLI merge/split/rotate tool |
| `tesseract-ocr` | System package | Conditional | OCR engine (required for `ocr` operation) |

---

## Step 1: Environment Setup

Install all Python dependencies and verify CLI tools are available.

```bash
echo "=== Installing Python dependencies ==="
pip install pypdf pdfplumber reportlab

# Install optional dependencies based on operation
OPERATION="${OPERATION:-extract-text}"
if [[ "$OPERATION" == "ocr" ]]; then
  pip install pytesseract pdf2image
fi
if [[ "$OPERATION" == "extract-tables" ]]; then
  pip install pandas openpyxl
fi

echo "=== Checking CLI tools ==="
command -v pdftotext >/dev/null 2>&1 && echo "pdftotext: OK" || echo "pdftotext: not found (install poppler-utils)"
command -v qpdf      >/dev/null 2>&1 && echo "qpdf: OK"      || echo "qpdf: not found"
command -v pdftk     >/dev/null 2>&1 && echo "pdftk: OK"     || echo "pdftk: not found (optional)"

echo "=== Creating output directory ==="
mkdir -p /app/results
```

Verify Python imports succeed before proceeding:

```python
from pypdf import PdfReader, PdfWriter
import pdfplumber
from reportlab.lib.pagesizes import letter
print("All core dependencies imported successfully")
```

---

## Step 2: Validate Inputs

Verify that the input PDF(s) exist and are readable before running any operation.

```python
import pathlib, sys

input_files = ["/app/results/input.pdf"]  # Replace with actual input path(s)

for f in input_files:
    p = pathlib.Path(f)
    if not p.exists():
        print(f"ERROR: Input file not found: {f}")
        sys.exit(1)
    if p.stat().st_size == 0:
        print(f"ERROR: Input file is empty: {f}")
        sys.exit(1)
    print(f"OK: {f} ({p.stat().st_size} bytes)")

print("All input files validated.")
```

---

## Step 3: Execute PDF Operation

Choose the appropriate code block for the requested operation. Run the relevant section only.

### 3a: Merge PDFs

```python
from pypdf import PdfWriter, PdfReader
import pathlib

input_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]  # Replace with actual paths
output_path = "/app/results/output.pdf"

writer = PdfWriter()
for pdf_file in input_files:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open(output_path, "wb") as output:
    writer.write(output)
print(f"Merged {len(input_files)} PDFs → {output_path}")
```

### 3b: Split PDF

```python
from pypdf import PdfReader, PdfWriter
import pathlib

input_path = "/app/results/input.pdf"
output_dir = pathlib.Path("/app/results")

reader = PdfReader(input_path)
output_files = []
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    out_path = output_dir / f"page_{i+1}.pdf"
    with open(out_path, "wb") as output:
        writer.write(output)
    output_files.append(str(out_path))

print(f"Split into {len(output_files)} pages: {output_files}")
```

### 3c: Extract Text

```python
import pdfplumber, pathlib

input_path = "/app/results/input.pdf"
output_path = "/app/results/extracted_text.txt"

text_parts = []
with pdfplumber.open(input_path) as pdf:
    for i, page in enumerate(pdf.pages):
        t = page.extract_text()
        if t:
            text_parts.append(f"=== Page {i+1} ===\n{t}")

full_text = "\n\n".join(text_parts)
pathlib.Path(output_path).write_text(full_text)
print(f"Extracted {len(full_text)} characters → {output_path}")
```

For scanned PDFs, use OCR instead (see Step 3g).

### 3d: Extract Tables

```python
import pdfplumber, pandas as pd, pathlib

input_path = "/app/results/input.pdf"
output_path = "/app/results/extracted_tables.xlsx"

all_tables = []
with pdfplumber.open(input_path) as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for table in tables:
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                df.insert(0, "source_page", i + 1)
                all_tables.append(df)

if all_tables:
    combined = pd.concat(all_tables, ignore_index=True)
    combined.to_excel(output_path, index=False)
    print(f"Extracted {len(all_tables)} table(s) with {len(combined)} rows → {output_path}")
else:
    pathlib.Path(output_path).write_text("")
    print("No tables found in the PDF.")
```

### 3e: Rotate Pages

```python
from pypdf import PdfReader, PdfWriter

input_path = "/app/results/input.pdf"
output_path = "/app/results/output.pdf"
degrees = 90  # Replace with desired rotation

reader = PdfReader(input_path)
writer = PdfWriter()
for page in reader.pages:
    page.rotate(degrees)
    writer.add_page(page)

with open(output_path, "wb") as out:
    writer.write(out)
print(f"Rotated all pages by {degrees}° → {output_path}")
```

### 3f: Add Watermark

```python
from pypdf import PdfReader, PdfWriter

watermark_path = "/app/results/watermark.pdf"
input_path = "/app/results/input.pdf"
output_path = "/app/results/output.pdf"

watermark = PdfReader(watermark_path).pages[0]
reader = PdfReader(input_path)
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open(output_path, "wb") as out:
    writer.write(out)
print(f"Watermark applied → {output_path}")
```

### 3g: OCR Scanned PDFs

```python
# Requires: pip install pytesseract pdf2image
# Requires: apt-get install tesseract-ocr poppler-utils
import pytesseract, pathlib
from pdf2image import convert_from_path

input_path = "/app/results/input.pdf"
output_path = "/app/results/extracted_text.txt"

images = convert_from_path(input_path)
text_parts = []
for i, image in enumerate(images):
    page_text = pytesseract.image_to_string(image)
    text_parts.append(f"=== Page {i+1} ===\n{page_text}")

full_text = "\n\n".join(text_parts)
pathlib.Path(output_path).write_text(full_text)
print(f"OCR complete: {len(images)} pages, {len(full_text)} chars → {output_path}")
```

### 3h: Password Protection / Encryption

```python
from pypdf import PdfReader, PdfWriter

input_path = "/app/results/input.pdf"
output_path = "/app/results/output.pdf"
user_password = "userpassword"    # Replace
owner_password = "ownerpassword"  # Replace

reader = PdfReader(input_path)
writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)

writer.encrypt(user_password, owner_password)
with open(output_path, "wb") as out:
    writer.write(out)
print(f"Encrypted → {output_path}")
```

### 3i: Decrypt / Remove Password

```bash
# Using qpdf
qpdf --password=mypassword --decrypt /app/results/input.pdf /app/results/output.pdf
echo "Decrypted → /app/results/output.pdf"
```

### 3j: Extract Images

```bash
# Using pdfimages (poppler-utils)
mkdir -p /app/results/images
pdfimages -j /app/results/input.pdf /app/results/images/img
echo "Images extracted to /app/results/images/"
ls /app/results/images/
```

### 3k: Create New PDF

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

output_path = "/app/results/output.pdf"

doc = SimpleDocTemplate(output_path, pagesize=letter)
styles = getSampleStyleSheet()
story = []

story.append(Paragraph("Document Title", styles['Title']))
story.append(Spacer(1, 12))
story.append(Paragraph("Document body content goes here.", styles['Normal']))

# IMPORTANT: Never use Unicode subscript/superscript chars (₀¹²) in ReportLab.
# Use XML tags instead: <sub>2</sub> or <super>2</super> in Paragraph objects.

doc.build(story)
print(f"Created PDF → {output_path}")
```

---

## Step 4: Iterate on Errors (max 3 rounds)

If Step 3 raised an exception or produced an empty/corrupt output file:

1. Check the error message for the specific failure class
2. Apply the relevant fix from the Common Fixes table below
3. Re-run the affected Step 3 sub-section
4. Repeat up to **3 rounds total**

After 3 rounds, if the output is still invalid, record the failure in `summary.md` and `validation_report.json` with `overall_passed: false` and stop.

### Common Fixes

| Issue | Fix |
|-------|-----|
| `FileNotFoundError` on input PDF | Verify the input path; check for typos or missing uploads |
| `PdfReadError: EOF marker not found` | The PDF may be corrupt or truncated; try with qpdf: `qpdf --check input.pdf` |
| `PasswordError` on encrypted PDF | Pass the correct password to `PdfReader("file.pdf", password="...")` |
| Empty extracted text (not scanned) | Try pdfplumber instead of pypdf for text extraction |
| Empty extracted text (scanned PDF) | Install tesseract and use OCR workflow (Step 3g) |
| ReportLab renders black boxes for subscripts | Replace Unicode sub/superscript chars with `<sub>` / `<super>` XML tags |
| `qpdf` or `pdftotext` not found | Install system packages: `apt-get install -y qpdf poppler-utils pdftk` |
| Tables extracted with None values | Rows with merged cells return `None`; filter with `if cell is not None` |

---

## Step 5: Validate Outputs

Verify that all expected output files exist and are non-empty.

```python
import pathlib, json, sys

results_dir = pathlib.Path("/app/results")
operation = "extract-text"  # Replace with actual operation

# Define expected outputs per operation
EXPECTED = {
    "merge":          ["output.pdf"],
    "split":          [],  # Dynamic; check for page_*.pdf files
    "extract-text":   ["extracted_text.txt"],
    "extract-tables": ["extracted_tables.xlsx"],
    "rotate":         ["output.pdf"],
    "watermark":      ["output.pdf"],
    "create":         ["output.pdf"],
    "encrypt":        ["output.pdf"],
    "decrypt":        ["output.pdf"],
    "ocr":            ["extracted_text.txt"],
    "extract-images": [],  # Check images/ subdir
    "fill-form":      ["output.pdf"],
}

stages = []
overall_passed = True

for fname in EXPECTED.get(operation, []):
    fpath = results_dir / fname
    passed = fpath.exists() and fpath.stat().st_size > 0
    stages.append({"name": f"output:{fname}", "passed": passed,
                   "message": f"{fpath} ({fpath.stat().st_size if fpath.exists() else 'MISSING'} bytes)"})
    if not passed:
        overall_passed = False

# Always check summary.md and validation_report.json
for fname in ["summary.md", "validation_report.json"]:
    fpath = results_dir / fname
    passed = fpath.exists() and fpath.stat().st_size > 0
    stages.append({"name": f"output:{fname}", "passed": passed,
                   "message": str(fpath)})

print(json.dumps({"stages": stages, "overall_passed": overall_passed}, indent=2))
```

---

## Step 6: Write Executive Summary

Write `/app/results/summary.md` with a concise record of the run.

```python
import pathlib, datetime

content = f"""# PDF Processing — Run Summary

## Operation
- **Operation**: <replace with actual operation>
- **Input**: <replace with input file(s)>
- **Output**: <replace with output file(s)>
- **Date**: {datetime.datetime.utcnow().isoformat()}Z

## Validation

| Check | Status | Notes |
|-------|--------|-------|
| Input file exists | ✓ PASS | |
| Operation completed | ✓ PASS | |
| Output file non-empty | ✓ PASS | |
| summary.md written | ✓ PASS | |
| validation_report.json written | ✓ PASS | |

## Issues / Notes
- None

## Provenance
- Skill: pdf by anthropics/skills
- Origin: https://skills.sh/anthropics/skills/pdf
- Imported by: skill-to-runbook-converter v1.0.0
"""
pathlib.Path("/app/results/summary.md").write_text(content)
print("summary.md written")
```

---

## Step 7: Write Validation Report

Write `/app/results/validation_report.json`.

```python
import json, pathlib, datetime

report = {
    "version": "1.0.0",
    "run_date": datetime.datetime.utcnow().isoformat() + "Z",
    "parameters": {
        "skill_url": "https://skills.sh/anthropics/skills/pdf",
        "operation": "<replace>",
        "input_files": ["<replace>"],
    },
    "stages": [
        {"name": "setup",        "passed": True, "message": "Dependencies installed"},
        {"name": "validation",   "passed": True, "message": "Input files verified"},
        {"name": "execution",    "passed": True, "message": "Operation completed"},
        {"name": "output_check", "passed": True, "message": "Output files non-empty"},
    ],
    "results": {"pass": 4, "partial": 0, "fail": 0},
    "overall_passed": True,
    "output_files": [
        "/app/results/output.pdf",
        "/app/results/summary.md",
        "/app/results/validation_report.json",
    ]
}

pathlib.Path("/app/results/validation_report.json").write_text(json.dumps(report, indent=2))
print("validation_report.json written")
```

---

## Step 8: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"

# Check mandatory files
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Check operation-specific output (adjust as needed)
OPERATION="${OPERATION:-extract-text}"
case "$OPERATION" in
  merge|rotate|watermark|create|encrypt|decrypt|fill-form)
    OUT="$RESULTS_DIR/output.pdf"
    [ -s "$OUT" ] && echo "PASS: $OUT ($(wc -c < "$OUT") bytes)" || echo "FAIL: $OUT missing or empty"
    ;;
  extract-text|ocr)
    OUT="$RESULTS_DIR/extracted_text.txt"
    [ -s "$OUT" ] && echo "PASS: $OUT ($(wc -c < "$OUT") bytes)" || echo "FAIL: $OUT missing or empty"
    ;;
  extract-tables)
    OUT="$RESULTS_DIR/extracted_tables.xlsx"
    [ -s "$OUT" ] && echo "PASS: $OUT ($(wc -c < "$OUT") bytes)" || echo "FAIL: $OUT missing or empty"
    ;;
  split)
    COUNT=$(ls "$RESULTS_DIR"/page_*.pdf 2>/dev/null | wc -l)
    [ "$COUNT" -gt 0 ] && echo "PASS: $COUNT split page files found" || echo "FAIL: no split page files found"
    ;;
  extract-images)
    COUNT=$(ls "$RESULTS_DIR"/images/ 2>/dev/null | wc -l)
    [ "$COUNT" -gt 0 ] && echo "PASS: $COUNT image files extracted" || echo "FAIL: no images extracted"
    ;;
esac

echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] Input PDF(s) existed and were readable
- [ ] Correct operation was selected and executed without unhandled exceptions
- [ ] Primary output file is non-empty and valid (not corrupt)
- [ ] `extracted_text.txt` exists for text/OCR operations
- [ ] `extracted_tables.xlsx` exists for table-extraction operations
- [ ] `summary.md` documents the operation, inputs, outputs, and any warnings
- [ ] `validation_report.json` has `overall_passed: true` (or documents why it is `false`)
- [ ] Verification script above printed PASS for every applicable line
- [ ] No credentials or sensitive data were written to output files

**If ANY item fails, return to the relevant step and fix it. Do NOT finish until all applicable items pass.**

---

## Tips

- **pypdf vs pdfplumber for text extraction**: Use `pdfplumber` for higher-fidelity text and table extraction (preserves layout). Use `pypdf` for structural operations (merge, split, rotate, encrypt).
- **Scanned PDFs**: If `page.extract_text()` returns empty or garbage, the PDF is likely scanned. Switch to the OCR workflow (Step 3g) with `pytesseract` and `pdf2image`.
- **ReportLab subscripts/superscripts**: Never use Unicode sub/superscript characters (₀¹²³) in ReportLab. Use `<sub>` and `<super>` XML tags inside `Paragraph` objects. For canvas-drawn text, manually adjust font size and baseline offset instead.
- **Large PDFs**: For PDFs with hundreds of pages, process in batches or use `qpdf` CLI tools which are more memory-efficient than pure-Python approaches.
- **Password-protected PDFs**: Pass `password=` to `PdfReader` constructor; use `qpdf --decrypt` for command-line decryption.
- **Form filling**: This runbook covers standard PDF operations. For form filling (AcroForms), follow the dedicated instructions in FORMS.md.
- **CLI tools as fallback**: If Python libraries fail on a malformed PDF, `qpdf` and `pdftotext` (poppler-utils) are often more robust and worth trying as fallbacks.
