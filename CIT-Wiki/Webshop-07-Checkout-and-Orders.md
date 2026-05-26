# 07 - Checkout & Orders

**Parent:** [Webshop Index](Webshop-Index)  
**Previous:** [06 - Pricing & Discounts](Webshop-06-Pricing-and-Discounts)  
**Next:** [08 - Templates & Frontend](Webshop-08-Templates-and-Frontend)  
**Source:** [Comfac Webstore Wiki - Chapter 07](https://github.com/Comfac-Global-Group/comfac-webstore/wiki/07-Checkout-and-Orders)

---

## Place Order Flow

When user clicks "Place Order":

```
1. cart.place_order() called
2. Validations:
   - Cart not empty
   - Items in stock (if stock check enabled)
   - Valid shipping/billing addresses
3. Quotation.submit() - converts to Sales Order
4. If payment required:
   - Create Payment Request
   - Redirect to payment gateway
5. Order confirmation page
```

## Order Pages

**Files:** `templates/pages/order.html`, `order.js`, `order.py`

- Shows order details, status, tracking
- Payment status
- Linked documents (Sales Order, Payment Entry)

## Wishlist

**Files:** `templates/pages/wishlist.html`, `wishlist.py`

- User's saved items
- Add to cart from wishlist
- Remove items

---

**Navigation:** [Webshop Index](Webshop-Index) | [Previous: 06 - Pricing & Discounts](Webshop-06-Pricing-and-Discounts) | [Next: 08 - Templates & Frontend](Webshop-08-Templates-and-Frontend)
