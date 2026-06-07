# Test Design Review — `78d5514b.00.rb`

## Overall Assessment

The file contains two system tests for a Dashboard feature. Both tests have meaningful
design problems. The most urgent is a forward-reference ordering bug (lines 6–7) that will
cause `let!(:order)` to raise a `NameError` or produce a broken fixture because it
references `:customer` before `:customer` is defined. The second test directly injects a
value into a controller instance variable (`instance_variable_set`), bypassing the real
order-counting logic entirely. Additional issues include a URL-based assertion
(`have_current_path`), labelling that names code tokens instead of scenarios (`scope=active`,
`redirect`), a stub of an internal authorization predicate, and an unexplained `wait: 3`.
Fixing the forward-reference and instance-variable issues should be the first priority.

## Findings by Guideline

| Guideline              | Count | Severity (H/M/L) |
|------------------------|-------|------------------|
| describe-the-essence   | 2     | M, L             |
| avoid-forward-reference| 1     | H                |
| no-have-current-path   | 1     | M                |
| no-instance-variable-set | 1   | H                |
| no-tight-coupling      | 2     | H, M             |
| no-speculative-coding  | 1     | L                |
| **Total**              | **8** |                  |

---

## `describe-the-essence`

### Finding 1 — line 4 (medium)

**Offending code:**
```ruby
describe "scope=active" do
```

**Why:** The label is a raw query-string token, not a description of the business scenario.
A reader cannot infer what situation is under test from `scope=active`.

**Suggested fix:**
```ruby
describe "when viewing active orders" do
```

---

### Finding 2 — line 5 (low)

**Offending code:**
```ruby
context "redirect" do
```

**Why:** "redirect" names the mechanism (a redirect will happen), not the precondition or
scenario. The reader does not know *when* or *why* a redirect occurs.

**Suggested fix:**
```ruby
context "when an authenticated customer visits the root path" do
```

---

## `avoid-forward-reference`

### Finding 3 — lines 6–7 (high)

**Offending code:**
```ruby
let!(:order) { create(:order, customer: customer) }
let!(:customer) { create(:customer) }
```

**Why:** `:order` is declared with `let!` (eager evaluation) before `:customer` is defined.
When RSpec evaluates `let!(:order)` it looks up `customer`, which is not yet memoized. This
produces a `NameError` or creates the order with no customer, making both tests unreliable.

**Suggested fix:**
```ruby
let!(:customer) { create(:customer) }
let!(:order)    { create(:order, customer: customer) }
```

---

## `no-have-current-path`

### Finding 4 — line 19 (medium)

**Offending code:**
```ruby
expect(page).to have_current_path(orders_path)
```

**Why:** The assertion couples the test to the URL. If the route path changes while the
page content stays identical, the test fails even though nothing visible to the user
changed.

**Suggested fix:** Assert on what the user actually sees on the destination page:
```ruby
expect(page).to have_content("Your Orders")
```

---

## `no-instance-variable-set`

### Finding 5 — line 23 (high)

**Offending code:**
```ruby
controller.instance_variable_set(:@order_count, 5)
```

**Why:** Forcing a controller ivar bypasses the real code path that populates `@order_count`.
Any bug in that path is invisible to this test. Per the guideline, if `instance_variable_set`
seems necessary, that signals a design problem in the production code — the count should
come from an accessible data source (e.g. a scoped query on the association).

**Suggested fix:** Create five real orders so the controller computes the count naturally
(one already exists from `let!(:order)`):
```ruby
4.times { create(:order, customer: customer) }
visit dashboard_path
expect(page).to have_content("5 orders")
```

---

## `no-tight-coupling`

### Finding 6 — lines 23–25 (high)

**Offending code:**
```ruby
controller.instance_variable_set(:@order_count, 5)
visit dashboard_path
expect(page).to have_content("5 orders", wait: 3)
```

**Why:** The test short-circuits the application's order-counting logic by injecting the
result directly into the controller's internal state. A change to how the count is computed
would not be caught by this test.

**Suggested fix:**
```ruby
5.times { create(:order, customer: customer) }
visit dashboard_path
expect(page).to have_content("5 orders")
```

---

### Finding 7 — line 13 (medium)

**Offending code:**
```ruby
allow_any_instance_of(User).to receive(:can_view?).and_return(true)
```

**Why:** Stubbing the internal authorization predicate couples both tests to the private
method name `can_view?`. If the authorization model is restructured (method renamed, moved
to a policy object) the stub silently continues to return `true`, masking regressions.

**Suggested fix:** Remove the stub and configure the user through the application's real
authorization API so `can_view?` returns `true` naturally:
```ruby
customer.user.grant_permission(:dashboard)  # or equivalent for this app's auth system
```

---

## `no-speculative-coding`

### Finding 8 — line 25 (low)

**Offending code:**
```ruby
expect(page).to have_content("5 orders", wait: 3)
```

**Why:** `wait: 3` is an unexplained magic number. If the page renders synchronously the
wait adds unnecessary latency and obscures intent; if there is a genuine async operation,
the reason is invisible to the reader.

**Suggested fix:** Remove the timeout if unneeded:
```ruby
expect(page).to have_content("5 orders")
```
Or add a comment if a real async condition requires it:
```ruby
expect(page).to have_content("5 orders", wait: 3)  # order-count widget polls every 2 s
```
