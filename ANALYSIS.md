# Frappe Webshop - Application Analysis

## High-Level Structure

Frappe Webshop is an **Open Source eCommerce Platform** built on the Frappe Framework, designed for small to medium-sized businesses to create online stores. It integrates with ERPNext for inventory management, billing, and order processing.

This is a **fork** of the official [Frappe Webshop](https://github.com/frappe/webshop), customized for Comfac's needs with planned enhancements around discount visibility and a System Builder configurator.

**Required apps:** `frappe`, `erpnext`, `payments`

**Codebase size:** ~172 files, ~988KB (excluding `.git`)

### Architecture Overview
- **Framework**: Frappe Framework (Python + JavaScript)
- **Server**: Python 3.10+, MariaDB/PostgreSQL
- **ORM**: Frappe DocType system (metadata-driven)
- **Web**: Jinja2 templates, jQuery frontend
- **API**: Whitelisted Python functions exposed as REST endpoints
- **Dependencies**: `payments` app and `erpnext` (required)
- **Type**: Frappe App with website/webshop functionality
- **Single Module**: Webshop
- **Package Manager**: Flit (build-backend)

---

## 01 - Architecture Overview

### 1.1 Framework Stack

- **Frappe Framework** - Python/JS full-stack framework
  - Server: Python 3, MariaDB/PostgreSQL
  - ORM: Frappe DocType system (metadata-driven)
  - Web: Jinja2 templates, jQuery frontend
  - API: Whitelisted Python functions exposed as REST endpoints
- **ERPNext** - ERP layer providing Item, Customer, Quotation, Sales Order, Pricing Rule, etc.
- **Payments** - Payment gateway integration

### 1.2 How the App Integrates

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

### 1.3 Data Flow Summary

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

### 1.4 Key Design Decisions

1. **Cart = Quotation**: The shopping cart IS an ERPNext Quotation document with `order_type="Shopping Cart"`. All pricing, taxes, and discounts flow through ERPNext's standard Quotation logic.

2. **Website Item vs Item**: ERPNext `Item` is the master. `Website Item` is a separate DocType that links to `Item` and adds web-specific fields (route, images, description). This allows selective publishing.

3. **Variant Handling**: Uses ERPNext's Item Variant system. Template items show a configurator; variant items are the actual purchasable products. Variant data is cached in Redis.

4. **No SPA**: Traditional server-rendered pages with jQuery for interactivity. Cart updates happen via AJAX calls that return re-rendered HTML fragments.

---

## 02 - DocTypes

### 2.1 Custom DocTypes (defined in webshop)

#### 2.1.1 Webshop Settings (Singleton)

**Path:** `webshop/webshop/doctype/webshop_settings/`

- Main configuration for the webshop
- Fields: company, price_list, default_customer_group, quotation_series
- Toggles: enabled, show_price, show_stock_availability, enable_checkout, enable_wishlist
- Filter settings, products_per_page, slideshow
- Coupon code settings, guest price visibility

#### 2.1.2 Website Item

**Path:** `webshop/webshop/doctype/website_item/`

- Published product linked to an ERPNext `Item`
- Fields: item_code, web_item_name, route, description, website_image, thumbnail
- Website warehouse, on_backorder flag
- Acts as a website generator (auto-creates web pages)
- Tabbed sections for additional content

#### 2.1.3 Wishlist

**Path:** `webshop/webshop/doctype/wishlist/`

- User wishlist storage
- Child table of wished items

#### 2.1.4 Item Review

**Path:** `webshop/webshop/doctype/item_review/`

- Customer product reviews and ratings

#### 2.1.5 Recommended Items

**Path:** `webshop/webshop/doctype/recommended_items/`

- Product recommendations (child table)

#### 2.1.6 Website Item Tabbed Section

**Path:** `webshop/webshop/doctype/website_item_tabbed_section/`

- Additional content tabs on product pages

### 2.2 Override DocTypes

**Path:** `webshop/webshop/doctype/override_doctype/`

- **WebshopItem** (extends Item) - adds website publishing behavior
- **WebshopItemGroup** (extends Item Group) - adds website page generation, child group utilities
- **PaymentRequest** (extends Payment Request) - customized payment handling

### 2.3 ERPNext DocTypes Used (not defined here, but central)

- **Quotation** - THE cart document. order_type="Shopping Cart"
- **Quotation Item** - Line items in cart
- **Sales Order** - Created when order is placed
- **Item** - Master product data
- **Item Group** - Product categories
- **Pricing Rule** - Discount rules
- **Coupon Code** - Promotional codes
- **Customer** - Auto-created for web users
- **Address** - Billing/shipping addresses
- **Contact** - User contact info
- **Sales Taxes and Charges Template** - Tax configuration

---

## 03 - Shopping Cart & Quotation Deep Dive

### 3.1 How the Cart IS a Quotation

The webshop has no separate "cart" data model. The shopping cart IS an ERPNext **Quotation** document with `order_type = "Shopping Cart"` and `docstatus = 0` (Draft).

When a user visits `/cart`, this is what happens:

```
cart.py (template controller)
  -> get_cart_quotation()
       -> _get_cart_quotation(party)  # finds or creates the Quotation
       -> decorate_quotation_doc(doc) # adds web-specific fields (thumbnail, route, etc.)
       -> returns { doc, shipping_addresses, billing_addresses, shipping_rules, cart_settings }
```

The entire `doc` object passed to the Jinja templates IS the Quotation document.

### 3.2 Data Flow: What the Cart UI Reads from the Quotation

#### 3.2.1 Page Load (cart.py -> cart.html)

The `/cart` page calls `get_cart_quotation()` which returns a context dict with:

| Context Key | Source | Description |
|-------------|--------|-------------|
| `doc` | Quotation document | The full quotation with all fields |
| `doc.items` | Quotation Item child table | Line items in the cart |
| `cart_settings` | Webshop Settings singleton | Controls what's shown (prices, checkout, etc.) |
| `shipping_addresses` | Customer's Address records | Shipping address options |
| `billing_addresses` | Customer's Address records | Billing address options |
| `shipping_rules` | Shipping Rule doctype | Available shipping options |

#### 3.2.2 Template Breakdown: What Each Section Displays

##### Cart Items Table (`cart_items.html`)

**Source file:** `templates/includes/cart/cart_items.html`

For each `d in doc.items` (Quotation Item), displays:

| Displayed | Quotation Item Field | Notes |
|-----------|---------------------|-------|
| Product image | `d.thumbnail` | Added by `decorate_quotation_doc()` from Website Item |
| Item name | `d.web_item_name` or `d.item_name` | web_item_name added by decorator |
| Item code | `d.item_code` | Direct from Quotation Item |
| Quantity | `d.qty` (formatted) | Editable input |
| Subtotal | `d.amount` (formatted) | `item.get_formatted('amount')` |
| Rate | `d.rate` (formatted) | Only shown if NOT a free item |
| Free item badge | `d.is_free_item` | From pricing rules |

**CRITICAL GAP:** The cart items template shows `rate` and `amount` but does NOT show:
- `d.price_list_rate` (original price before discount)
- `d.discount_percentage` (the discount applied)
- `d.discount_amount` (monetary discount)
- `d.pricing_rules` (which pricing rules were applied)
- Strike-through original price
- Any "you save X%" messaging

##### Cart Items Total (`cart_items_total.html`)

**Source file:** `templates/includes/cart/cart_items_total.html`

| Displayed | Quotation Field | Notes |
|-----------|----------------|-------|
| Net Total | `doc.total` (formatted) | Sum of all item amounts (pre-tax) |

**What's NOT shown:**
- `doc.discount_amount` (additional discount on total)
- `doc.additional_discount_percentage`
- Any per-item discount breakdown

##### Payment Summary (`cart_payment_summary.html`)

**Source file:** `templates/includes/cart/cart_payment_summary.html`

| Displayed | Quotation Field | Notes |
|-----------|----------------|-------|
| Net Total (X Items) | `doc.net_total` + `doc.total_qty` | Header row |
| Tax rows | `doc.taxes[].description` + `doc.taxes[].tax_amount` | Each tax line |
| Grand Total | `doc.grand_total` | Final total |

**What's NOT shown (but EXISTS on the Quotation):**
- `doc.discount_amount`
- `doc.additional_discount_percentage`
- Per-item discount_percentage
- Per-item price_list_rate vs rate comparison
- Coupon code display (commented out TODO in template)
- Savings calculation

### 3.3 Quotation Fields Available but NOT Used in Cart

#### 3.3.1 Document Level

| Field | Type | Description | Used in Cart? |
|-------|------|-------------|---------------|
| `total` | Currency | Sum of item amounts | YES (in footer) |
| `net_total` | Currency | Total after item discounts | YES (payment summary) |
| `grand_total` | Currency | Final total with taxes | YES |
| `total_qty` | Float | Total quantity | YES (payment summary label) |
| `taxes` | Table | Tax breakdown | YES |
| `discount_amount` | Currency | Additional discount on total | **NO** |
| `additional_discount_percentage` | Percent | % discount on total | **NO** |
| `coupon_code` | Link | Applied coupon | PARTIAL (shown as badge, no amount) |

#### 3.3.2 Item Level (Quotation Item)

| Field | Type | Description | Used in Cart? |
|-------|------|-------------|---------------|
| `item_code` | Link | Item reference | YES |
| `item_name` | Data | Item name | YES |
| `qty` | Float | Quantity | YES |
| `rate` | Currency | Final rate after discounts | YES |
| `amount` | Currency | qty * rate | YES |
| `price_list_rate` | Currency | **Original price before discount** | **NO** |
| `discount_percentage` | Percent | **Discount % applied** | **NO** |
| `discount_amount` | Currency | **Per-unit discount amount** | **NO** |
| `is_free_item` | Check | Added by pricing rule as free | YES (shows "FREE" badge) |
| `pricing_rules` | Small Text | **JSON of applied pricing rule names** | **NO** |

### 3.4 AJAX Update Cycle

When a user changes quantity or removes an item, the JS calls:

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

1. Sets price list and recalculates rates (`set_price_list_and_rate`)
2. Runs `calculate_taxes_and_totals` (ERPNext standard - this IS where discounts are computed)
3. Sets taxes from templates
4. Applies shipping rules

**The discounts ARE being calculated on the backend.** They just aren't rendered in the templates.

### 3.5 The Decorator Function

`decorate_quotation_doc(doc)` in `cart.py` enriches each Quotation Item with web-specific data:

```python
def decorate_quotation_doc(doc):
    for d in doc.get("items", []):
        # Adds: web_item_name, thumbnail, website_image, description, route
        # For variants: looks up the template item's Website Item
        # Sets warehouse from website_warehouse
```

This decorator does NOT add any discount/pricing info - it only adds display metadata.

---

## 04 - Product Pages & Browsing

### 4.1 Product Listing Pages

#### 4.1.1 /all-products

**Files:** `www/all-products/index.py`, `index.html`, `index.js`

- Server-side: builds filter context (field filters, attribute filters) from Webshop Settings
- Client-side: JS calls `webshop.webshop.api.get_product_filter_data` API
- Uses `ProductQuery` engine (`product_data_engine/query.py`) for filtered product search
- Supports: search, field filters (item_group, brand), attribute filters (Color, Size), discount filters
- Pagination via `products_per_page` setting

#### 4.1.2 /shop-by-category

**Files:** `www/shop-by-category/index.py`, `index.html`, `index.js`

- Renders category cards based on Webshop Settings filter_fields
- Supports slideshow from Website Slideshow
- Uses `category_card_section.html` template for each category

#### 4.1.3 Item Group Pages (generated)

**File:** `templates/generators/item_group.html`

- Auto-generated pages for each Item Group with `show_in_website=1`
- Shows: slideshow, description, product grid, filters
- Product listing loaded via same JS as /all-products

### 4.2 Individual Product Pages

#### 4.2.1 Item Page (generated)

**Files:** `templates/generators/item/item.html` + sub-templates

Sub-templates:

- `item_image.html` - Product image carousel
- `item_details.html` - Title, item code, item group, description
- `item_add_to_cart.html` - Price display, qty selector, add to cart button (for non-variant items)
- `item_configure.html` + `item_configure.js` - Variant attribute selector (for template items)
- `item_specifications.html` - Item attributes table
- `item_reviews.html` - Customer reviews
- `item_inquiry.html` + `item_inquiry.js` - Product inquiry form

#### 4.2.2 Product Info API

**File:** `webshop/shopping_cart/product_info.py`

`get_product_info_for_website(item_code)` returns:

- price (formatted_price, price_list_rate, currency)
- qty in cart
- stock status (in_stock, stock_qty, on_backorder)
- UOM info

### 4.3 Product Data Engine

#### 4.3.1 Query Engine (`product_data_engine/query.py`)

- `ProductQuery.query()` - main search/filter method
- Supports: text search, field filters, attribute filters
- Returns items with price and discount info
- Falls back to legacy search if RediSearch unavailable

#### 4.3.2 Filter Builder (`product_data_engine/filters.py`)

- `ProductFiltersBuilder` - builds filter UI data
- Field filters from Webshop Settings
- Attribute filters from Item Variant Attributes
- Discount filters from pricing rules

### 4.4 Web Templates (Blocks)

- `hero_slider/` - Homepage hero carousel
- `product_card/` - Individual product card
- `product_category_cards/` - Category card grid
- `item_card_group/` - Group of item cards

---

## 05 - Variant Selector

### 5.1 How Variants Work in ERPNext + Webshop

ERPNext has a built-in **Item Variant** system:

- **Template Item**: defines attributes (e.g., Color, Size, RAM, Storage)
- **Variant Items**: concrete products with specific attribute values (e.g., "Laptop - 16GB RAM - 512GB SSD")

The webshop uses this to create a step-by-step configurator on product pages.

### 5.2 Key Files

- `webshop/variant_selector/utils.py` - Core variant logic
- `webshop/variant_selector/item_variants_cache.py` - Redis caching layer
- `templates/generators/item/item_configure.html` - Configurator UI
- `templates/generators/item/item_configure.js` - Configurator JS

### 5.3 Variant Selection Flow

1. User visits a Template Item page (has_variants=True)
2. `item_configure.html` renders attribute dropdowns
3. `item_configure.js` calls `get_next_attribute_and_values` API on each selection
4. Backend filters valid combinations, returns:
   - `next_attribute` - which attribute to select next
   - `valid_options_for_attributes` - valid values given current selections
   - `filtered_items_count` - how many variants match
   - `exact_match` - if one variant is fully selected
   - `product_info` - price for the matched variant
   - `available_qty` - stock quantity
5. When exact match found, "Add to Cart" button appears with variant item_code

### 5.4 Cache System (`ItemVariantsCacheManager`)

Uses Redis to cache:

- `item_variants_data` - all variant attribute values
- `item_attribute_value_map` - attribute -> variant mapping
- `optional_attributes` - which attributes are optional

Cache is invalidated on Item save/rename via crud_events hooks.

### 5.5 API Endpoints

#### `get_attributes_and_values(item_code)`

Returns all attributes and their possible values for a template item.

#### `get_next_attribute_and_values(item_code, selected_attributes)`

Progressive filtering - returns valid options given current selections.

#### `get_item_variant_price_dict(item_code, cart_settings)`

Gets price for a specific variant item.

### 5.6 Relevance to System Builder

The existing variant selector is a **single-item configurator**. The planned System Builder would need:

- **Multi-item configuration** (CPU + RAM + Storage + etc.)
- **Cross-item compatibility rules** (not just attribute filtering within one template)
- **Template/preset system** (save configurations)
- **Aggregated pricing** (total system price with combined discounts)

The variant_selector's caching and attribute filtering logic could be extended, but the System Builder is fundamentally a different scope.

---

## 06 - Pricing & Discounts

### 6.1 Pricing Architecture

ERPNext's pricing engine handles all calculations:

1. **Price List** - Base prices per item
2. **Pricing Rules** - Discounts based on conditions (qty, customer, date range, etc.)
3. **Coupon Codes** - Additional discounts via codes
4. **Tax Rules** - Tax calculation

The webshop reads the **results** of these calculations but does not implement the logic itself.

### 6.2 Discount Calculation Flow

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

### 6.3 Key Pricing Fields on Quotation

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

---

## 07 - Checkout & Orders

### 7.1 Place Order Flow

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

### 7.2 Order Pages

**Files:** `templates/pages/order.html`, `order.js`, `order.py`

- Shows order details, status, tracking
- Payment status
- Linked documents (Sales Order, Payment Entry)

### 7.3 Wishlist

**Files:** `templates/pages/wishlist.html`, `wishlist.py`

- User's saved items
- Add to cart from wishlist
- Remove items

---

## 08 - Templates & Frontend

### 8.1 Template Structure

#### Pages (Full Page Templates)

| File | Route | Purpose |
|------|-------|---------|
| `templates/pages/cart.html` | /cart | Shopping cart |
| `templates/pages/order.html` | /orders/{name} | Order details |
| `templates/pages/wishlist.html` | /wishlist | Wishlist |
| `templates/pages/product_search.html` | /products | Search results |
| `templates/pages/customer_reviews.html` | - | Review management |

#### Includes (Partial Templates)

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

### 8.2 JavaScript Files

| File | Purpose |
|------|---------|
| `public/js/shopping_cart.js` | Cart interactions, AJAX updates |
| `public/js/wishlist.js` | Wishlist add/remove |
| `public/js/customer_reviews.js` | Review submission |
| `templates/generators/item/item_configure.js` | Variant selector |
| `templates/includes/product_page.js` | Product page interactions |

### 8.3 CSS/SCSS

| File | Purpose |
|------|---------|
| `public/scss/webshop-web.bundle.css` | Main stylesheet |
| `public/scss/webshop_cart.scss` | Cart-specific styles |

---

## 09 - Hooks & Events

### 9.1 App Hooks (`webshop/hooks.py`)

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

### 9.2 CRUD Events

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

## 10 - Feature Gap: Cart Discounts (from Wiki)

### 10.1 Problem Statement

Discounts (from Pricing Rules, Coupon Codes, etc.) are calculated on the Quotation backend but are NOT displayed to the customer in the shopping cart UI. Customers see only the final price without understanding what promotions are active or how much they're saving.

### 10.2 Where the Fix Needs to Happen

#### 10.2.1 `cart_items.html` - Per-item discount display

**Current:** Shows only `rate` and `amount`
**Needed:** Show `price_list_rate` struck through when it differs from `rate`, plus discount badge

```jinja2
{# Proposed addition to item_subtotal macro #}
{% if item.price_list_rate and item.price_list_rate != item.rate %}
    <span class="original-price text-muted" style="text-decoration: line-through;">
        {{ item.get_formatted('price_list_rate') }}
    </span>
    <span class="discount-badge text-success ml-1">
        -{{ item.discount_percentage }}%
    </span>
{% endif %}
```

#### 10.2.2 `cart_payment_summary.html` - Savings total

**Current:** Net Total, Taxes, Grand Total only
**Needed:** Add "You Save" row

The logic already exists in `order_taxes.html`:

```jinja2
{% set tot_quotation_discount = [] %}
{%- for item in doc.items -%}
    {% if tot_quotation_discount.append(
        ((item.price_list_rate * item.qty) * item.discount_percentage) / 100
    ) %}{% endif %}
{% endfor %}
Savings: {{ tot_quotation_discount | sum }}
```

#### 10.2.3 `cart_items_total.html` - Pre-discount subtotal

**Current:** Shows `doc.total` only
**Needed:** Optionally show original total and savings

#### 10.2.4 `cart_items_dropdown.html` - Navbar mini-cart

**Current:** Shows `amount` only
**Needed:** Strike-through price when discounted

### 10.3 Files to Modify

| File | Change |
|------|--------|
| `templates/includes/cart/cart_items.html` | Add original price, discount % display |
| `templates/includes/cart/cart_payment_summary.html` | Add savings row, discount summary |
| `templates/includes/cart/cart_items_total.html` | Add pre-discount total |
| `templates/includes/cart/cart_items_dropdown.html` | Add strike-through price |
| `public/scss/webshop_cart.scss` | Styles for discount badges, strike-through |

### 10.4 No Backend Changes Needed

All discount data is already computed by ERPNext's pricing engine during `apply_cart_settings()` -> `set_price_list_and_item_details()` -> `calculate_taxes_and_totals()`. This is purely a **frontend/template display issue**.

---

## 11 - Feature Plan: System Builder (from Wiki)

### 11.1 Vision

A configurable product builder where customers can assemble multi-component systems (servers, desktops, maker kits, open-source hardware platforms) from a template of compatible components, with real-time pricing, compatibility enforcement, and the ability to save/load configurations.

### 11.2 Use Cases

1. **Server Builder** - Customer selects: chassis, CPU, RAM (qty/type), storage (multiple drives), NIC, PSU, OS
2. **Desktop Builder** - Case, motherboard, CPU, GPU, RAM, storage, PSU, peripherals
3. **Maker Kit Builder** - Board (RPi, Arduino, etc.), sensors, actuators, enclosure, power supply
4. **Future platforms** - Any multi-component configurable product

### 11.3 New DocTypes Needed

#### 11.3.1 System Builder Template

- Name, description, image
- Category (Server, Desktop, Maker Kit, etc.)
- Child table: **Component Slots**
  - Slot name (e.g., "CPU", "RAM", "Storage Bay 1")
  - Required (yes/no)
  - Min/Max quantity
  - Allowed Item Group or explicit item list
  - Default selection (if any)

#### 11.3.2 Compatibility Rule

- Rule name
- Rule type: "Requires", "Excludes", "Max Qty", "Min Qty"
- Source slot + attribute/item filter
- Target slot + attribute/item filter
- Error message

#### 11.3.3 Saved Configuration

- User (Customer)
- Template reference
- Name (user-defined)
- Child table: selected items per slot
- Total price, status (draft/shared/ordered)

### 11.4 Implementation Phases

#### Phase 1: Foundation

- Create System Builder Template DocType
- Create Component Slot child table
- Basic UI: template selection, slot browsing
- Simple "add all to cart" (no compatibility engine yet)

#### Phase 2: Compatibility

- Create Compatibility Rule DocType
- Build rule evaluation engine
- Real-time filtering of valid options
- Warning/error display

#### Phase 3: Save & Share

- Saved Configuration DocType
- User dashboard for saved configs
- Share via URL
- Load/clone/modify

#### Phase 4: Advanced

- Power/thermal budget calculation
- AI-assisted recommendations
- Preset "popular configurations"
- Comparison between configurations
- Integration with BOM for manufacturing

### 11.5 Technical Challenges

1. **Performance**: Evaluating compatibility across many items/rules in real-time
2. **Attribute mapping**: Different items have different attributes; need a normalized way to express compatibility
3. **Cart representation**: How to group system components in a Quotation
4. **Pricing complexity**: Component discounts + bundle discounts + system-level pricing rules
5. **Stock**: All components must be available simultaneously

---

## 12 - Staging Sandbox Deployment (from Wiki)

### 12.1 Purpose

Create an isolated environment to:
1. Clone production ERPNext instance
2. Install comfac-webshop fork
3. Validate seamless replacement of existing webshop
4. Test new features without affecting production

### 12.2 Phase 0: Baseline Validation

**Objective:** Verify comfac-webshop fork runs identically to base webshop

**Steps:**

1. **Clone Production Instance**
   ```bash
   # Backup production site
   bench --site production-site backup
   
   # Create staging site from backup
   bench --site staging-site restore production-site_backup.sql
   ```

2. **Install Fork**
   ```bash
   # Get comfac-webshop
   bench get-app https://github.com/Comfac-Global-Group/comfac-webshop.git
   
   # Install on staging site
   bench --site staging-site install-app webshop
   ```

3. **Validation Checklist**

| Test | Pass Criteria |
|------|---------------|
| Site loads | No 500 errors on homepage |
| Product listing | /all-products shows items |
| Product pages | Individual items render correctly |
| Add to cart | Items added to cart successfully |
| Cart page | /cart displays items with correct totals |
| Checkout flow | Place order creates Sales Order |
| Payment | Payment Request generates correctly |
| Wishlist | Add/remove items works |
| Search | Product search returns results |
| Filters | Category/attribute filters work |
| Variant selector | Template items show configurator |

4. **Comparison Testing**
   - Side-by-side comparison of base webshop vs fork
   - Same items, same prices, same cart behavior
   - No feature changes in Phase 0

### 12.3 Phase 1: Feature Development

**Objective:** Implement features on clone of successful staging

**Steps:**

1. **Clone Validated Staging**
   ```bash
   # Backup Phase 0 staging
   bench --site staging-site backup
   
   # Restore to experiment site
   bench --site experiment-site restore staging-site_backup.sql
   ```

2. **Implement Features**
   - Implement discount visibility (RQ-11.x)
   - Test each scenario thoroughly
   - Implement System Builder (Phase 1)

3. **Test Data Setup**
   - Create sample products with pricing rules
   - Set up coupon codes
   - Create offer deadlines
   - Build system builder templates

### 12.4 Phase 2: Production Merge

**Criteria for merge:**

- All Phase 0 validation checks pass
- Phase 1 feature tests complete
- No regressions from base webshop
- Documentation updated
- Rollback plan prepared

---

## 13 - Discount Visibility & Offer Urgency Specifications (from Wiki)

### 13.1 Goal

Make discounts, promotions, and offer deadlines clearly visible to customers throughout the shopping experience - from product browsing to cart to checkout - creating transparency and a sense of urgency.

### 13.2 Offer Deadline / Urgency Display

#### 13.2.1 Where Deadline Data Lives

ERPNext **Pricing Rule** has these date fields:

- `valid_from` - Start date of the offer
- `valid_upto` - End date of the offer (THIS IS THE DEADLINE)

The `pricing_rules` field on each Quotation Item contains the names of applied pricing rules (JSON string).

#### 13.2.2 How to Surface Deadlines

1. When rendering cart items, parse the `pricing_rules` field
2. Look up the Pricing Rule document(s)
3. If `valid_upto` exists, display it as an urgency indicator

#### 13.2.3 Proposed UI

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

#### 13.2.4 Urgency Levels

| Days Remaining | Display Style |
|----------------|---------------|
| > 14 days | Green text, informational |
| 7-14 days | Yellow/orange badge: "Ends soon" |
| 1-7 days | Red badge: "Only X days left!" |
| < 24 hours | Red pulsing: "Ends today!" |
| Expired | Remove discount, recalculate |

### 13.3 Product Page Offer Display

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

### 13.4 Sample Test Scenarios

#### Scenario 1: Percentage Discount with Deadline

- Product: "DDR5 RAM 32GB" at $149.99
- Pricing Rule: 20% off, valid_upto = March 15, 2026
- Cart should show: $149.99 → $119.99 (-20%), "Offer ends March 15" (24 days)

#### Scenario 2: Coupon Code Discount

- Product: "1TB NVMe SSD" at $89.99
- Coupon "SAVE15" for 15% off
- Cart should show: $89.99 → $76.49 (-15%), coupon badge

#### Scenario 3: Free Item Promotion

- Buy 2x "Cat6 Network Cable", get 1 free
- Cart should show: 2x at $12.99, 1x FREE, savings = $12.99

#### Scenario 4: Bundle/System Discount (future)

- Complete server build: $2,500
- System builder bundle discount: 5%
- Cart should show: original total, -5% bundle discount, final price

#### Scenario 5: Expiring Today

- Product: "USB Hub" at $29.99
- Flash sale: 40% off, valid_upto = today
- Cart should show: $29.99 → $17.99, RED "Offer ends TODAY!"

#### Scenario 6: Multiple Overlapping Offers

- Product qualifies for both "Brand Sale 10%" and "Category Sale 15%"
- ERPNext applies the better rule (or both, depending on config)
- Cart should show the effective discount and list active offers

---

## 14 - Hypothesis: Making Discounts and Deadlines Visible (from Wiki)

### 14.1 Prerequisite: Seamless Baseline First

**This hypothesis is NOT to be executed until the comfac-webshop fork runs seamlessly as a drop-in replacement on a production-like ERPNext instance.**

**Execution order:**

1. **Phase 0 (Staging Sandbox):** Clone the production ERPNext instance, install comfac-webshop, validate it works identically to the existing webshop. No feature changes. Pass all validation checks.

2. **Phase 1 (Experiment Clone):** Once Phase 0 is proven stable, clone THAT successful staging instance into a second sandbox. This is where we implement and test the hypothesis below.

3. **Phase 2 (Iterate):** Test with sample products, pricing rules, coupons, and deadline-bearing offers on the experiment clone. Validate every scenario. Only when everything passes do we merge back to the main fork.

**Do not skip Phase 0.**

### 14.2 Core Thesis

**All the data we need already exists on the Quotation document.** ERPNext's pricing engine populates discount fields on every cart save. We do not need to change the backend calculation logic. We need to:

1. **Surface existing hidden fields** in the cart templates
2. **Enrich the decorator** to pass pricing rule metadata (deadlines, titles) to the frontend
3. **Add summation logic** in the payment summary template
4. **Style it** so customers immediately see value and urgency

### 14.3 The Fields We Will Target

#### 14.3.1 Per-Item Fields (Quotation Item - already populated)

| Field | Type | What It Contains | Currently Used? |
|-------|------|------------------|-----------------|
| `price_list_rate` | Currency | Original unit price from the Price List (before any discount) | **NO** |
| `rate` | Currency | Final unit price (after discount applied) | YES |
| `discount_percentage` | Percent | The % discount applied by the Pricing Rule | **NO** |
| `discount_amount` | Currency | Per-unit discount in currency | **NO** |
| `amount` | Currency | `rate * qty` = line total after discount | YES |
| `is_free_item` | Check | True if item was added by a "Free Item" pricing rule | YES |
| `pricing_rules` | Small Text | **JSON string** of Pricing Rule document names | **NO** |

#### 14.3.2 Document-Level Fields (Quotation - already populated)

| Field | Type | What It Contains | Currently Used? |
|-------|------|------------------|-----------------|
| `total` | Currency | Sum of all `amount` values (item totals before tax) | YES |
| `net_total` | Currency | Total after additional discounts | YES |
| `grand_total` | Currency | Final total with taxes | YES |
| `discount_amount` | Currency | Additional discount on the overall total | **NO** |
| `additional_discount_percentage` | Percent | % discount on total | **NO** |
| `coupon_code` | Link | Applied Coupon Code document name | PARTIAL |

#### 14.3.3 Pricing Rule Fields (need to be looked up from pricing_rules JSON)

| Field | Type | What It Contains | Purpose for Us |
|-------|------|------------------|----------------|
| `title` | Data | Human-readable name (e.g., "Spring GPU Sale") | Display offer name to customer |
| `valid_from` | Date | Start date of the offer | Show when offer started |
| `valid_upto` | Date | **End date / DEADLINE** of the offer | **URGENCY DISPLAY** |
| `discount_percentage` | Percent | The discount % this rule applies | Confirm which rule gave what discount |

### 14.4 The Summation System

#### 14.4.1 How Totals Are Currently Calculated

ERPNext's `calculate_taxes_and_totals()` runs this sequence:

```
For each item:
    if discount_percentage:
        rate = price_list_rate * (1 - discount_percentage/100)
    elif discount_amount:
        rate = price_list_rate - discount_amount
    amount = rate * qty
    net_amount = amount  (unless additional item discount)

total = sum(item.amount for all items)
net_total = total - doc.discount_amount  (if apply_discount_on == "Net Total")

For each tax:
    tax_amount calculated on net_total

grand_total = net_total + sum(tax.tax_amount)
```

#### 14.4.2 Our New Summation: "What You Would Have Paid"

We need to compute and display the **pre-discount total**:

```
original_total = sum(item.price_list_rate * item.qty for all items where price_list_rate > 0)
savings_total  = original_total - doc.total
```

#### 14.4.3 Improved Summation Formula

```
Per-item savings:
    if item.is_free_item:
        item_savings = item.price_list_rate * item.qty  (entire value is free)
    elif item.price_list_rate and item.price_list_rate > item.rate:
        item_savings = (item.price_list_rate - item.rate) * item.qty
    else:
        item_savings = 0

total_item_savings = sum(item_savings for all items)
Additional discount savings:
    doc_discount = doc.discount_amount or 0

Grand savings:
    total_savings = total_item_savings + doc_discount
```

### 14.5 The Deadline System

#### 14.5.1 Data Chain for Deadlines

```
Pricing Rule (has valid_upto date)
    ↓ applied during set_price_list_and_item_details()
Quotation Item.pricing_rules = '["PRLE-0001", "PRLE-0002"]'  (JSON string)
    ↓ we parse this in the decorator
decorate_quotation_doc() enriches each item with:
    d.offer_deadlines = [
        {"title": "Spring Sale", "valid_upto": "2026-03-01", "days_left": 10},
        ...
    ]
    ↓ template renders deadline badges
```

#### 14.5.2 Where the Lookup Happens

We will modify `decorate_quotation_doc()` in `cart.py` to also fetch pricing rule metadata:

```python
def decorate_quotation_doc(doc):
    for d in doc.get("items", []):
        # ... existing image/route decoration ...
        
        # NEW: Enrich with pricing rule deadlines
        d.offer_details = get_offer_details_for_item(d)
        
    return doc

def get_offer_details_for_item(item):
    """Parse pricing_rules JSON and fetch deadline/title from each Pricing Rule."""
    import json
    offers = []
    
    if not item.pricing_rules:
        return offers
    
    try:
        rule_names = json.loads(item.pricing_rules)
    except (json.JSONDecodeError, TypeError):
        return offers
    
    for rule_name in rule_names:
        rule = frappe.get_cached_doc("Pricing Rule", rule_name)
        offer = {
            "title": rule.title or rule.name,
            "valid_upto": rule.valid_upto,
            "days_left": None,
        }
        if rule.valid_upto:
            from frappe.utils import date_diff, today
            offer["days_left"] = date_diff(rule.valid_upto, today())
        offers.append(offer)
    
    return offers
```

### 14.6 File-by-File Change Map

#### File 1: `webshop/webshop/shopping_cart/cart.py`

**Function:** `decorate_quotation_doc()`

**Change:** Add `offer_details` list to each item by parsing `pricing_rules` and looking up Pricing Rule `title` and `valid_upto`. Also compute and add `doc.original_total`, `doc.total_savings`, `doc.has_any_discount`.

#### File 2: `templates/includes/cart/cart_items.html`

**Macro:** `item_subtotal`

**Change:** Add strike-through original price when discounted, discount percentage badge, "You save" amount, and offer deadline badges.

#### File 3: `templates/includes/cart/cart_payment_summary.html`

**Change:** Add original subtotal (struck through) if discounts exist, savings row, and additional discount row.

#### File 4: `templates/includes/cart/cart_items_total.html`

**Change:** Show original total (struck through) if `doc.has_any_discount`.

#### File 5: `public/scss/webshop_cart.scss`

**Change:** Add styles for discount badges, strike-through, and urgency indicators.

### 14.7 What We Do NOT Need to Change

| Component | Why No Change Needed |
|-----------|---------------------|
| `set_price_list_and_rate()` | Already resets and repopulates `price_list_rate`, `discount_percentage` on every save |
| `apply_cart_settings()` | Already calls `calculate_taxes_and_totals()` which does all the math |
| `update_cart()` | Already re-renders all three template fragments on AJAX update |
| ERPNext Pricing Rules | Standard feature - we just read the results |
| ERPNext Quotation DocType | All fields we need already exist on the standard DocType |
| `shopping_cart.js` | AJAX update already replaces `.cart-items`, `.cart-tax-items`, `.payment-summary` |

### 14.8 Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `price_list_rate` is 0 or null for some items | Medium | Guard with `{% if item.price_list_rate and item.price_list_rate > 0 %}` |
| `pricing_rules` JSON is malformed | Low | Wrap in try/except, return empty list |
| Pricing Rule deleted but still referenced in old Quotation | Low | Use `frappe.db.exists()` check before `get_cached_doc()` |
| Performance hit from looking up Pricing Rules in decorator | Low | `get_cached_doc()` uses Frappe cache; typical cart has <10 items |
| `discount_percentage` is 0 but `discount_amount` is set | Medium | Use `price_list_rate - rate` comparison instead of `discount_percentage` alone |
| Free items with no `price_list_rate` | Medium | Skip savings calculation for free items without `price_list_rate` |
| Multiple pricing rules per item | Medium | Show all offer details; sum savings using `price_list_rate - rate` which is the net effect |

### 14.9 Verification Checklist

After implementation, verify each scenario:

| # | Scenario | Check |
|---|----------|-------|
| 1 | Item with percentage discount | Shows $100 → $80 (-20%), "You save $20" |
| 2 | Item with amount discount | Shows $100 → $85, "You save $15" |
| 3 | Item with no discount | Shows $100 only, no strikethrough, no badge |
| 4 | Free item from pricing rule | Shows "FREE" badge, value counted in savings |
| 5 | Coupon code applied | Savings row in payment summary reflects coupon |
| 6 | Offer expiring in 3 days | Red text "Only 3 days left!" |
| 7 | Offer expiring in 10 days | Warning text "Offer ends March 1, 2026" |
| 8 | Offer with no deadline | No deadline shown, discount still visible |
| 9 | Multiple offers on one item | All offer titles/deadlines listed |
| 10 | Additional discount on total | "Additional Discount -$50" row in payment summary |
| 11 | Cart with mixed discounted/non-discounted items | Only discounted items show strikethrough |
| 12 | AJAX qty update | All discount info re-renders correctly |
| 13 | Mobile responsive | Discount badges readable on small screens |
| 14 | `price_list_rate` is null | Falls back to showing `rate` only, no error |

---

## Critical Components for Frappe Bench Loading

### Package Configuration (`pyproject.toml`)

```toml
[project]
name = "webshop"
description = "Open Source eCommerce Platform"
requires-python = ">=3.10"
dynamic = ["version"]
dependencies = []

[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core.buildapi"
```

### App Hooks (`webshop/hooks.py`)

**Core App Registration** (78 lines of hooks):
```python
app_name = "webshop"
app_title = "Webshop"
app_publisher = "Frappe Technologies Pvt. Ltd."
app_license = "GNU General Public License (v3)"
required_apps = ["payments", "erpnext"]  # Hard dependencies
```

**Website Asset Loading**:
```python
web_include_css = "webshop-web.bundle.css"
web_include_js = "web.bundle.js"
```

**Installation Hook**:
```python
after_install = "webshop.setup.install.after_install"
```

**Website Generators** (Auto-generated pages):
```python
website_generators = ["Website Item", "Item Group"]
```

### Module Declaration (`webshop/modules.txt`)

```
Webshop
```

---

## Discrete Functional Elements

### Core DocTypes (11 Document Types)

1. **Webshop Settings** - Main configuration singleton
2. **Website Item** - Published product linked to ERPNext Item
3. **Wishlist** - User wishlist storage
4. **Item Review** - Customer product reviews
5. **Recommended Items** - Product recommendations
6. **Website Item Tabbed Section** - Additional content tabs
7. **Website Offer** - Promotional offers
8. **Homepage Featured Product** - Homepage showcase
9. **Wishlist Item** - Individual wishlist entries
10. **Override DocTypes** (3): WebshopItem, WebshopItemGroup, PaymentRequest

### Shopping Cart System

- **cart.py** - Core cart logic, Quotation CRUD
- **product_info.py** - Product price/stock API
- **utils.py** - Cart utilities and context updates

### Product Data Engine

- **query.py** - Product search/filter engine
- **filters.py** - Filter builders
- **redisearch_utils.py** - Redis-based full-text search

### Variant Selector

- **utils.py** - Variant attribute filtering
- **item_variants_cache.py** - Redis cache for variant data

### CRUD Event Handlers

- **item/** - Item document events (sync, cache invalidation)
- **quotation/** - Quotation validation
- **price_list/** - Price list changes
- **tax_rule/** - Tax rule validation

### Web Templates

- **hero_slider/** - Homepage hero carousel
- **item_card_group/** - Product card grid layouts
- **product_card/** - Individual product display cards
- **product_category_cards/** - Category navigation cards

### Frontend Assets

- **shopping_cart.js** - Cart UI interactions
- **wishlist.js** - Wishlist UI functionality
- **customer_reviews.js** - Review submission & display
- **webshop-web.bundle.css** - Main stylesheet

---

---

### 2026-05-23 15:19 — cwp vs etest Deployment Gap

**Root cause of `/all-products` 404 on etest (t3.comfac-it.com):**

cwp is NOT installed for the etest site. This is the single root cause of all observed failures.

| Signal | State | Explanation |
|--------|-------|-------------|
| `/all-products` | 404 | Route handler at `webshop/www/all-products/` missing — cwp not installed |
| `Website Item` DocType | DoesNotExistError | cwp not installed; DocType not in DB |
| `Shopping Cart Settings` | DoesNotExistError | Same cause |
| `Webshop Settings` | DoesNotExistError | Same cause |
| Items with `published_in_website=1` | 89 items ✅ | Replicated from ecit |
| Website Item records | 0 | No cwp = no Website Item table |
| cwp in bench `apps/` | ✅ Present | App directory exists on bench |
| cwp installed for site | ❌ | `bench list-apps` confirms: only frappe, erpnext, hrms, print_designer |
| Webshop assets served | ✅ | CSS/JS bundles at `/assets/webshop/` — app is in bench even if not installed for site |

**cwp = Comfac's standalone fork of fws (95% identical):**
- cwp is 95% upstream Frappe WebShop — all routing, DocTypes, cart logic, checkout unchanged
- The 5% delta is Comfac's cart UI additions (discount display, savings summary, mini-cart)
- cwp is NOT a separate webshop engine — it IS fws with Comfac's UI layer on top
- No upstream fws will be installed alongside cwp; cwp replaces it entirely

**Install blocker — `payments` dependency:**
`hooks.py` line 11: `required_apps = ["payments", "erpnext"]`
The `payments` app is not in the etest bench. Attempting `bench install-app webshop` failed with:
```
No module named 'payments'
An error occurred while installing webshop
```
Resolution options:
1. Add `payments` to the bench via Frappe Cloud dashboard, then install cwp
2. Remove `payments` from `required_apps` in `hooks.py` (safe only if no payment gateway features used)

**Note on earlier 260523 log entries:**
A previous log entry from this date stated "All items accessible via /all-products route on webshop"
— this was incorrect. `/all-products` returns 404 on etest. The analysis above is the authoritative
finding based on direct API and SSH verification.

**Next actions:**
1. Resolve `payments` blocker (dashboard install or remove from `required_apps`)
2. Install cwp: `bench --site test260204.s.frappe.cloud install-app webshop`
3. Run `create_website_items.py` patch or bench console script using `make_website_item()` to
   create Website Item records from the 89 items with `published_in_website=1`
4. Verify `/all-products` renders and cart flow works end-to-end on etest

*Analysis compiled from Frappe Webshop codebase and Comfac Webshop Wiki documentation*
