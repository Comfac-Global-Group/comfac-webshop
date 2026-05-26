# 06 - Pricing & Discounts

**Parent:** [Webshop Index](Webshop-Index)  
**Previous:** [05 - Variant Selector](Webshop-05-Variant-Selector)  
**Next:** [07 - Checkout & Orders](Webshop-07-Checkout-and-Orders)  
**Source:** [Comfac Webstore Wiki - Chapter 06](https://github.com/Comfac-Global-Group/comfac-webstore/wiki/06-Pricing-and-Discounts)

---

## Pricing Architecture

ERPNext's pricing engine handles all calculations:

1. **Price List** - Base prices per item
2. **Pricing Rules** - Discounts based on conditions (qty, customer, date range, etc.)
3. **Coupon Codes** - Additional discounts via codes
4. **Tax Rules** - Tax calculation

The webshop reads the **results** of these calculations but does not implement the logic itself.

## Discount Calculation Flow

```
1. User adds item to cart
2. cart.py:apply_cart_settings() calls set_price_list_and_rate()
3. ERPNext pricing engine:
   - Reads Price List for base price (price_list_rate)
   - Checks Pricing Rules for discounts
   - Applies discount to get rate
4. calculate_taxes_and_totals() computes:
   - item.amount = rate * qty
   - doc.total = sum of all item.amount
```

## Key Pricing Fields on Quotation

| Field | Location | Contains |
|-------|----------|----------|
| `price_list_rate` | Quotation Item | Original price from Price List |
| `rate` | Quotation Item | Final price after discount |
| `discount_percentage` | Quotation Item | % discount applied |
| `discount_amount` | Quotation Item | Fixed discount amount |
| `amount` | Quotation Item | Line total (rate * qty) |
| `total` | Quotation | Sum of all item amounts |
| `net_total` | Quotation | Total after item-level discounts |
| `discount_amount` | Quotation | Additional order-level discount |
| `grand_total` | Quotation | Final total with taxes |
| `coupon_code` | Quotation | Applied coupon code |

## Missing: Discount Visibility

**Critical Gap:** While ERPNext calculates and stores all pricing data, the webshop templates do not display:
- Original prices (strikethrough)
- Discount percentages
- "You save" amounts
- Offer deadlines
- Total savings

**See:** [Feature Gap: Cart Discounts](Webshop-10-Feature-Gap-Cart-Discounts) for implementation plan

---

**Navigation:** [Webshop Index](Webshop-Index) | [Previous: 05 - Variant Selector](Webshop-05-Variant-Selector) | [Next: 07 - Checkout & Orders](Webshop-07-Checkout-and-Orders)
