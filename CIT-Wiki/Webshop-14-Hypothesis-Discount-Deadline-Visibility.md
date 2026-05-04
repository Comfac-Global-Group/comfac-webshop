# 14 - Hypothesis: Making Discounts and Deadlines Visible

**Parent:** [Webshop Index](Webshop-Index)  
**Previous:** [13 - Discount Visibility & Urgency](Webshop-13-Discount-Visibility-and-Urgency)  
**Source:** [Comfac Webshop Wiki - Chapter 14](https://github.com/Comfac-Global-Group/comfac-webshop/wiki/14-Hypothesis-Discount-Deadline-Visibility)

---

## Prerequisite: Seamless Baseline First

**This hypothesis is NOT to be executed until the comfac-webshop fork runs seamlessly as a drop-in replacement on a production-like ERPNext instance.**

**Execution order:**

1. **Phase 0 (Staging Sandbox):** Clone the production ERPNext instance, install comfac-webshop, validate it works identically to the existing webshop. No feature changes. Pass all validation checks.

2. **Phase 1 (Experiment Clone):** Once Phase 0 is proven stable, clone THAT successful staging instance into a second sandbox. This is where we implement and test the hypothesis below.

3. **Phase 2 (Iterate):** Test with sample products, pricing rules, coupons, and deadline-bearing offers on the experiment clone. Validate every scenario. Only when everything passes do we merge back to the main fork.

**Do not skip Phase 0.**

## Core Thesis

**All the data we need already exists on the Quotation document.** ERPNext's pricing engine populates discount fields on every cart save. We do not need to change the backend calculation logic. We need to:

1. **Surface existing hidden fields** in the cart templates
2. **Enrich the decorator** to pass pricing rule metadata (deadlines, titles) to the frontend
3. **Add summation logic** in the payment summary template
4. **Style it** so customers immediately see value and urgency

## Part 1: The Fields We Will Target

### Per-Item Fields (Quotation Item - already populated)

| Field | Type | What It Contains | Currently Used? |
|-------|------|------------------|-----------------|
| `price_list_rate` | Currency | Original unit price from the Price List (before any discount) | **NO** |
| `rate` | Currency | Final unit price (after discount applied) | YES |
| `discount_percentage` | Percent | The % discount applied by the Pricing Rule | **NO** |
| `discount_amount` | Currency | Per-unit discount in currency | **NO** |
| `amount` | Currency | `rate * qty` = line total after discount | YES |
| `is_free_item` | Check | True if item was added by a "Free Item" pricing rule | YES |
| `pricing_rules` | Small Text | **JSON string** of Pricing Rule document names | **NO** |

### Document-Level Fields (Quotation - already populated)

| Field | Type | What It Contains | Currently Used? |
|-------|------|------------------|-----------------|
| `total` | Currency | Sum of all `amount` values (item totals before tax) | YES |
| `net_total` | Currency | Total after additional discounts | YES |
| `grand_total` | Currency | Final total with taxes | YES |
| `discount_amount` | Currency | Additional discount on the overall total | **NO** |
| `additional_discount_percentage` | Percent | % discount on total | **NO** |
| `coupon_code` | Link | Applied Coupon Code document name | PARTIAL |

### Pricing Rule Fields (need to be looked up from pricing_rules JSON)

| Field | Type | What It Contains | Purpose for Us |
|-------|------|------------------|----------------|
| `title` | Data | Human-readable name (e.g., "Spring GPU Sale") | Display offer name |
| `valid_from` | Date | Start date of the offer | Show when offer started |
| `valid_upto` | Date | **End date / DEADLINE** of the offer | **URGENCY DISPLAY** |
| `discount_percentage` | Percent | The discount % this rule applies | Confirm which rule gave what discount |

## Part 2: The Summation System

### Improved Summation Formula

```python
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
```

## Part 3: The Deadline System

### Data Chain for Deadlines

```
Pricing Rule (has valid_upto date)
    ↓ applied during set_price_list_and_item_details()
Quotation Item.pricing_rules = '["PRLE-0001", "PRLE-0002"]'  (JSON string)
    ↓ we parse this in the decorator
decorate_quotation_doc() enriches each item with:
    d.offer_details = [
        {"title": "Spring Sale", "valid_upto": "2026-03-01", "days_left": 10},
        ...
    ]
    ↓ template renders deadline badges
```

### Backend Helper

```python
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

## Part 4: File-by-File Change Map

### File 1: `webshop/webshop/shopping_cart/cart.py`

**Function:** `decorate_quotation_doc()`

**Change:** Add `offer_details` list to each item. Also compute and add `doc.original_total`, `doc.total_savings`, `doc.has_any_discount`.

### File 2: `templates/includes/cart/cart_items.html`

**Macro:** `item_subtotal`

**Change:** Add strike-through original price when discounted, discount percentage badge, "You save" amount, and offer deadline badges.

### File 3: `templates/includes/cart/cart_payment_summary.html`

**Change:** Add original subtotal (struck through) if discounts exist, savings row, and additional discount row.

### File 4: `templates/includes/cart/cart_items_total.html`

**Change:** Show original total (struck through) if `doc.has_any_discount`.

### File 5: `public/scss/webshop_cart.scss`

**Change:** Add styles for discount badges, strikethrough, and urgency indicators.

## Part 5: What We Do NOT Need to Change

| Component | Why No Change Needed |
|-----------|---------------------|
| `set_price_list_and_rate()` | Already resets and repopulates fields on every save |
| `apply_cart_settings()` | Already calls `calculate_taxes_and_totals()` which does all the math |
| `update_cart()` | Already re-renders all three template fragments on AJAX update |
| ERPNext Pricing Rules | Standard feature - we just read the results |
| ERPNext Quotation DocType | All fields we need already exist |
| `shopping_cart.js` | AJAX update already replaces affected DOM elements |

## Part 6: Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `price_list_rate` is 0 or null | Medium | Guard with `{% if item.price_list_rate and item.price_list_rate > 0 %}` |
| `pricing_rules` JSON malformed | Low | Wrap in try/except, return empty list |
| Pricing Rule deleted but referenced | Low | Use `frappe.db.exists()` check |
| Performance hit from lookups | Low | `get_cached_doc()` uses Frappe cache |
| `discount_percentage` is 0 but `discount_amount` is set | Medium | Use `price_list_rate - rate` comparison |
| Free items with no `price_list_rate` | Medium | Skip savings calculation for these |
| Multiple pricing rules per item | Medium | Show all offer details; sum net savings |

## Part 7: Verification Checklist

| # | Scenario | Check |
|---|----------|-------|
| 1 | Item with percentage discount | Shows $100 → $80 (-20%), "You save $20" |
| 2 | Item with amount discount | Shows $100 → $85, "You save $15" |
| 3 | Item with no discount | Shows $100 only, no strikethrough |
| 4 | Free item from pricing rule | Shows "FREE" badge, value in savings |
| 5 | Coupon code applied | Savings row reflects coupon |
| 6 | Offer expiring in 3 days | Red text "Only 3 days left!" |
| 7 | Offer expiring in 10 days | Warning text "Offer ends March 1, 2026" |
| 8 | Offer with no deadline | No deadline shown, discount visible |
| 9 | Multiple offers on one item | All offer titles/deadlines listed |
| 10 | Additional discount on total | "Additional Discount -$50" row |
| 11 | Cart with mixed items | Only discounted items show strikethrough |
| 12 | AJAX qty update | All discount info re-renders |
| 13 | Mobile view | Discount badges readable |
| 14 | `price_list_rate` is null | Falls back showing rate only |

## Summary

**What we're doing:** Reading 4 hidden Quotation Item fields (`price_list_rate`, `discount_percentage`, `pricing_rules`, `is_free_item`) + 2 hidden Quotation fields (`discount_amount`, `additional_discount_percentage`) that ERPNext already populates, and displaying them in 4 template files + 1 Python decorator.

**What we're NOT doing:** No new DocTypes, no pricing engine changes, no database migrations, no JS logic changes. The AJAX update cycle already re-renders all affected templates.

**Files touched:** 5 total (1 Python, 3 HTML templates, 1 SCSS)

---

**Navigation:** [Webshop Index](Webshop-Index) | [Previous: 13 - Discount Visibility](Webshop-13-Discount-Visibility-and-Urgency) | [Webshop Index](Webshop-Index)
