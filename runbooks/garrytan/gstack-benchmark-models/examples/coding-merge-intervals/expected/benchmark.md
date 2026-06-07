# Cross-Model Benchmark

Prompt: 330 chars · Models: 3 (3 ran) · Judge: True

| Model | Latency | Tokens | Cost | Quality (0-10) | Status |
|-------|---------|--------|------|----------------|--------|
| claude-sonnet-4-6 | 3.32s | 296 | n/a | 10 | ok |
| gpt-4o | 2.39s | 277 | $0.00218 | 10 | ok |
| gemini/gemini-2.5-flash | 12.52s | 2740 | $0.00669 | 9 | ok |

## Recommendation

- **Fastest:** gpt-4o
- **Cheapest:** gpt-4o
- **Highest quality:** claude-sonnet-4-6
- **Benchmark cost:** $0.008867

## Best Overall

**gpt-4o** was fastest (2.39s) but **claude-sonnet-4-6** responded in 3.32s with higher quality.  

**Pick claude-sonnet-4-6** if output quality is critical; **gpt-4o** if cost dominates; **gpt-4o** for latency-sensitive workloads.

## Per-Model Outputs

### claude-sonnet-4-6

**Judge:** 10/10 — The implementation is correct, complete, and clear: it handles empty input, single intervals, and overlapping intervals correctly, includes a one-line docstring, and provides exactly 3 assert statements that demonstrate all required cases.

```python
```python
def merge_intervals(intervals):
    """Merge overlapping intervals and return sorted non-overlapping intervals."""
    if not intervals:
        return []
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged = [sorted_intervals[0]]
    for start, end in sorted_intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


assert merge_intervals([]) == []
assert merge_intervals([[1, 3]]) == [[1, 3]]
assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
```
```

### gpt-4o

**Judge:** 10/10 — The implementation is correct, handles empty input and single interval, includes a one-line docstring, has exactly 3 assert statements, and the merging logic properly handles overlapping intervals by sorting and comparing boundaries.

```python
```python
def merge_intervals(intervals):
    """Merge and return non-overlapping intervals sorted by start."""
    if not intervals:
        return []
    
    # Sort intervals by starting time
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]

    for current in intervals[1:]:
        prev = merged[-1]
        if current[0] <= prev[1]:  # There is an overlap
            # Merge the current interval with the previous one
            prev[1] = max(prev[1], current[1])
        else:
            merged.append(current)

    return merged

# Example assert statements
assert merge_intervals([]) == []
assert merge_intervals([[1, 3]]) == [[1, 3]]
assert merge_intervals([[1, 4], [2, 5], [7, 8]]) == [[1, 5], [7, 8]]
```
```

### gemini/gemini-2.5-flash

**Judge:** 9/10 — The function is correct, complete, and clear with a proper docstring, handles empty input and single intervals, and includes exactly 3 valid assert statements; the only minor note is that it mutates the input list via sort, but this doesn't affect correctness of the output.

```python
```python
def merge_intervals(intervals):
    """Merges overlapping intervals and returns them sorted by start."""
    if not intervals:
        return []

    intervals.sort(key=lambda x: x[0])
    
    merged = []
    for interval in intervals:
        # If the merged list is empty or the current interval does not overlap with the last merged interval,
        # simply append it.
        if not merged or interval[0] > merged[-1][1]:
            merged.append(interval)
        # Otherwise, there is an overlap, so merge the current and previous intervals.
        # Update the end time of the last merged interval if the current interval extends further.
        else:
            merged[-1][1] = max(merged[-1][1], interval[1])
            
    return merged

assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]
assert merge_intervals([[1, 4], [0, 4]]) == [[0, 4]]
```
```
