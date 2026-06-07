# Cross-Model Benchmark — Results

## Overview
- **Date**: 2026-06-07T12:10:28.586049Z  ·  **Prompt source**: /app/assets/3d17a697.00.md  ·  **Judge**: enabled
- **Models requested**: 3  ·  **Ran**: 3  ·  **Skipped/errored**: 0
- **Benchmark cost**: $0.008867

## Results
| Model | Latency | Tokens | Cost | Quality |
|-------|---------|--------|------|---------|
| claude-sonnet-4-6 | 3.32s | 296 | n/a | 10 |
| gpt-4o | 2.39s | 277 | $0.00218 | 10 |
| gemini/gemini-2.5-flash | 12.52s | 2740 | $0.00669 | 9 |

## Recommendation
- **Fastest**: gpt-4o (2.39s)
- **Cheapest**: gpt-4o ($0.002178)
- **Highest quality**: claude-sonnet-4-6 (10/10)
- **Best overall**: **gpt-4o** is the speed leader (2.39s vs 3.32s for claude-sonnet-4-6). For latency-sensitive use cases, gpt-4o is the clear choice.

## Notes / Limitations
- Original model id `gemini/gemini-2.0-flash` was retired (404); automatically retried with `gemini/gemini-2.5-flash` which ran successfully.
- All three models scored 9–10/10 on a well-defined algorithmic task; quality gaps would likely widen on open-ended or creative prompts.
- Gemini cost is estimated from litellm pricing tables and may not reflect exact billing.
