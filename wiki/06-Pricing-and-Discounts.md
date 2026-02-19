# Pricing & Discounts

## Pricing Stack (ERPNext standard, used by webshop)

### 1. Price List
- Base prices stored in **Item Price** linked to a **Price List**
- Webshop uses the Price List configured in Webshop Settings (or customer-specific)
- `_set_price_list()` in cart.py selects the correct price list

### 2. Pricing Rules
- ERPNext's **Pricing Rule** doctype handles discounts
- Applied automatically during `set_price_list_and_item_details()`
- Types: Discount Percentage, Discount Amount, Rate, Product (free items)
- Can be based on: item, item group, customer, qty, date range, etc.

### 3. Coupon Codes
- **Coupon Code** doctype links to a Pricing Rule
- Applied via `apply_coupon_code()` in cart.py
- Sets `quotation.coupon_code` and `quotation.ignore_pricing_rule = 0`
- Removed via `remove_coupon_code()` which resets discount fields

### 4. Tax Calculation
- **Sales Taxes and Charges Template** applied via `set_taxes()`
- Based on territory, customer group, tax category
- Appended to quotation.taxes child table

## Where Discounts Are Calculated

In `apply_cart_settings()`:
```python
set_price_list_and_rate(quotation, cart_settings)  # resets and refetches prices
quotation.run_method("calculate_taxes_and_totals")  # ERPNext standard calculation
set_taxes(quotation, cart_settings)                  # applies tax template
```

`set_price_list_and_rate()` explicitly resets item rates:
```python
for item in quotation.get("items"):
    item.price_list_rate = item.discount_percentage = item.rate = item.amount = None
quotation.run_method("set_price_list_and_item_details")  # refetches everything
```

This means ALL pricing rules are re-evaluated on every cart save.

## Where Discounts Are Visible vs Hidden

| Location | Discount Visible? | Details |
|----------|-------------------|---------|
| Product page | Partial | Shows `formatted_price` only (final price) |
| Cart items | NO | Shows `rate` and `amount` only, no original price |
| Cart payment summary | NO | Shows net_total, taxes, grand_total - no savings |
| Order taxes template | YES (coupon only) | Shows "Savings" row calculated from `price_list_rate * discount_percentage` |
| Quotation print format | YES | ERPNext standard shows full pricing breakdown |
| ERPNext desk view | YES | Full Quotation with all fields visible |

## The Discount Display Gap

### What the customer sees in cart:
```
Item A          Qty: 2     $80.00
Item B          Qty: 1     $45.00
---
Net Total: $125.00
Tax:        $12.50
Grand Total: $137.50
```

### What the Quotation actually contains:
```
Item A  price_list_rate: $50  discount: 20%  rate: $40  qty: 2  amount: $80
Item B  price_list_rate: $50  discount: 10%  rate: $45  qty: 1  amount: $45
---
Net Total: $125.00
Discount Amount: $0 (additional_discount_percentage: 0%)
Tax: $12.50
Grand Total: $137.50
Total Savings: $25.00
```

The customer never sees the $25 in savings or the per-item discounts.

## Relevant Fields on Quotation Item

```
price_list_rate     -> Original price from Price List
discount_percentage -> Discount % from pricing rule
discount_amount     -> Per-unit discount in currency
rate                -> Final unit price (after discount)
amount              -> rate * qty
net_rate            -> After any additional item discount
net_amount          -> qty * net_rate
is_free_item        -> True if added by "Product" type pricing rule
pricing_rules       -> JSON string of applied Pricing Rule names
```

---

## Related Wiki Pages

- [03 - Shopping Cart & Quotation Deep Dive](03-Shopping-Cart-Quotation-Deep-Dive.md) - Which of these fields the cart currently shows vs hides
- [10 - Feature Gap: Cart Discounts](10-Feature-Gap-Cart-Discounts.md) - Root cause analysis of the discount display gap
- [13 - Discount Visibility & Urgency](13-Discount-Visibility-and-Urgency.md) - UI specs for showing discounts and deadlines
- [14 - Hypothesis: Discount & Deadline Visibility](14-Hypothesis-Discount-Deadline-Visibility.md) - Exact fields to target and summation formulas
- [12 - Staging Sandbox](12-Staging-Sandbox-Deployment.md) - Setting up test pricing rules and coupons
- [Back to Home](00-Home.md)
