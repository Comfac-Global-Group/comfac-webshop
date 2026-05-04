# 10 - Feature Gap: Cart Discounts

**Parent:** [Webshop Index](Webshop-Index)  
**Previous:** [09 - Hooks & Events](Webshop-09-Hooks-and-Events)  
**Next:** [11 - Feature Plan: System Builder](Webshop-11-Feature-Plan-System-Builder)  
**Source:** [Comfac Webshop Wiki - Chapter 10](https://github.com/Comfac-Global-Group/comfac-webshop/wiki/10-Feature-Gap-Cart-Discounts)

**Status:** 🔴 Not Implemented | **Priority:** High

---

## Problem Statement

Discounts (from Pricing Rules, Coupon Codes, etc.) are calculated on the Quotation backend but are NOT displayed to the customer in the shopping cart UI. Customers see only the final price without understanding what promotions are active or how much they're saving.

## Current State

### What the customer sees in the cart:

- Item name, code, image
- Quantity (editable)
- Rate (final price per unit)
- Amount (total for that line)
- Net Total, Taxes, Grand Total
- Coupon code badge (if applied)

### What exists on the Quotation but is HIDDEN:

- Original price (`price_list_rate`) before discount
- Discount percentage (`discount_percentage`)
- Per-item discount amount
- Total savings
- Which pricing rules are active
- Additional discount on total (`discount_amount`, `additional_discount_percentage`)

## Where the Fix Needs to Happen

### 1. `cart_items.html` - Per-item discount display

**Current:** Shows only `rate` and `amount`
**Needed:** Show `price_list_rate` struck through when it differs from `rate`, plus discount badge

```jinja2
{% if item.price_list_rate and item.price_list_rate != item.rate %}
    <span class="original-price text-muted" style="text-decoration: line-through;">
        {{ item.get_formatted('price_list_rate') }}
    </span>
    <span class="discount-badge text-success ml-1">
        -{{ item.discount_percentage }}%
    </span>
{% endif %}
```

### 2. `cart_payment_summary.html` - Savings total

**Current:** Net Total, Taxes, Grand Total only
**Needed:** Add "You Save" row

### 3. `cart_items_total.html` - Pre-discount subtotal

**Current:** Shows `doc.total` only
**Needed:** Optionally show original total and savings

### 4. `cart_items_dropdown.html` - Navbar mini-cart

**Current:** Shows `amount` only
**Needed:** Strike-through price when discounted

### 5. Quotation DocType Modifications

To "better reflect discounts" per the requirements:

- Consider adding a **child table or virtual field** that summarizes all active pricing rules per item
- Add a "Discount Summary" section to the Quotation print format
- Potentially add `total_savings` as a computed field on Quotation

## No Backend Changes Needed

All discount data is already computed by ERPNext's pricing engine during:
- `apply_cart_settings()` 
- `set_price_list_and_item_details()` 
- `calculate_taxes_and_totals()`

This is purely a **frontend/template display issue**.

## Files to Modify

| File | Change |
|------|--------|
| `templates/includes/cart/cart_items.html` | Add original price, discount % display |
| `templates/includes/cart/cart_payment_summary.html` | Add savings row, discount summary |
| `templates/includes/cart/cart_items_total.html` | Add pre-discount total |
| `templates/includes/cart/cart_items_dropdown.html` | Add strike-through price |
| `public/scss/webshop_cart.scss` | Styles for discount badges, strike-through |

## Edge Cases to Handle

1. **Free items** (`is_free_item=True`) - already handled with "FREE" badge
2. **Items with no discount** (`price_list_rate == rate`) - no change needed
3. **Additional discount on total** (`doc.discount_amount`) - show separately
4. **Multiple pricing rules per item** - show highest or combined
5. **Margin-based pricing** - `rate_with_margin` field

## Related Documentation

- [Chapter 13: Discount Visibility & Urgency](Webshop-13-Discount-Visibility-and-Urgency) - UI specifications
- [Chapter 14: Hypothesis - Discount Deadline Visibility](Webshop-14-Hypothesis-Discount-Deadline-Visibility) - Exact implementation plan

---

**Navigation:** [Webshop Index](Webshop-Index) | [Previous: 09 - Hooks & Events](Webshop-09-Hooks-and-Events) | [Next: 11 - System Builder](Webshop-11-Feature-Plan-System-Builder)
