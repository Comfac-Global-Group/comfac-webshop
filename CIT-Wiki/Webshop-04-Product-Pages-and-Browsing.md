# 04 - Product Pages & Browsing

**Parent:** [Webshop Index](Webshop-Index)  
**Previous:** [03 - Shopping Cart & Quotation Deep Dive](Webshop-03-Shopping-Cart-Quotation-Deep-Dive)  
**Next:** [05 - Variant Selector](Webshop-05-Variant-Selector)  
**Source:** [Comfac Webstore Wiki - Chapter 04](https://github.com/Comfac-Global-Group/comfac-webstore/wiki/04-Product-Pages-and-Browsing)

---

## Product Listing Pages

### /all-products

**Files:** `www/all-products/index.py`, `index.html`, `index.js`

- Server-side: builds filter context from Webshop Settings
- Client-side: JS calls `webshop.webshop.api.get_product_filter_data` API
- Uses `ProductQuery` engine for filtered product search
- Supports: search, field filters (item_group, brand), attribute filters (Color, Size), discount filters
- Pagination via `products_per_page` setting

### /shop-by-category

**Files:** `www/shop-by-category/index.py`, `index.html`, `index.js`

- Renders category cards based on Webshop Settings filter_fields
- Supports slideshow from Website Slideshow
- Uses `category_card_section.html` template

### Item Group Pages (generated)

**File:** `templates/generators/item_group.html`

- Auto-generated pages for each Item Group with `show_in_website=1`
- Shows: slideshow, description, product grid, filters
- Product listing loaded via same JS as /all-products

## Individual Product Pages

### Item Page (generated)

**Files:** `templates/generators/item/item.html` + sub-templates

Sub-templates:

- `item_image.html` - Product image carousel
- `item_details.html` - Title, item code, item group, description
- `item_add_to_cart.html` - Price display, qty selector, add to cart (non-variant items)
- `item_configure.html` + `item_configure.js` - Variant selector (template items)
- `item_specifications.html` - Item attributes table
- `item_reviews.html` - Customer reviews
- `item_inquiry.html` + `item_inquiry.js` - Product inquiry form

### Product Info API

**File:** `webshop/shopping_cart/product_info.py`

`get_product_info_for_website(item_code)` returns:

- price (formatted_price, price_list_rate, currency)
- qty in cart
- stock status (in_stock, stock_qty, on_backorder)
- UOM info

## Product Data Engine

### Query Engine (`product_data_engine/query.py`)

- `ProductQuery.query()` - main search/filter method
- Supports: text search, field filters, attribute filters
- Returns items with price and discount info
- Falls back to legacy search if RediSearch unavailable

### Filter Builder (`product_data_engine/filters.py`)

- `ProductFiltersBuilder` - builds filter UI data
- Field filters from Webshop Settings
- Attribute filters from Item Variant Attributes
- Discount filters from pricing rules

## Web Templates (Blocks)

- `hero_slider/` - Homepage hero carousel
- `product_card/` - Individual product card
- `product_category_cards/` - Category card grid
- `item_card_group/` - Group of item cards

---

**Navigation:** [Webshop Index](Webshop-Index) | [Previous: 03 - Shopping Cart](Webshop-03-Shopping-Cart-Quotation-Deep-Dive) | [Next: 05 - Variant Selector](Webshop-05-Variant-Selector)
