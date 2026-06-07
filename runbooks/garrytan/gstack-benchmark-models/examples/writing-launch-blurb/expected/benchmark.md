# Cross-Model Benchmark

Prompt: 228 chars · Models: 3 (3 ran) · Judge: True

| Model | Latency | Tokens | Cost | Quality (0-10) | Status |
|-------|---------|--------|------|----------------|--------|
| claude-sonnet-4-6 | 4.95s | 227 | n/a | 9 | ok |
| gpt-4o | 1.71s | 177 | $0.00133 | 3 | ok |
| gemini/gemini-2.5-flash | 13.04s | 2831 | $0.00695 | 7 | ok |

## Recommendation

- **Fastest:** gpt-4o (1.71s)
- **Cheapest:** gpt-4o ($0.00133)
- **Highest quality:** claude-sonnet-4-6 (score: 9)
- **Benchmark cost:** $0.008282

## Best Overall

**claude-sonnet-4-6** is the clear winner on quality (9/10) and is the second-fastest. The tradeoff: its cost is unknown (litellm has no pricing for this new model id), while gpt-4o was fastest (1.71s, $0.00133) and gemini/gemini-2.5-flash was cheapest ($0.00695 but slowest at 13s and scored 7/10). For quality-critical workloads choose Claude; for cost- or latency-critical workloads choose GPT-4o.