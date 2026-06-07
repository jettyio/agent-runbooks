# The Verification Gap in AI Agents

**Through-line:** AI agents can act confidently and fail silently — the engineering discipline of verification is what separates reliable agents from risky ones.

## Deck Details

| Property | Value |
|----------|-------|
| Slide count | 11 |
| Style preset | `dark-botanical` |
| Fonts | Cormorant (display) / IBM Plex Sans (body) / IBM Plex Mono (code) |
| Target audience | Engineers building or deploying AI agents |
| Density mode | Speaker-led |

## Slide Outline

1. **Cover** — The Verification Gap in AI Agents
2. **Statement** — Agents don't crash. They hallucinate and keep going.
3. **Content** — What do agents actually get wrong? (Factual / Action / Compounding)
4. **Content** — Compounding: one bad step multiplies
5. **Section** — The Verification Gap
6. **Two-column** — What agents report vs. what actually happened
7. **Content** — Three verification strategies engineers can ship today
8. **Code** — Assertion layers: catch the gap at the seam
9. **Content** — When to put a human in the loop — and where
10. **Content** — Audit trails: the post-mortem you'll need
11. **Closing** — Close the gap — before your agent closes it for you

## Running the Deck

```bash
# Install Slidev CLI (if not already installed)
npm install -g @slidev/cli

# Start the presentation dev server
slidev slides.md

# Export to PDF
slidev export slides.md --output deck.pdf
```

## Project Structure

```
/app/results/
├── slides.md          # Slidev source (main deliverable)
├── deck.pdf           # Compiled PDF export
├── deck.spec.md       # Slide deck specification
├── README.md          # This file
├── summary.md         # Run metadata and validation results
├── validation_report.json
└── styles/
    └── tokens.css     # Dark botanical CSS token overrides
```
