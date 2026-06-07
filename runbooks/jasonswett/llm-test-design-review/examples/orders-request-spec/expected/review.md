# Test Design Review

## Overall Assessment

The file under review (`d0436129.00.rb`) is a Rails request spec covering two scenarios for `POST /orders`. It is brief, which is a genuine virtue, but it accumulates several design problems that together make the tests fragile and misleading as specifications. The most consequential issues are: the first test uses `Order.last` (order-dependent, brittle) and the name `"works"` (uninformative), while the second test asserts on a mock method call rather than an observable outcome and couples itself to `PaymentGateway.new`. Fixing the `avoid-arbitrariness` and `observable-not-method-calls` violations would most improve the test suite's long-term reliability.

| Guideline | Violations | Severity |
|-----------|-----------|----------|
| `no-described-class` | 1 | Medium |
| `describe-the-essence` | 1 | Medium |
| `specification-format` | 1 | High |
| `avoid-arbitrariness` | 1 | High |
| `observable-not-method-calls` | 1 | High |
| `no-tight-coupling` | 1 | Medium |
| *(all others)* | 0 | — |

---

## `specification-format` — Test names must describe a scenario and expected outcome

### Finding — line 5

**Offending code:**
```ruby
it "works" do
```

**Why it violates the guideline:** `"works"` conveys nothing about the scenario being exercised or the expected outcome. A reader cannot tell from the name what the test is checking or when it would legitimately fail.

**Suggested fix:**
```ruby
it "creates an order with the given SKU" do
```

---

## `avoid-arbitrariness` — Don't retrieve records with `.last`

### Finding — line 7

**Offending code:**
```ruby
order = Order.last
```

**Why it violates the guideline:** `.last` is insertion-order dependent. If any other code path creates an `Order` before this line runs (a before-hook, a factory, or a parallel test), the retrieved record is silently wrong, producing a false positive or a misleading failure.

**Suggested fix:**
```ruby
it "creates an order with the given SKU" do
  expect {
    post orders_path, params: { sku: "ABC-1", qty: 2 }
  }.to change { Order.where(sku: "ABC-1").count }.by(1)
end
```

---

## `observable-not-method-calls` — Assert observable outcomes, not method calls

### Finding — lines 12–19

**Offending code:**
```ruby
it "charges the customer" do
  gateway = instance_double(PaymentGateway, charge: true)
  allow(PaymentGateway).to receive(:new).and_return(gateway)

  post orders_path, params: { sku: "ABC-1", qty: 2 }

  expect(gateway).to have_received(:charge).with(amount: 1998)
end
```

**Why it violates the guideline:** `have_received(:charge)` asserts that a specific method was invoked — the means — rather than the observable end (the customer was actually charged). If the controller is refactored to call a different method, delegate to a service object, or use an enqueued job, this test breaks even if the externally observable behavior is identical. The guideline permits stubbing true externals such as a payment processor, but the assertion should still target a real effect.

**Suggested fix:**
```ruby
it "records a charge for the order amount" do
  # Using a persisted Charge record as the observable outcome:
  expect {
    post orders_path, params: { sku: "ABC-1", qty: 2 }
  }.to change { Charge.where(amount_cents: 1998).count }.by(1)

  # Or, if the gateway exposes a test-mode log:
  # expect(PaymentGateway.test_charges.last[:amount]).to eq(1998)
end
```

---

## `no-tight-coupling` — Don't couple to internal instantiation mechanisms

### Finding — lines 13–14

**Offending code:**
```ruby
gateway = instance_double(PaymentGateway, charge: true)
allow(PaymentGateway).to receive(:new).and_return(gateway)
```

**Why it violates the guideline:** Intercepting `PaymentGateway.new` binds the test to a specific internal construction pattern. If the controller switches to `PaymentGateway.for_environment`, a factory method, or dependency injection, the test breaks even if the charging behavior is unchanged. Prefer a test-mode gateway that records calls at the class level rather than patching object construction.

**Suggested fix:**
```ruby
before { PaymentGateway.test_mode! }
after  { PaymentGateway.reset! }

it "records a charge for the order amount" do
  post orders_path, params: { sku: "ABC-1", qty: 2 }
  # then assert the observable outcome — see observable-not-method-calls
end
```

---

## `describe-the-essence` — `describe`/`context` strings must capture scenario meaning

### Finding — line 4

**Offending code:**
```ruby
describe "POST /orders" do
```

**Why it violates the guideline:** `"POST /orders"` names the HTTP mechanism, not the user-facing scenario. The reader learns the route and verb but not what the block of tests is specifying about system behaviour.

**Suggested fix:**
```ruby
describe "placing an order" do
```

---

## `no-described-class` — Use the actual class name, not `described_class`

### Finding — line 3

**Offending code:**
```ruby
RSpec.describe described_class do
```

**Why it violates the guideline:** `described_class` is a forward reference to whatever class the outer `describe` wraps. Here, however, the outer `describe` is this call itself — there is no enclosing block providing a class, so `described_class` resolves to `nil` at runtime and adds confusion rather than clarity. Even where it works, replacing it with the actual class name makes the file self-documenting.

**Suggested fix:**
```ruby
RSpec.describe OrdersController do
```
