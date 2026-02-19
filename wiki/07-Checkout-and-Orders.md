# Checkout & Orders

## Place Order Flow

1. User clicks "Place Order" button
2. JS calls `webshop.webshop.shopping_cart.cart.place_order`
3. Backend:
   - Gets the cart Quotation
   - Sets company from Webshop Settings
   - Submits the Quotation (`quotation.submit()`)
   - Creates a Sales Order via `_make_sales_order(quotation.name)`
   - Validates stock availability (if `allow_items_not_in_stock` is off)
   - Inserts and submits the Sales Order
   - Clears the cart_count cookie
4. Returns Sales Order name
5. JS redirects to `/orders/<sales_order_name>`

## Request for Quotation Flow (alternative)

If checkout is disabled, the "Request for Quote" button:
1. Gets the cart Quotation
2. Either saves (draft) or submits it based on `save_quotations_as_draft` setting
3. Redirects to `/quotations/<quotation_name>`

## Payment Flow

- If `enable_checkout` is on, the Payment Request override handles payment gateway integration
- `override_doctype/payment_request.py` customizes the payment flow
- Uses the `payments` app for gateway integration

## Order History Pages

- `/orders` - Lists past Sales Orders
- `/orders/<name>` - Order detail page (`templates/pages/order.html`)
- `/quotations` - Lists past Quotations

## Stock Validation

During place_order:
```python
for item in sales_order.get("items"):
    item.warehouse = frappe.db.get_value("Website Item", {"item_code": item.item_code}, "website_warehouse")
    if is_stock_item:
        item_stock = get_web_item_qty_in_stock(item.item_code, "website_warehouse")
        if not item_stock.in_stock: throw("Not in Stock")
        if item.qty > item_stock.stock_qty: throw("Only X in Stock")
```

---

## Related Wiki Pages

- [03 - Shopping Cart & Quotation Deep Dive](03-Shopping-Cart-Quotation-Deep-Dive.md) - The Quotation that becomes a Sales Order
- [06 - Pricing & Discounts](06-Pricing-and-Discounts.md) - How prices/discounts carry through to the order
- [02 - DocTypes](02-DocTypes.md) - Payment Request override details
- [Back to Home](00-Home.md)
