# 13 - Discount Visibility & Offer Urgency

**Parent:** [Webshop Index](Webshop-Index)  
**Previous:** [12 - Staging Sandbox Deployment](Webshop-12-Staging-Sandbox-Deployment)  
**Next:** [14 - Hypothesis: Discount Deadline Visibility](Webshop-14-Hypothesis-Discount-Deadline-Visibility)  
**Source:** [Comfac Webstore Wiki - Chapter 13](https://github.com/Comfac-Global-Group/comfac-webstore/wiki/13-Discount-Visibility-and-Urgency)

---

## Goal

Make discounts, promotions, and offer deadlines clearly visible to customers throughout the shopping experience - from product browsing to cart to checkout - creating transparency and a sense of urgency.

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
|----------------|---------------|
| > 14 days | Green text, informational |
| 7-14 days | Yellow/orange badge: "Ends soon" |
| 1-7 days | Red badge: "Only X days left!" |
| < 24 hours | Red pulsing: "Ends today!" |
| Expired | Remove discount, recalculate |

## Feature: Payment Summary with Savings

In `cart_payment_summary.html`:

```
Subtotal (before discounts) ...... $XXX.XX  (strikethrough, muted)
Your Savings ..................... -$XX.XX  (green)
Net Total (X Items) .............. $XXX.XX
[Additional Discount ............. -$XX.XX] (if doc.discount_amount)
Tax A ............................ $XX.XX
Tax B ............................ $XX.XX
----------------------------------------
Grand Total ...................... $XXX.XX
```

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

## Sample Test Scenarios

### Scenario 1: Percentage Discount with Deadline

- Product: "DDR5 RAM 32GB" at $149.99
- Pricing Rule: 20% off, valid_upto = March 15, 2026
- Cart should show: $149.99 → $119.99 (-20%), "Offer ends March 15" (24 days)

### Scenario 2: Coupon Code Discount

- Product: "1TB NVMe SSD" at $89.99
- Coupon "SAVE15" for 15% off
- Cart should show: $89.99 → $76.49 (-15%), coupon badge

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
- Cart should show: $29.99 → $17.99, RED "Offer ends TODAY!"

### Scenario 6: Multiple Overlapping Offers

- Product qualifies for both "Brand Sale 10%" and "Category Sale 15%"
- ERPNext applies the better rule (or both, depending on config)
- Cart should show the effective discount and list active offers

---

**See Also:** [Chapter 14: Hypothesis - Implementation Plan](Webshop-14-Hypothesis-Discount-Deadline-Visibility)

**Navigation:** [Webshop Index](Webshop-Index) | [Previous: 12 - Staging Sandbox](Webshop-12-Staging-Sandbox-Deployment) | [Next: 14 - Hypothesis](Webshop-14-Hypothesis-Discount-Deadline-Visibility)
