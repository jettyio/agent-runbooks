# Cross-Model Benchmark — Results

## Overview
- **Date**: 2026-06-07T12:13:35.702655+00:00  ·  **Prompt source**: /app/assets/f7a86295.00.md  ·  **Judge**: True
- **Models requested**: 3  ·  **Ran**: 3  ·  **Skipped/errored**: none
- **Benchmark cost**: $0.003825

## Results
| Model | Latency | Tokens | Cost | Quality |
|-------|---------|--------|------|---------|
| claude-sonnet-4-6 | 2.47s | 290 | n/a | 10 |
| gpt-4o | 1.52s | 246 | $0.00160 | 10 |
| gemini/gemini-2.5-flash | 4.81s | 991 | $0.00223 | 9 |

## Recommendation
- **Fastest**: gpt-4o (1.52s)
- **Cheapest**: gpt-4o ($0.00160)
- **Highest quality**: claude-sonnet-4-6 (score: 10)
- **Best overall**: claude-sonnet-4-6

**Tradeoff**: claude-sonnet-4-6 achieved the highest quality score with acceptable latency and cost.

## Notes / Limitations
- Prompt: JSON extraction from meeting notes (476 chars)
- All models received the identical prompt and system prompt (none)
- Quality scored by claude-sonnet-4-6 on correctness, completeness, and clarity (0–10)
