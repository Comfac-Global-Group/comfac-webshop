# 02 - DocTypes

**Parent:** [Webshop Index](Webshop-Index)  
**Previous:** [01 - Architecture Overview](Webshop-01-Architecture-Overview)  
**Next:** [03 - Shopping Cart & Quotation Deep Dive](Webshop-03-Shopping-Cart-Quotation-Deep-Dive)  
**Source:** [Comfac Webshop Wiki - Chapter 02](https://github.com/Comfac-Global-Group/comfac-webshop/wiki/02-DocTypes)

---

## Custom DocTypes (defined in webshop)

### Webshop Settings (Singleton)

**Path:** `webshop/webshop/doctype/webshop_settings/`

Main configuration for the webshop:
- Fields: company, price_list, default_customer_group, quotation_series
- Toggles: enabled, show_price, show_stock_availability, enable_checkout, enable_wishlist
- Filter settings, products_per_page, slideshow
- Coupon code settings, guest price visibility

### Website Item

**Path:** `webshop/webshop/doctype/website_item/`

Published product linked to an ERPNext `Item`:
- Fields: item_code, web_item_name, route, description, website_image, thumbnail
- Website warehouse, on_backorder flag
- Acts as a website generator (auto-creates web pages)
- Tabbed sections for additional content

### Wishlist

**Path:** `webshop/webshop/doctype/wishlist/`

User wishlist storage with child table of wished items.

### Item Review

**Path:** `webshop/webshop/doctype/item_review/`

Customer product reviews and ratings.

### Recommended Items

**Path:** `webshop/webshop/doctype/recommended_items/`

Product recommendations (child table).

### Website Item Tabbed Section

**Path:** `webshop/webshop/doctype/website_item_tabbed_section/`

Additional content tabs on product pages.

## Override DocTypes

**Path:** `webshop/webshop/doctype/override_doctype/`

- **WebshopItem** (extends Item) - adds website publishing behavior
- **WebshopItemGroup** (extends Item Group) - adds website page generation, child group utilities
- **PaymentRequest** (extends Payment Request) - customized payment handling

## ERPNext DocTypes Used

These are not defined in webshop but are central to its operation:

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

**Navigation:** [Webshop Index](Webshop-Index) | [Previous: 01 - Architecture](Webshop-01-Architecture-Overview) | [Next: 03 - Shopping Cart](Webshop-03-Shopping-Cart-Quotation-Deep-Dive)
