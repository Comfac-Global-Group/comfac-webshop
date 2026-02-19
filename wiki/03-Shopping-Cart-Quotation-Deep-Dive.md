# Shopping Cart & Quotation Deep Dive

## How the Cart IS a Quotation

The webshop has no separate "cart" data model. The shopping cart IS an ERPNext **Quotation** document with `order_type = "Shopping Cart"` and `docstatus = 0` (Draft).

When a user visits `/cart`, this is what happens:

```
cart.py (template controller)
  -> get_cart_quotation()
       -> _get_cart_quotation(party)  # finds or creates the Quotation
       -> decorate_quotation_doc(doc) # adds web-specific fields (thumbnail, route, etc.)
       -> returns { doc, shipping_addresses, billing_addresses, shipping_rules, cart_settings }
```

The entire `doc` object passed to the Jinja templates IS the Quotation document.

---

## Data Flow: What the Cart UI Reads from the Quotation

### Page Load (cart.py -> cart.html)

The `/cart` page calls `get_cart_quotation()` which returns a context dict with:

| Context Key | Source | Description |
|-------------|--------|-------------|
| `doc` | Quotation document | The full quotation with all fields |
| `doc.items` | Quotation Item child table | Line items in the cart |
| `cart_settings` | Webshop Settings singleton | Controls what's shown (prices, checkout, etc.) |
| `shipping_addresses` | Customer's Address records | Shipping address options |
| `billing_addresses` | Customer's Address records | Billing address options |
| `shipping_rules` | Shipping Rule doctype | Available shipping options |

### Template Breakdown: What Each Section Displays

#### 1. Cart Items Table (`cart_items.html`)
**Source file:** `templates/includes/cart/cart_items.html`

For each `d in doc.items` (Quotation Item), displays:

| Displayed | Quotation Item Field | Notes |
|-----------|---------------------|-------|
| Product image | `d.thumbnail` | Added by `decorate_quotation_doc()` from Website Item |
| Item name | `d.web_item_name` or `d.item_name` | web_item_name added by decorator |
| Item code | `d.item_code` | Direct from Quotation Item |
| Variant link | looked up via `frappe.db.get_value('Item', d.item_code, 'variant_of')` | Runtime DB query in template |
| Additional notes | `d.additional_notes` | Custom field on Quotation Item |
| Quantity | `d.qty` (formatted) | Editable input |
| Subtotal | `d.amount` (formatted) | `item.get_formatted('amount')` |
| Rate | `d.rate` (formatted) | Only shown if NOT a free item |
| Free item badge | `d.is_free_item` | From pricing rules |

**CRITICAL GAP:** The cart items template shows `rate` and `amount` but does NOT show:
- `d.price_list_rate` (original price before discount)
- `d.discount_percentage` (the discount applied)
- `d.discount_amount` (monetary discount)
- `d.pricing_rules` (which pricing rules were applied)
- Strike-through original price
- Any "you save X%" messaging

#### 2. Cart Items Total (`cart_items_total.html`)
**Source file:** `templates/includes/cart/cart_items_total.html`

| Displayed | Quotation Field | Notes |
|-----------|----------------|-------|
| Net Total | `doc.total` (formatted) | Sum of all item amounts (pre-tax) |

**What's NOT shown:**
- `doc.discount_amount` (additional discount on total)
- `doc.additional_discount_percentage`
- Any per-item discount breakdown

#### 3. Payment Summary (`cart_payment_summary.html`)
**Source file:** `templates/includes/cart/cart_payment_summary.html`

| Displayed | Quotation Field | Notes |
|-----------|----------------|-------|
| Net Total (X Items) | `doc.net_total` + `doc.total_qty` | Header row |
| Tax rows | `doc.taxes[].description` + `doc.taxes[].tax_amount` | Each tax line |
| Grand Total | `doc.grand_total` | Final total |

**What's NOT shown (but EXISTS on the Quotation):**
- `doc.discount_amount`
- `doc.additional_discount_percentage`
- Per-item discount_percentage
- Per-item price_list_rate vs rate comparison
- Coupon code display (commented out TODO in template)
- Savings calculation

#### 4. Coupon Code Section (in cart.html)
**Source file:** `templates/includes/cart/coupon_code.html`

| Displayed | Quotation Field | Notes |
|-----------|----------------|-------|
| Coupon code badge | `doc.coupon_code` | Shows applied code with remove button |
| Coupon input | N/A | Text input for entering new codes |

The coupon section IS implemented but there's no savings/discount display associated with it in the cart.

#### 5. Address Section (`cart_address.html`)

| Displayed | Quotation Field | Notes |
|-----------|----------------|-------|
| Shipping address | `doc.shipping_address_name` | Selected shipping address |
| Billing address | `doc.customer_address` | Selected billing address |

#### 6. Place Order (`place_order.html`)

Shows either "Place Order" (if checkout enabled) or "Request for Quote" button.

---

## Quotation Fields Available but NOT Used in Cart

These fields exist on the Quotation document and are populated by ERPNext's pricing engine, but the cart templates ignore them:

### Document Level
| Field | Type | Description | Used in Cart? |
|-------|------|-------------|--------------|
| `total` | Currency | Sum of item amounts | YES (in footer) |
| `net_total` | Currency | Total after item discounts | YES (payment summary) |
| `grand_total` | Currency | Final total with taxes | YES |
| `total_qty` | Float | Total quantity | YES (payment summary label) |
| `taxes` | Table | Tax breakdown | YES |
| `discount_amount` | Currency | Additional discount on total | NO |
| `additional_discount_percentage` | Percent | % discount on total | NO |
| `coupon_code` | Link | Applied coupon | PARTIAL (shown as badge, no amount) |
| `apply_discount_on` | Select | Net Total or Grand Total | NO |
| `base_discount_amount` | Currency | Discount in base currency | NO |
| `total_taxes_and_charges` | Currency | Sum of all taxes | NO (shown per-line only) |
| `rounding_adjustment` | Currency | Rounding | NO |
| `rounded_total` | Currency | Rounded grand total | NO |

### Item Level (Quotation Item)
| Field | Type | Description | Used in Cart? |
|-------|------|-------------|--------------|
| `item_code` | Link | Item reference | YES |
| `item_name` | Data | Item name | YES |
| `qty` | Float | Quantity | YES |
| `rate` | Currency | Final rate after discounts | YES |
| `amount` | Currency | qty * rate | YES |
| `price_list_rate` | Currency | **Original price before discount** | NO |
| `discount_percentage` | Percent | **Discount % applied** | NO |
| `discount_amount` | Currency | **Per-unit discount amount** | NO |
| `base_rate` | Currency | Rate in base currency | NO |
| `base_amount` | Currency | Amount in base currency | NO |
| `net_rate` | Currency | Rate after item-level discount | NO |
| `net_amount` | Currency | Amount after item-level discount | NO |
| `is_free_item` | Check | Added by pricing rule as free | YES (shows "FREE" badge) |
| `pricing_rules` | Small Text | **JSON of applied pricing rule names** | NO |
| `margin_type` | Select | Margin calculation type | NO |
| `margin_rate_or_amount` | Currency | Margin value | NO |
| `rate_with_margin` | Currency | Rate including margin | NO |

---

## AJAX Update Cycle

When a user changes quantity or removes an item, the JS calls:

```
shopping_cart.shopping_cart_update({item_code, qty, additional_notes})
  -> POST webshop.webshop.shopping_cart.cart.update_cart
       -> with_items=1
       -> Returns re-rendered HTML fragments:
          {
            items: rendered "cart_items.html",
            total: rendered "cart_items_total.html",
            taxes_and_totals: rendered "cart_payment_summary.html"
          }
  -> JS replaces DOM:
       $(".cart-items").html(r.message.items)
       $(".cart-tax-items").html(r.message.total)
       $(".payment-summary").html(r.message.taxes_and_totals)
```

The backend calls `apply_cart_settings()` before saving, which:
1. Sets price list and recalculates rates (`set_price_list_and_rate`)
2. Runs `calculate_taxes_and_totals` (ERPNext standard - this IS where discounts are computed)
3. Sets taxes from templates
4. Applies shipping rules

**The discounts ARE being calculated on the backend.** They just aren't rendered in the templates.

---

## Comparison: Cart vs Order Page Discount Display

The **order_taxes.html** template (used on `/orders/<name>`) DOES show discounts:

```jinja
{# order_taxes.html - this IS implemented for orders #}
{% if doc.coupon_code %}
  Savings: {{ sum of (price_list_rate * qty * discount_percentage / 100) for each item }}
{% endif %}
```

But `cart_payment_summary.html` has NONE of this logic. The savings calculation exists in `order_taxes.html` but was never ported to the cart payment summary.

---

## The Decorator Function

`decorate_quotation_doc(doc)` in `cart.py` enriches each Quotation Item with web-specific data:

```python
def decorate_quotation_doc(doc):
    for d in doc.get("items", []):
        # Adds: web_item_name, thumbnail, website_image, description, route
        # For variants: looks up the template item's Website Item
        # Sets warehouse from website_warehouse
```

This decorator does NOT add any discount/pricing info - it only adds display metadata.

---

## Summary: What Needs to Change for Discount Visibility

1. **`cart_items.html`** - Show `price_list_rate` (struck through) alongside `rate` when they differ. Show `discount_percentage`.
2. **`cart_payment_summary.html`** - Add savings row (similar to `order_taxes.html`). Show `discount_amount` if present.
3. **`cart_items_total.html`** - Optionally show pre-discount total vs discounted total.
4. **`cart_items_dropdown.html`** (navbar mini-cart) - Show original vs discounted price.
5. **Backend** - No changes needed. All discount data is already computed and available on the Quotation.

---

## Related Wiki Pages

- [01 - Architecture Overview](01-Architecture-Overview.md) - How Cart=Quotation fits into the overall system
- [06 - Pricing & Discounts](06-Pricing-and-Discounts.md) - How pricing rules populate the fields documented above
- [07 - Checkout & Orders](07-Checkout-and-Orders.md) - What happens when Place Order is clicked
- [08 - Templates & Frontend](08-Templates-and-Frontend.md) - Map of all templates referenced here
- [10 - Feature Gap: Cart Discounts](10-Feature-Gap-Cart-Discounts.md) - Analysis of the missing discount display
- [14 - Hypothesis: Discount & Deadline Visibility](14-Hypothesis-Discount-Deadline-Visibility.md) - Exact implementation plan for surfacing hidden fields
- [Back to Home](00-Home.md)
