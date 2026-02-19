# Hooks & Events

## hooks.py Configuration

### DocType Class Overrides
```python
override_doctype_class = {
    "Payment Request": "...override_doctype.payment_request.PaymentRequest",
    "Item Group": "...override_doctype.item_group.WebshopItemGroup",
    "Item": "...override_doctype.item.WebshopItem",
}
```

### Doc Events
| DocType | Event | Handler | Purpose |
|---------|-------|---------|---------|
| Item | on_update | `update_website_item.execute` | Sync changes to Website Item |
| Item | on_update | `invalidate_item_variants_cache.execute` | Clear Redis variant cache |
| Item | before_rename | `validate_duplicate_website_item.execute` | Prevent naming conflicts |
| Item | after_rename | `invalidate_item_variants_cache.execute` | Clear cache after rename |
| Sales Taxes Template | on_update | `webshop_settings.validate_cart_settings` | Validate tax setup |
| Quotation | validate | `validate_shopping_cart_items.execute` | Validate cart items on save |
| Price List | validate | `check_impact_on_cart.execute` | Check if price change affects carts |
| Tax Rule | validate | `validate_use_for_cart.execute` | Validate cart tax rules |

### Session Hooks
- `on_logout` -> `clear_cart_count` (removes cart cookie)
- `on_session_creation` -> `update_debtors_account` + `set_cart_count`

### Website Hooks
- `update_website_context` -> `shopping_cart.utils.update_website_context`
- `website_generators` -> Website Item, Item Group
- `has_website_permission` -> Permission checks for Website Item and Item Group

### Client-Side
- `doctype_js["Item"]` -> `public/js/override/item.js`
- `doctype_js["Homepage"]` -> `public/js/override/homepage.js`

## CRUD Events Detail

### `validate_shopping_cart_items.execute`
**File:** `crud_events/quotation/validate_shopping_cart_items.py`
- Runs on Quotation validate
- Ensures cart items have valid Website Items

### `update_website_item.execute`
**File:** `crud_events/item/update_website_item.py`
- When an Item is updated, syncs relevant fields to its Website Item

### `check_impact_on_cart.execute`
**File:** `crud_events/price_list/check_impact_on_cart.py`
- When a Price List is modified, checks if it affects any active shopping carts

---

## Related Wiki Pages

- [01 - Architecture Overview](01-Architecture-Overview.md) - How hooks integrate the app with ERPNext
- [02 - DocTypes](02-DocTypes.md) - The DocTypes these events hook into
- [03 - Shopping Cart & Quotation Deep Dive](03-Shopping-Cart-Quotation-Deep-Dive.md) - Quotation validate event and cart logic
- [06 - Pricing & Discounts](06-Pricing-and-Discounts.md) - Price List and Tax Rule validation hooks
- [Back to Home](00-Home.md)
