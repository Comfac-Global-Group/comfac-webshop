# 03 - Shopping Cart & Quotation Deep Dive

**Parent:** [Webshop Index](Webshop-Index)  
**Previous:** [02 - DocTypes](Webshop-02-DocTypes)  
**Next:** [04 - Product Pages & Browsing](Webshop-04-Product-Pages-and-Browsing)  
**Source:** [Comfac Webstore Wiki - Chapter 03](https://github.com/Comfac-Global-Group/comfac-webstore/wiki/03-Shopping-Cart-Quotation-Deep-Dive)

---

## How the Cart IS a Quotation

The webshop has no separate "cart" data model. The shopping cart IS an ERPNext **Quotation** document with `order_type = "Shopping Cart"` and `docstatus = 0` (Draft).

When a user visits `/cart`:

```
cart.py (template controller)
  -> get_cart_quotation()
       -> _get_cart_quotation(party)  # finds or creates the Quotation
       -> decorate_quotation_doc(doc) # adds web-specific fields (thumbnail, route, etc.)
       -> returns { doc, shipping_addresses, billing_addresses, shipping_rules, cart_settings }
```

The entire `doc` object passed to the Jinja templates IS the Quotation document.

## Data Flow: Cart UI to Quotation

### Page Load Context

The `/cart` page calls `get_cart_quotation()` which returns:

| Context Key | Source | Description |
|-------------|--------|-------------|
| `doc` | Quotation document | The full quotation with all fields |
| `doc.items` | Quotation Item child table | Line items in the cart |
| `cart_settings` | Webshop Settings | Controls what's shown (prices, checkout, etc.) |
| `shipping_addresses` | Customer's Address | Shipping address options |
| `billing_addresses` | Customer's Address | Billing address options |
| `shipping_rules` | Shipping Rule | Available shipping options |

### Template Breakdown

#### Cart Items Table (`cart_items.html`)

**File:** `templates/includes/cart/cart_items.html`

For each `d in doc.items` (Quotation Item), displays:

| Displayed | Quotation Item Field | Notes |
|-----------|---------------------|-------|
| Product image | `d.thumbnail` | Added by decorator from Website Item |
| Item name | `d.web_item_name` or `d.item_name` | web_item_name added by decorator |
| Item code | `d.item_code` | Direct from Quotation Item |
| Quantity | `d.qty` (formatted) | Editable input |
| Subtotal | `d.amount` (formatted) | `item.get_formatted('amount')` |
| Rate | `d.rate` (formatted) | Only shown if NOT a free item |
| Free item badge | `d.is_free_item` | From pricing rules |

**⚠️ CRITICAL GAP:** Template does NOT show:
- `d.price_list_rate` (original price before discount)
- `d.discount_percentage` (the discount applied)
- `d.discount_amount` (monetary discount)
- `d.pricing_rules` (which pricing rules were applied)
- Strike-through original price
- Any "you save X%" messaging

#### Cart Items Total (`cart_items_total.html`)

**File:** `templates/includes/cart/cart_items_total.html`

Shows only `doc.total` (Net Total). Does NOT show:
- `doc.discount_amount` (additional discount on total)
- `doc.additional_discount_percentage`
- Any per-item discount breakdown

#### Payment Summary (`cart_payment_summary.html`)

**File:** `templates/includes/cart/cart_payment_summary.html`

Shows Net Total, Taxes, Grand Total. Does NOT show:
- `doc.discount_amount`
- `doc.additional_discount_percentage`
- Per-item discount_percentage
- Per-item price_list_rate vs rate comparison
- Coupon code display (commented out TODO in template)
- Savings calculation

## Hidden Fields (Exist but Not Used)

### Document Level

| Field | Type | Used? |
|-------|------|-------|
| `total` | Currency | YES |
| `net_total` | Currency | YES |
| `grand_total` | Currency | YES |
| `total_qty` | Float | YES |
| `taxes` | Table | YES |
| `discount_amount` | Currency | **NO** |
| `additional_discount_percentage` | Percent | **NO** |
| `coupon_code` | Link | PARTIAL |

### Item Level

| Field | Type | Used? |
|-------|------|-------|
| `item_code` | Link | YES |
| `qty` | Float | YES |
| `rate` | Currency | YES |
| `amount` | Currency | YES |
| `price_list_rate` | Currency | **NO** |
| `discount_percentage` | Percent | **NO** |
| `discount_amount` | Currency | **NO** |
| `is_free_item` | Check | YES |
| `pricing_rules` | Small Text | **NO** |

## AJAX Update Cycle

When a user changes quantity or removes an item:

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
1. Sets price list and recalculates rates
2. Runs `calculate_taxes_and_totals` (where discounts are computed)
3. Sets taxes from templates
4. Applies shipping rules

**The discounts ARE being calculated on the backend.** They just aren't rendered in the templates.

## The Decorator Function

`decorate_quotation_doc(doc)` in `cart.py` enriches each Quotation Item with:
- `web_item_name`
- `thumbnail`
- `website_image`
- `description`
- `route`

This decorator does NOT add any discount/pricing info - it only adds display metadata.

---

**See Also:** [Feature Gap: Cart Discounts](Webshop-10-Feature-Gap-Cart-Discounts) for planned enhancements

**Navigation:** [Webshop Index](Webshop-Index) | [Previous: 02 - DocTypes](Webshop-02-DocTypes) | [Next: 04 - Product Pages](Webshop-04-Product-Pages-and-Browsing)
