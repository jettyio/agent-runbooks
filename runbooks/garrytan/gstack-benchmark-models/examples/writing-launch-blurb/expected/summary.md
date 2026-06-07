# Cross-Model Benchmark — Results

## Overview
- **Date**: 2026-06-07T12:13:52.888123Z  ·  **Prompt source**: /app/assets/1b299910.00.md  ·  **Judge**: True
- **Models requested**: 3  ·  **Ran**: 3  ·  **Skipped/errored**: none
- **Benchmark cost**: $0.008282

## Results
| Model | Latency | Tokens | Cost | Quality |
|-------|---------|--------|------|---------|
| claude-sonnet-4-6 | 4.95s | 227 | n/a | 9 |
| gpt-4o | 1.71s | 177 | $0.00133 | 3 |
| gemini/gemini-2.5-flash | 13.04s | 2831 | $0.00695 | 7 |

## Recommendation
- **Fastest**: gpt-4o (1.71s)
- **Cheapest**: gpt-4o ($0.00133)
- **Highest quality**: claude-sonnet-4-6 (score: 9/10)
- **Best overall**: claude-sonnet-4-6 wins on quality (9/10). The key tradeoff: GPT-4o is 3× faster and has known pricing ($0.00133), making it the pick for latency- or cost-sensitive workloads. Gemini 2.5 Flash was cheapest ($0.00695) but slowest and scored 2 points below Claude. If output quality matters most, choose Claude; if speed and predictable cost matter more, choose GPT-4o.

## Notes / Limitations
- `claude-sonnet-4-6` cost is unavailable — litellm does not yet have pricing for this new model id (`anthropic/claude-4.6-sonnet-20260217`). Cost is marked `n/a`; actual spend was non-zero.
- All three models ran without errors.
- Judge model: claude-sonnet-4-6.
