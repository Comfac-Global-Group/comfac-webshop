# 08 - Templates & Frontend

**Parent:** [Webshop Index](Webshop-Index)  
**Previous:** [07 - Checkout & Orders](Webshop-07-Checkout-and-Orders)  
**Next:** [09 - Hooks & Events](Webshop-09-Hooks-and-Events)  
**Source:** [Comfac Webstore Wiki - Chapter 08](https://github.com/Comfac-Global-Group/comfac-webstore/wiki/08-Templates-and-Frontend)

---

## Template Structure

### Pages (Full Page Templates)

| File | Route | Purpose |
|------|-------|---------|
| `templates/pages/cart.html` | /cart | Shopping cart |
| `templates/pages/order.html` | /orders/{name} | Order details |
| `templates/pages/wishlist.html` | /wishlist | Wishlist |
| `templates/pages/product_search.html` | /products | Search results |
| `templates/pages/customer_reviews.html` | - | Review management |

### Includes (Partial Templates)

**Cart Components** (`templates/includes/cart/`):

| File | Purpose |
|------|---------|
| `cart_items.html` | Cart line items table |
| `cart_items_total.html` | Subtotal display |
| `cart_payment_summary.html` | Taxes, grand total |
| `cart_items_dropdown.html` | Mini-cart in navbar |
| `cart_address.html` | Address selection |
| `place_order.html` | Order button |
| `coupon_code.html` | Coupon input |

## JavaScript Files

| File | Purpose |
|------|---------|
| `public/js/shopping_cart.js` | Cart interactions, AJAX updates |
| `public/js/wishlist.js` | Wishlist add/remove |
| `public/js/customer_reviews.js` | Review submission |
| `templates/generators/item/item_configure.js` | Variant selector |
| `templates/includes/product_page.js` | Product page interactions |

## CSS/SCSS

| File | Purpose |
|------|---------|
| `public/scss/webshop-web.bundle.css` | Main stylesheet |
| `public/scss/webshop_cart.scss` | Cart-specific styles |

---

**Navigation:** [Webshop Index](Webshop-Index) | [Previous: 07 - Checkout & Orders](Webshop-07-Checkout-and-Orders) | [Next: 09 - Hooks & Events](Webshop-09-Hooks-and-Events)
