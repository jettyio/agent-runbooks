# Test Design Review — `cdfa87cc.00.rb`

## Overall Assessment

The file contains two tests for an `Order` model. Both tests exercise the right domain objects and the assertions are at least pointed at the right output, but both contain meaningful design problems. The first test is the more serious case: it asserts on the internal Rails cache key rather than any observable behavioral change, which is precisely the anti-pattern the `test-ends-not-means` guideline exists to prevent. The second test couples setup to a specific JSON serialisation shape that would be invisible to a reader unfamiliar with the model's internals. Three findings total: one high, one medium, one low.

| Guideline | Count | Severity |
|---|---|---|
| `test-ends-not-means` | 1 | High |
| `no-tight-coupling` | 1 | Medium |
| `describe-the-essence` | 1 | Low |

---

## `test-ends-not-means` — 1 finding (High)

> For caching/perf, assert the observable difference (e.g. zero extra DB queries), not the mechanism (Rails.cache.read).

### Finding — `cdfa87cc.00.rb` lines 7–8

**Offending code:**
```ruby
order.total
expect(Rails.cache.read("order/#{order.id}/total")).not_to be_nil
```

**Why it violates the guideline:**  
The assertion reaches inside the caching layer and reads from the cache store using a hard-coded key string. This tests the *mechanism* of caching (that a particular key exists in the store), not the *effect* of caching (that subsequent calls don't re-query the database). If the cache key format changes—or if the implementation switches from Rails.cache to another store—the test fails even when the behaviour is completely correct. The test also guarantees nothing about whether caching actually improves anything.

**Suggested fix:**  
Assert the observable outcome directly: a warm call should not trigger additional database queries.

```ruby
it "does not re-query the database on subsequent calls" do
  order = create(:order, :with_line_items)
  order.total  # warm the cache

  expect { order.total }.not_to make_database_queries
end
```

Use a query-counting matcher (e.g. the `db-query-matchers` gem) so the assertion is independent of the cache implementation.

---

## `no-tight-coupling` — 1 finding (Medium)

> Don't set up state via internal shapes when a behavioral input expresses the scenario.

### Finding — `cdfa87cc.00.rb` line 15

**Offending code:**
```ruby
task.update!(json_output: { "summary" => { "ok" => true } }.to_json)
```

**Why it violates the guideline:**  
The test reaches into the model's internal serialisation format (`json_output` containing a specific JSON structure) to put the task into a "finished" state. A reader must understand the internal shape to understand the scenario. More importantly, if the model's internal representation changes (e.g. the key `"ok"` is renamed, or the field is replaced with a dedicated column), this test breaks even though the observable behaviour—`display_status` returning `"Finished"`—has not changed.

**Suggested fix:**  
Drive the scenario through a factory trait or a domain method that expresses what "finished" means without exposing the internal shape:

```ruby
it "shows the finished status" do
  task = create(:task, :finished)   # :finished trait encodes the JSON internally
  expect(task.display_status).to eq("Finished")
end
```

If a factory trait isn't available, use whatever domain-level completion method the model exposes:

```ruby
task.complete!(summary: { ok: true })
```

---

## `describe-the-essence` — 1 finding (Low)

> `describe`/`context` strings should capture the scenario's meaning, not a code token.

### Finding — `cdfa87cc.00.rb` line 4

**Offending code:**
```ruby
describe "#total" do
```

**Why it violates the guideline:**  
`"#total"` is the Ruby method-sigil notation for the method name—a code token, not a description of the behaviour or scenario being specified. A reader learns nothing about *what* `#total` does or under what conditions.

**Suggested fix:**  
Rename the describe block to describe the capability:

```ruby
describe "computing the order total" do
```
