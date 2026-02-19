# Hypothesis: Making Discounts and Deadlines Visible

## Prerequisite: Seamless Baseline First

**This hypothesis is NOT to be executed until the comfac-webshop fork runs seamlessly as a drop-in replacement on a production-like ERPNext instance.** The execution order is:

1. **Phase 0 (Staging Sandbox):** Clone the production ERPNext instance, install comfac-webshop, validate it works identically to the existing webshop (see [wiki/12](12-Staging-Sandbox-Deployment.md)). No feature changes. Pass all validation checks.

2. **Phase 1 (Experiment Clone):** Once Phase 0 is proven stable, clone THAT successful staging instance into a second sandbox. This is where we implement and test the hypothesis below. If anything breaks, the Phase 0 baseline is untouched.

3. **Phase 2 (Iterate):** Test with sample products, pricing rules, coupons, and deadline-bearing offers on the experiment clone. Validate every scenario. Only when everything passes do we merge back to the main fork.

**Do not skip Phase 0.** The hypothesis below assumes a working, stable comfac-webshop instance as its foundation.

---

## Core Thesis

**All the data we need already exists on the Quotation document.** ERPNext's pricing engine populates discount fields on every cart save. We do not need to change the backend calculation logic. We need to:

1. **Surface existing hidden fields** in the cart templates
2. **Enrich the decorator** to pass pricing rule metadata (deadlines, titles) to the frontend
3. **Add summation logic** in the payment summary template
4. **Style it** so customers immediately see value and urgency

---

## Part 1: The Fields We Will Target

### Per-Item Fields (Quotation Item - already populated)

These fields exist on every `Quotation Item` row (`doc.items[]`) and are populated by ERPNext's `set_price_list_and_item_details()` method every time the cart is saved:

| Field | Type | What It Contains | Currently Used? |
|-------|------|------------------|-----------------|
| **`price_list_rate`** | Currency | Original unit price from the Price List (before any discount) | NO - reset then repopulated on every save at `cart.py:473` |
| **`rate`** | Currency | Final unit price (after discount applied) | YES - shown as "Rate" |
| **`discount_percentage`** | Percent | The % discount applied by the Pricing Rule | NO - reset then repopulated at `cart.py:473` |
| **`discount_amount`** | Currency | Per-unit discount in currency (alternative to %) | NO |
| **`amount`** | Currency | `rate * qty` = line total after discount | YES - shown as subtotal |
| **`is_free_item`** | Check | True if item was added by a "Free Item" pricing rule | YES - shows "FREE" badge |
| **`pricing_rules`** | Small Text | **JSON string** of Pricing Rule document names that were applied to this item, e.g. `'["PRLE-0001"]'` | NO |
| **`net_rate`** | Currency | Rate after any additional per-item discount | NO |
| **`net_amount`** | Currency | `net_rate * qty` | NO |

### Document-Level Fields (Quotation - already populated)

| Field | Type | What It Contains | Currently Used? |
|-------|------|------------------|-----------------|
| **`total`** | Currency | Sum of all `amount` values (item totals before tax) | YES - in footer as "Net Total" |
| **`net_total`** | Currency | Total after additional discounts | YES - in payment summary |
| **`grand_total`** | Currency | Final total including taxes | YES |
| **`discount_amount`** | Currency | Additional discount on the overall total (not per-item) | NO |
| **`additional_discount_percentage`** | Percent | % discount on total | NO |
| **`coupon_code`** | Link | Applied Coupon Code document name | PARTIAL - shown as badge only |
| **`total_qty`** | Float | Total quantity of all items | YES - in payment summary label |
| **`taxes`** | Table | Tax line items | YES |

### Pricing Rule Fields (need to be looked up from `pricing_rules` JSON)

The `pricing_rules` field on each Quotation Item contains a JSON array of Pricing Rule names. Each Pricing Rule document has:

| Field | Type | What It Contains | Purpose for Us |
|-------|------|------------------|---------------|
| **`title`** | Data | Human-readable name (e.g. "Spring GPU Sale") | Display offer name to customer |
| **`valid_from`** | Date | Start date of the offer | Show when offer started |
| **`valid_upto`** | Date | **End date / DEADLINE** of the offer | **URGENCY DISPLAY** - "Offer ends March 1" |
| **`discount_percentage`** | Percent | The discount % this rule applies | Confirm which rule gave what discount |
| **`discount_amount`** | Currency | Fixed discount amount | Alternative to percentage |
| **`pricing_rule_for`** | Select | "Discount Percentage", "Discount Amount", "Rate" | Determines discount type |
| **`free_item`** | Link | Item given free | Identifies free item promos |

---

## Part 2: The Summation System

### How Totals Are Currently Calculated

ERPNext's `calculate_taxes_and_totals()` runs this sequence (standard Quotation logic):

```
For each item:
    if discount_percentage:
        rate = price_list_rate * (1 - discount_percentage/100)
    elif discount_amount:
        rate = price_list_rate - discount_amount
    amount = rate * qty
    net_amount = amount  (unless additional item discount)

total = sum(item.amount for all items)
net_total = total - doc.discount_amount  (if apply_discount_on == "Net Total")
           OR total  (if no additional discount)

For each tax:
    tax_amount calculated on net_total

grand_total = net_total + sum(tax.tax_amount)
              - doc.discount_amount  (if apply_discount_on == "Grand Total")
```

### Our New Summation: "What You Would Have Paid"

We need to compute and display the **pre-discount total** so customers can see savings. The formula:

```
original_total = sum(item.price_list_rate * item.qty for all items where price_list_rate > 0)
savings_total  = original_total - doc.total
```

This is the SAME formula already used in `order_taxes.html` lines 37-43:

```jinja
{% set tot_quotation_discount = [] %}
{%- for item in doc.items -%}
    {% if tot_quotation_discount.append(
        ((item.price_list_rate * item.qty) * item.discount_percentage) / 100
    ) %}{% endif %}
{% endfor %}
{{ tot_quotation_discount | sum }}
```

**Problem with the existing formula:** It only calculates savings from `discount_percentage`. It misses:
- Items with `discount_amount` instead of `discount_percentage`
- Additional document-level `doc.discount_amount`
- Free items (their entire value is a "saving")

### Our Improved Summation Formula

```
Per-item savings:
    if item.is_free_item:
        item_savings = item.price_list_rate * item.qty  (entire value is free)
    elif item.price_list_rate and item.price_list_rate > item.rate:
        item_savings = (item.price_list_rate - item.rate) * item.qty
    else:
        item_savings = 0

total_item_savings = sum(item_savings for all items)

Additional discount savings:
    doc_discount = doc.discount_amount or 0

Grand savings:
    total_savings = total_item_savings + doc_discount

Original subtotal (what you would have paid):
    original_subtotal = sum(item.price_list_rate * item.qty for all non-free items)
                      + sum(item.price_list_rate * item.qty for free items)
```

This is more robust because `price_list_rate - rate` captures all discount types regardless of whether they were percentage-based or amount-based.

---

## Part 3: The Deadline System

### Data Chain for Deadlines

```
Pricing Rule (has valid_upto date)
    ↓ applied during set_price_list_and_item_details()
Quotation Item.pricing_rules = '["PRLE-0001", "PRLE-0002"]'  (JSON string)
    ↓ we parse this in the decorator
decorate_quotation_doc() enriches each item with:
    d.offer_deadlines = [
        {"title": "Spring Sale", "valid_upto": "2026-03-01", "days_left": 10},
        ...
    ]
    ↓ template renders deadline badges
```

### Where the Lookup Happens

We will modify `decorate_quotation_doc()` in `cart.py` (line 333) to also fetch pricing rule metadata:

```python
def decorate_quotation_doc(doc):
    for d in doc.get("items", []):
        # ... existing image/route decoration ...

        # NEW: Enrich with pricing rule deadlines
        d.offer_details = get_offer_details_for_item(d)

    return doc


def get_offer_details_for_item(item):
    """Parse pricing_rules JSON and fetch deadline/title from each Pricing Rule."""
    import json
    offers = []

    if not item.pricing_rules:
        return offers

    try:
        rule_names = json.loads(item.pricing_rules)
    except (json.JSONDecodeError, TypeError):
        return offers

    for rule_name in rule_names:
        rule = frappe.get_cached_doc("Pricing Rule", rule_name)
        offer = {
            "title": rule.title or rule.name,
            "valid_upto": rule.valid_upto,
            "days_left": None,
        }
        if rule.valid_upto:
            from frappe.utils import date_diff, today
            offer["days_left"] = date_diff(rule.valid_upto, today())
        offers.append(offer)

    return offers
```

### Why This is Safe

- `frappe.get_cached_doc()` uses Frappe's document cache - no extra DB hit if the same rule is applied to multiple items
- The `pricing_rules` field is already populated by ERPNext's standard logic - we're just reading it
- If `pricing_rules` is empty or null, we return an empty list - no errors
- Template gracefully skips if `offer_details` is empty

---

## Part 4: File-by-File Change Map

### File 1: `webshop/webshop/shopping_cart/cart.py`

**Function:** `decorate_quotation_doc()` (line 333)

**Current behavior:** Adds `web_item_name`, `thumbnail`, `website_image`, `description`, `route`, `warehouse` to each item.

**Change:** Add `offer_details` list to each item by parsing `pricing_rules` and looking up Pricing Rule `title` and `valid_upto`.

**Impact:** The `doc` object returned by `get_cart_quotation()` will have richer item data. No other callers are affected because this only adds new attributes.

---

### File 2: `templates/includes/cart/cart_items.html`

**Current `item_subtotal` macro (lines 3-18):**
```jinja
{% macro item_subtotal(item) %}
    <div>{{ item.get_formatted('amount') }}</div>
    {% if item.is_free_item %}
        <span class="free-tag">FREE</span>
    {% else %}
        <span class="item-rate">Rate: {{ item.get_formatted('rate') }}</span>
    {% endif %}
{% endmacro %}
```

**Proposed new macro:**
```jinja
{% macro item_subtotal(item) %}
    {# Strike-through original price if discounted #}
    {% if not item.is_free_item and item.price_list_rate and item.price_list_rate != item.rate %}
        <div class="original-price text-muted small">
            <span style="text-decoration: line-through;">
                {{ item.get_formatted('price_list_rate') }}
            </span>
            <span class="badge badge-success ml-1">
                -{{ item.discount_percentage | int }}%
            </span>
        </div>
    {% endif %}

    {# Current total #}
    <div>{{ item.get_formatted('amount') }}</div>

    {# Rate or FREE badge #}
    {% if item.is_free_item %}
        <div class="text-success mt-1"><span class="free-tag">{{ _('FREE') }}</span></div>
    {% else %}
        <span class="item-rate">{{ _('Rate:') }} {{ item.get_formatted('rate') }}</span>
    {% endif %}

    {# Per-item savings #}
    {% if not item.is_free_item and item.price_list_rate and item.price_list_rate > item.rate %}
        {% set line_savings = (item.price_list_rate - item.rate) * item.qty %}
        <div class="text-success small mt-1">
            {{ _('You save') }} {{ frappe.utils.fmt_money(line_savings, currency=doc.currency) }}
        </div>
    {% endif %}

    {# Offer deadline badges #}
    {% if item.offer_details %}
        {% for offer in item.offer_details %}
            {% if offer.valid_upto %}
                {% if offer.days_left is not none and offer.days_left <= 0 %}
                    <div class="text-danger small mt-1 font-weight-bold">
                        {{ _('Offer ends today!') }}
                    </div>
                {% elif offer.days_left is not none and offer.days_left <= 7 %}
                    <div class="text-danger small mt-1">
                        {{ _('Only') }} {{ offer.days_left }} {{ _('days left!') }}
                    </div>
                {% elif offer.days_left is not none and offer.days_left <= 14 %}
                    <div class="text-warning small mt-1">
                        {{ _('Offer ends') }} {{ frappe.utils.formatdate(offer.valid_upto) }}
                    </div>
                {% else %}
                    <div class="text-muted small mt-1">
                        {{ _('Offer until') }} {{ frappe.utils.formatdate(offer.valid_upto) }}
                    </div>
                {% endif %}
            {% endif %}
            {% if offer.title %}
                <div class="text-info small">{{ offer.title }}</div>
            {% endif %}
        {% endfor %}
    {% endif %}
{% endmacro %}
```

**Fields targeted:**
- `item.price_list_rate` - original price (strikethrough)
- `item.rate` - discounted price (current display, unchanged)
- `item.discount_percentage` - shown as badge "-20%"
- `item.amount` - line total (current display, unchanged)
- `item.is_free_item` - FREE badge (current, unchanged)
- `item.offer_details[].valid_upto` - deadline date
- `item.offer_details[].days_left` - computed days remaining
- `item.offer_details[].title` - offer name

---

### File 3: `templates/includes/cart/cart_payment_summary.html`

**Current structure (lines 11-31):**
```
Net Total (X Items) .............. $XXX.XX
Tax A ............................ $XX.XX
Tax B ............................ $XX.XX
------
Grand Total ...................... $XXX.XX
```

**Proposed new structure:**
```
Subtotal (before discounts) ...... $XXX.XX  (strikethrough, muted)
Your Savings ..................... -$XX.XX  (green)
Net Total (X Items) .............. $XXX.XX
[Additional Discount ............. -$XX.XX] (if doc.discount_amount)
Tax A ............................ $XX.XX
Tax B ............................ $XX.XX
------
Grand Total ...................... $XXX.XX
```

**Summation logic (Jinja):**
```jinja
{# Compute original total and savings #}
{% set original_amounts = [] %}
{% set savings_amounts = [] %}
{% for item in doc.items %}
    {% if item.price_list_rate and item.price_list_rate > 0 %}
        {% if original_amounts.append(item.price_list_rate * item.qty) %}{% endif %}
    {% else %}
        {% if original_amounts.append(item.rate * item.qty) %}{% endif %}
    {% endif %}

    {% if item.is_free_item and item.price_list_rate %}
        {% if savings_amounts.append(item.price_list_rate * item.qty) %}{% endif %}
    {% elif item.price_list_rate and item.price_list_rate > item.rate %}
        {% if savings_amounts.append((item.price_list_rate - item.rate) * item.qty) %}{% endif %}
    {% endif %}
{% endfor %}

{% set original_total = original_amounts | sum %}
{% set total_savings = savings_amounts | sum %}
{% set has_any_discount = total_savings > 0 or doc.discount_amount %}
```

**Fields targeted:**
- `item.price_list_rate` - per-item original price for summing
- `item.rate` - per-item discounted price
- `item.qty` - quantity multiplier
- `item.is_free_item` - includes free item value in savings
- `doc.net_total` - current net total (unchanged)
- `doc.discount_amount` - additional discount on total (new row)
- `doc.additional_discount_percentage` - alternative to amount (new row)
- `doc.taxes[].tax_amount` - tax lines (unchanged)
- `doc.grand_total` - final total (unchanged)

---

### File 4: `templates/includes/cart/cart_items_total.html`

**Current (shows only `doc.total`):**
```jinja
<th>{{ _("Net Total") }}</th>
<th>{{ doc.get_formatted("total") }}</th>
```

**Proposed (show original total if savings exist):**
```jinja
{% if has_any_discount %}
<tr>
    <th></th>
    <th class="text-left text-muted">
        <span style="text-decoration: line-through;">{{ _("Was") }}</span>
    </th>
    <th class="text-left text-muted totals" style="text-decoration: line-through;">
        {{ frappe.utils.fmt_money(original_total, currency=doc.currency) }}
    </th>
</tr>
{% endif %}
<tr>
    <th></th>
    <th class="text-left item-grand-total">{{ _("Net Total") }}</th>
    <th class="text-left item-grand-total totals">{{ doc.get_formatted("total") }}</th>
</tr>
```

**Problem:** This template is rendered independently from `cart_payment_summary.html`, so it doesn't share the computed `original_total` / `has_any_discount` variables. We'll need to either:
- Duplicate the computation in this template, OR
- Move the computation to `decorate_quotation_doc()` and add `doc.original_total` and `doc.total_savings` as computed fields

**Recommendation:** Add computed fields to the doc in the decorator. This is cleaner.

---

### File 5: `webshop/webshop/shopping_cart/cart.py` (additional change)

Add computed summary fields in `decorate_quotation_doc()`:

```python
def decorate_quotation_doc(doc):
    original_total = 0
    total_savings = 0

    for d in doc.get("items", []):
        # ... existing decoration ...
        d.offer_details = get_offer_details_for_item(d)

        # Compute savings
        plr = flt(d.price_list_rate) or flt(d.rate)
        if d.is_free_item and d.price_list_rate:
            total_savings += flt(d.price_list_rate) * flt(d.qty)
        elif d.price_list_rate and flt(d.price_list_rate) > flt(d.rate):
            total_savings += (flt(d.price_list_rate) - flt(d.rate)) * flt(d.qty)
        original_total += plr * flt(d.qty)

    doc.original_total = original_total
    doc.total_savings = total_savings
    doc.has_any_discount = total_savings > 0 or flt(doc.discount_amount) > 0

    return doc
```

This way ALL templates can use `doc.original_total`, `doc.total_savings`, `doc.has_any_discount` without recomputing.

---

### File 6: `public/scss/webshop_cart.scss`

Add styles for:
```scss
.original-price {
    font-size: 0.85em;
}

.badge-success {
    // discount percentage badge
    font-size: 0.75em;
    padding: 2px 6px;
}

.offer-deadline-urgent {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}
```

---

## Part 5: What We Do NOT Need to Change

| Component | Why No Change Needed |
|-----------|---------------------|
| `set_price_list_and_rate()` | Already resets and repopulates `price_list_rate`, `discount_percentage` on every save |
| `apply_cart_settings()` | Already calls `calculate_taxes_and_totals()` which does all the math |
| `update_cart()` | Already re-renders all three template fragments on AJAX update |
| ERPNext Pricing Rules | Standard feature - we just read the results |
| ERPNext Quotation DocType | All fields we need already exist on the standard DocType |
| `shopping_cart.js` | AJAX update already replaces `.cart-items`, `.cart-tax-items`, `.payment-summary` |
| `cart.js` | No changes needed - existing event bindings work with new template content |

---

## Part 6: Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| `price_list_rate` is 0 or null for some items | Medium | Guard with `{% if item.price_list_rate and item.price_list_rate > 0 %}` |
| `pricing_rules` JSON is malformed | Low | Wrap in try/except, return empty list |
| Pricing Rule deleted but still referenced in old Quotation | Low | Use `frappe.db.exists()` check before `get_cached_doc()` |
| Performance hit from looking up Pricing Rules in decorator | Low | `get_cached_doc()` uses Frappe cache; typical cart has <10 items |
| `discount_percentage` is 0 but `discount_amount` is set | Medium | Use `price_list_rate - rate` comparison instead of `discount_percentage` alone |
| Free items with no `price_list_rate` | Medium | Skip savings calculation for free items without `price_list_rate` |
| Multiple pricing rules per item | Medium | Show all offer details; sum savings using `price_list_rate - rate` which is the net effect |

---

## Part 7: Verification Checklist

After implementation, verify each scenario:

| # | Scenario | Check |
|---|----------|-------|
| 1 | Item with percentage discount | Shows ~~$100~~ $80 (-20%), "You save $20" |
| 2 | Item with amount discount | Shows ~~$100~~ $85, "You save $15" |
| 3 | Item with no discount | Shows $100 only, no strikethrough, no badge |
| 4 | Free item from pricing rule | Shows "FREE" badge, value counted in savings |
| 5 | Coupon code applied | Savings row in payment summary reflects coupon |
| 6 | Offer expiring in 3 days | Red text "Only 3 days left!" |
| 7 | Offer expiring in 10 days | Warning text "Offer ends March 1, 2026" |
| 8 | Offer with no deadline | No deadline shown, discount still visible |
| 9 | Multiple offers on one item | All offer titles/deadlines listed |
| 10 | Additional discount on total | "Additional Discount -$50" row in payment summary |
| 11 | Cart with mixed discounted/non-discounted items | Only discounted items show strikethrough |
| 12 | AJAX qty update | All discount info re-renders correctly |
| 13 | Mobile responsive | Discount badges readable on small screens |
| 14 | `price_list_rate` is null | Falls back to showing `rate` only, no error |

---

## Summary

**What we're doing:** Reading 4 hidden Quotation Item fields (`price_list_rate`, `discount_percentage`, `pricing_rules`, `is_free_item`) + 2 hidden Quotation fields (`discount_amount`, `additional_discount_percentage`) that ERPNext already populates, and displaying them in 4 template files + 1 Python decorator.

**What we're NOT doing:** No new DocTypes, no pricing engine changes, no database migrations, no JS logic changes. The AJAX update cycle already re-renders all affected templates.

**Files touched:** 6 total (1 Python, 4 HTML templates, 1 SCSS)

**New data flow:**
```
ERPNext Pricing Engine (unchanged)
    ↓ populates on every cart save
Quotation Item fields: price_list_rate, discount_percentage, pricing_rules
    ↓ read by
decorate_quotation_doc() → adds offer_details[], original_total, total_savings
    ↓ passed to
Jinja templates → render strikethrough prices, savings, deadlines
    ↓ displayed in
Cart UI → customer sees the value they're getting
```
