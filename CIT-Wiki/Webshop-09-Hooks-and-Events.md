# 09 - Hooks & Events

**Parent:** [Webshop Index](Webshop-Index)  
**Previous:** [08 - Templates & Frontend](Webshop-08-Templates-and-Frontend)  
**Next:** [10 - Feature Gap: Cart Discounts](Webshop-10-Feature-Gap-Cart-Discounts)  
**Source:** [Comfac Webshop Wiki - Chapter 09](https://github.com/Comfac-Global-Group/comfac-webshop/wiki/09-Hooks-and-Events)

---

## App Hooks (`webshop/hooks.py`)

```python
# Installation
after_install = "webshop.setup.install.after_install"

# Session Management
on_logout = "webshop.webshop.shopping_cart.utils.clear_cart_count"
on_session_creation = [
    "webshop.webshop.utils.portal.update_debtors_account",
    "webshop.webshop.shopping_cart.utils.set_cart_count",
]

# Website Context
update_website_context = [
    "webshop.webshop.shopping_cart.utils.update_website_context",
]

# DocType Overrides
override_doctype_class = {
    "Payment Request": "webshop.webshop.doctype.override_doctype.payment_request.PaymentRequest",
    "Item Group": "webshop.webshop.doctype.override_doctype.item_group.WebshopItemGroup",
    "Item": "webshop.webshop.doctype.override_doctype.item.WebshopItem",
}

# DocType Events
doc_events = {
    "Item": {
        "on_update": [
            "webshop.webshop.crud_events.item.update_website_item.execute",
            "webshop.webshop.crud_events.item.invalidate_item_variants_cache.execute",
        ],
        "before_rename": [
            "webshop.webshop.crud_events.item.validate_duplicate_website_item.execute",
        ],
        "after_rename": [
            "webshop.webshop.crud_events.item.invalidate_item_variants_cache.execute",
        ],
    },
    "Quotation": {
        "validate": [
            "webshop.webshop.crud_events.quotation.validate_shopping_cart_items.execute",
        ],
    },
    "Price List": {
        "validate": [
            "webshop.webshop.crud_events.price_list.check_impact_on_cart.execute"
        ],
    },
    "Tax Rule": {
        "validate": [
            "webshop.webshop.crud_events.tax_rule.validate_use_for_cart.execute",
        ],
    },
}

# Website Generators
website_generators = ["Website Item", "Item Group"]

# Website Permissions
has_website_permission = {
    "Website Item": "webshop.webshop.doctype.website_item.website_item.has_website_permission_for_website_item",
    "Item Group": "webshop.webshop.doctype.website_item.website_item.has_website_permission_for_item_group"
}
```

## CRUD Events

**Item Events** (`webshop/webshop/crud_events/item/`):

- `update_website_item.execute` - Sync Item → Website Item
- `invalidate_item_variants_cache.execute` - Clear variant cache on save/rename
- `validate_duplicate_website_item.execute` - Prevent duplicate web items

**Quotation Events** (`webshop/webshop/crud_events/quotation/`):

- `validate_shopping_cart_items.execute` - Validate cart items on save

**Price List Events** (`webshop/webshop/crud_events/price_list/`):

- `check_impact_on_cart.execute` - Check if price list changes affect cart

**Tax Rule Events** (`webshop/webshop/crud_events/tax_rule/`):

- `validate_use_for_cart.execute` - Validate tax rules for cart usage

---

**Navigation:** [Webshop Index](Webshop-Index) | [Previous: 08 - Templates & Frontend](Webshop-08-Templates-and-Frontend) | [Next: 10 - Feature Gap: Cart Discounts](Webshop-10-Feature-Gap-Cart-Discounts)
