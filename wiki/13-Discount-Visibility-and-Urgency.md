# Discount Visibility & Offer Urgency

## Goal

Make discounts, promotions, and offer deadlines clearly visible to customers throughout the shopping experience - from product browsing to cart to checkout - creating transparency and a sense of urgency.

---

## Feature: Per-Item Discount Display in Cart

### What to Show per Line Item

```
+-----------------------------------------------------------------+
| [IMG] Server RAM DDR5 32GB                          Qty: 2      |
|       SKU: RAM-DDR5-32GB                                        |
|                                                                 |
|       Was: $149.99  (strikethrough)                             |
|       Now: $119.99  (-20%)                                      |
|       You save: $60.00 on this item                             |
|                                                   Total: $239.98|
+-----------------------------------------------------------------+
```

### Data Source (all on Quotation Item already)
- `price_list_rate` = $149.99 (original)
- `rate` = $119.99 (after discount)
- `discount_percentage` = 20%
- `amount` = $239.98

---

## Feature: Offer Deadline / Urgency Display

### Where Deadline Data Lives

ERPNext **Pricing Rule** has these date fields:
- `valid_from` - Start date of the offer
- `valid_upto` - End date of the offer (THIS IS THE DEADLINE)

The `pricing_rules` field on each Quotation Item contains the names of applied pricing rules (JSON string).

### How to Surface Deadlines

1. When rendering cart items, parse the `pricing_rules` field
2. Look up the Pricing Rule document(s)
3. If `valid_upto` exists, display it as an urgency indicator

### Proposed UI

```
+-----------------------------------------------------------------+
| [IMG] GPU RTX 4090                                  Qty: 1      |
|       SKU: GPU-RTX4090                                          |
|                                                                 |
|       Was: $1,599.00                                            |
|       Now: $1,279.20  (-20%)                                    |
|                                                                 |
|       [clock icon] Offer ends: March 1, 2026 (10 days left)    |
|       [tag icon]   "Spring GPU Sale"                            |
|                                                   Total: $1,279.20|
+-----------------------------------------------------------------+
```

### Urgency Levels

| Days Remaining | Display Style |
|---------------|---------------|
| > 14 days | Green text, informational |
| 7-14 days | Yellow/orange badge: "Ends soon" |
| 1-7 days | Red badge: "Only X days left!" |
| < 24 hours | Red pulsing: "Ends today!" |
| Expired | Remove discount, recalculate |

### Implementation: Backend Helper

```python
# New utility function to get discount details for cart display
@frappe.whitelist()
def get_cart_discount_details(quotation_name):
    """Returns discount and deadline info for each cart item."""
    doc = frappe.get_doc("Quotation", quotation_name)
    discount_details = []

    for item in doc.items:
        detail = {
            "item_code": item.item_code,
            "price_list_rate": item.price_list_rate,
            "rate": item.rate,
            "discount_percentage": item.discount_percentage,
            "discount_amount": item.discount_amount,
            "is_free_item": item.is_free_item,
            "savings": (item.price_list_rate - item.rate) * item.qty,
            "offers": []
        }

        # Parse applied pricing rules
        if item.pricing_rules:
            import json
            rule_names = json.loads(item.pricing_rules)
            for rule_name in rule_names:
                rule = frappe.get_cached_doc("Pricing Rule", rule_name)
                offer = {
                    "rule_name": rule.name,
                    "title": rule.title or rule.name,
                    "valid_from": rule.valid_from,
                    "valid_upto": rule.valid_upto,
                    "discount_percentage": rule.discount_percentage,
                    "discount_amount": rule.discount_amount,
                }
                if rule.valid_upto:
                    from frappe.utils import date_diff, today
                    offer["days_remaining"] = date_diff(rule.valid_upto, today())
                detail["offers"].append(offer)

        discount_details.append(detail)

    return discount_details
```

### Implementation: Template Changes

In `cart_items.html`, within the `item_subtotal` macro:

```jinja
{% macro item_subtotal(item) %}
    {# Original price with strikethrough if discounted #}
    {% if item.price_list_rate and item.price_list_rate != item.rate and not item.is_free_item %}
        <div class="original-price">
            <span class="text-muted" style="text-decoration: line-through;">
                {{ item.get_formatted('price_list_rate') }}
            </span>
            <span class="discount-badge badge badge-success ml-1">
                -{{ item.discount_percentage | int }}%
            </span>
        </div>
    {% endif %}

    {# Current price #}
    <div>{{ item.get_formatted('amount') }}</div>

    {# Rate per unit #}
    {% if item.is_free_item %}
        <div class="text-success mt-1"><span class="free-tag">{{ _('FREE') }}</span></div>
    {% else %}
        <span class="item-rate">{{ _('Rate:') }} {{ item.get_formatted('rate') }}</span>
    {% endif %}

    {# Per-item savings #}
    {% if item.price_list_rate and item.price_list_rate != item.rate and not item.is_free_item %}
        {% set savings = (item.price_list_rate - item.rate) * item.qty %}
        <div class="text-success small mt-1">
            {{ _('You save:') }} {{ frappe.utils.fmt_money(savings, currency=doc.currency) }}
        </div>
    {% endif %}

    {# Offer deadline (requires pricing_rules lookup) #}
    {# This would need to be passed via decorate_quotation_doc or a separate call #}
{% endmacro %}
```

---

## Feature: Payment Summary with Savings

In `cart_payment_summary.html`:

```jinja
<table class="table w-100">
    {# Original subtotal (before discounts) #}
    {% set original_total = [] %}
    {% for item in doc.items %}
        {% if original_total.append(item.price_list_rate * item.qty) %}{% endif %}
    {% endfor %}
    {% set original_sum = original_total | sum %}
    {% set total_savings = original_sum - doc.net_total %}

    {% if total_savings > 0 %}
    <tr>
        <td class="bill-label text-muted">
            <span style="text-decoration: line-through;">{{ _("Subtotal") }}</span>
        </td>
        <td class="text-right text-muted" style="text-decoration: line-through;">
            {{ frappe.utils.fmt_money(original_sum, currency=doc.currency) }}
        </td>
    </tr>
    <tr class="text-success">
        <td class="bill-label">{{ _("Your Savings") }}</td>
        <td class="text-right">
            -{{ frappe.utils.fmt_money(total_savings, currency=doc.currency) }}
        </td>
    </tr>
    {% endif %}

    <tr>
        <td class="bill-label">{{ _("Net Total") }} ({{ doc.total_qty | int }} {{ _("Items") }})</td>
        <td class="text-right">{{ doc.get_formatted("net_total") }}</td>
    </tr>

    {# Taxes #}
    {% for d in doc.taxes %}
        {% if d.tax_amount %}
        <tr>
            <td class="bill-label">{{ d.description }}</td>
            <td class="text-right">{{ d.get_formatted("tax_amount") }}</td>
        </tr>
        {% endif %}
    {% endfor %}

    {# Additional discount on total #}
    {% if doc.discount_amount %}
    <tr class="text-success">
        <td class="bill-label">{{ _("Additional Discount") }}</td>
        <td class="text-right">-{{ doc.get_formatted("discount_amount") }}</td>
    </tr>
    {% endif %}
</table>

<table class="table w-100 grand-total mt-6">
    <tr>
        <td class="bill-content net-total">{{ _("Grand Total") }}</td>
        <td class="bill-content net-total text-right">{{ doc.get_formatted("grand_total") }}</td>
    </tr>
</table>
```

---

## Feature: Product Page Offer Display

On individual product pages, show active offers:

```
+-----------------------------------------------+
|  GPU RTX 4090                                 |
|                                               |
|  Was: $1,599.00                               |
|  Now: $1,279.20                               |
|                                               |
|  [SPRING GPU SALE - 20% OFF]                  |
|  [clock] Offer ends March 1, 2026            |
|  [bar] Only 10 days left!                     |
|                                               |
|  [Add to Cart]                                |
+-----------------------------------------------+
```

---

## Sample Test Scenarios

### Scenario 1: Percentage Discount with Deadline
- Product: "DDR5 RAM 32GB" at $149.99
- Pricing Rule: 20% off, valid_upto = March 15, 2026
- Cart should show: ~~$149.99~~ $119.99 (-20%), "Offer ends March 15" (24 days)

### Scenario 2: Coupon Code Discount
- Product: "1TB NVMe SSD" at $89.99
- Coupon "SAVE15" for 15% off
- Cart should show: ~~$89.99~~ $76.49 (-15%), coupon badge

### Scenario 3: Free Item Promotion
- Buy 2x "Cat6 Network Cable", get 1 free
- Cart should show: 2x at $12.99, 1x FREE, savings = $12.99

### Scenario 4: Bundle/System Discount (future)
- Complete server build: $2,500
- System builder bundle discount: 5%
- Cart should show: original total, -5% bundle discount, final price

### Scenario 5: Expiring Today
- Product: "USB Hub" at $29.99
- Flash sale: 40% off, valid_upto = today
- Cart should show: ~~$29.99~~ $17.99, RED "Offer ends TODAY!"

### Scenario 6: Multiple Overlapping Offers
- Product qualifies for both "Brand Sale 10%" and "Category Sale 15%"
- ERPNext applies the better rule (or both, depending on config)
- Cart should show the effective discount and list active offers

---

## Related Wiki Pages

- [14 - Hypothesis: Discount & Deadline Visibility](14-Hypothesis-Discount-Deadline-Visibility.md) - Exact implementation plan with field targeting, formulas, and code
- [10 - Feature Gap: Cart Discounts](10-Feature-Gap-Cart-Discounts.md) - Root cause analysis of why discounts are hidden
- [06 - Pricing & Discounts](06-Pricing-and-Discounts.md) - How the pricing stack works
- [03 - Shopping Cart & Quotation Deep Dive](03-Shopping-Cart-Quotation-Deep-Dive.md) - Field-level mapping of cart to Quotation
- [12 - Staging Sandbox](12-Staging-Sandbox-Deployment.md) - Test environment setup including sample pricing rules
- [Back to Home](00-Home.md)
