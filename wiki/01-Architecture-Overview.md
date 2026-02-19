# Architecture Overview

## Framework Stack

- **Frappe Framework** - Python/JS full-stack framework
  - Server: Python 3, MariaDB/PostgreSQL
  - ORM: Frappe DocType system (metadata-driven)
  - Web: Jinja2 templates, jQuery frontend
  - API: Whitelisted Python functions exposed as REST endpoints
- **ERPNext** - ERP layer providing Item, Customer, Quotation, Sales Order, Pricing Rule, etc.
- **Payments** - Payment gateway integration

## How the App Integrates

The webshop is a **Frappe app** installed alongside ERPNext. It:

1. **Overrides ERPNext DocTypes** via `override_doctype_class` in hooks.py:
   - `Item` -> adds website publishing fields
   - `Item Group` -> adds website rendering (acts as category pages)
   - `Payment Request` -> customized payment flow

2. **Hooks into doc_events** for Quotation (validate cart items), Item (sync Website Item), Price List, Tax Rule

3. **Provides website generators** for `Website Item` and `Item Group` (auto-generates web pages from DocType records)

4. **Registers web pages** at:
   - `/all-products` - product listing with filters
   - `/shop-by-category` - category browsing
   - `/cart` - shopping cart page
   - `/orders` - order history
   - `/wishlist` - saved items
   - `/<item-route>` - individual product pages (generated)
   - `/<item-group-route>` - category pages (generated)

## Data Flow Summary

```
Website Item (published product)
    |
    v
Product Page (variant selector if template item)
    |
    v
Add to Cart -> Quotation (order_type="Shopping Cart", docstatus=0)
    |           - Quotation Item rows (item_code, qty, rate, amount)
    |           - Pricing rules applied via ERPNext
    |           - Taxes calculated
    v
Place Order -> Quotation.submit() -> Sales Order created
    |
    v
Payment (if checkout enabled) -> Payment Request
```

## Key Design Decisions

1. **Cart = Quotation**: The shopping cart IS an ERPNext Quotation document with `order_type="Shopping Cart"`. All pricing, taxes, and discounts flow through ERPNext's standard Quotation logic.

2. **Website Item vs Item**: ERPNext `Item` is the master. `Website Item` is a separate DocType that links to `Item` and adds web-specific fields (route, images, description). This allows selective publishing.

3. **Variant Handling**: Uses ERPNext's Item Variant system. Template items show a configurator; variant items are the actual purchasable products. Variant data is cached in Redis.

4. **No SPA**: Traditional server-rendered pages with jQuery for interactivity. Cart updates happen via AJAX calls that return re-rendered HTML fragments.

---

## Related Wiki Pages

- [02 - DocTypes](02-DocTypes.md) - Detailed listing of all DocTypes
- [03 - Shopping Cart & Quotation Deep Dive](03-Shopping-Cart-Quotation-Deep-Dive.md) - How the Cart=Quotation design works in practice
- [08 - Templates & Frontend](08-Templates-and-Frontend.md) - Complete file map of templates and JS
- [09 - Hooks & Events](09-Hooks-and-Events.md) - How the app integrates via hooks
- [Back to Home](00-Home.md)
