# Templates & Frontend

## JavaScript Files

| File | Purpose | Loaded |
|------|---------|--------|
| `public/js/shopping_cart.js` | Core cart logic: update_cart, set_cart_count, navbar dropdown, add-to-cart binding | All pages (web.bundle.js) |
| `public/js/init.js` | Bundle entry point | All pages |
| `public/js/wishlist.js` | Wishlist add/remove actions | All pages |
| `public/js/customer_reviews.js` | Review submission/display | All pages |
| `public/js/product_ui/views.js` | Product grid/list view toggle | Product pages |
| `public/js/product_ui/list.js` | List view renderer | Product pages |
| `public/js/product_ui/grid.js` | Grid view renderer | Product pages |
| `public/js/product_ui/search.js` | Product search handler | Product pages |
| `public/js/override/item.js` | Item doctype form customization | ERPNext desk |
| `public/js/override/homepage.js` | Homepage customization | ERPNext desk |
| `templates/pages/cart.js` | Cart page specific: qty change, remove item, place order, coupon | /cart only |
| `templates/generators/item/item_configure.js` | Variant configurator | Item pages |
| `templates/generators/item/item_inquiry.js` | Product inquiry form | Item pages |
| `templates/pages/order.js` | Order page interactions | /orders only |
| `www/all-products/index.js` | Product listing, filters, pagination | /all-products |
| `www/shop-by-category/index.js` | Category browsing | /shop-by-category |

## Template Hierarchy

### Full Pages (`templates/pages/`)
- `cart.html` - Shopping cart (extends `templates/web.html`)
- `order.html` - Order detail page
- `wishlist.html` - Wishlist page
- `product_search.html` - Search results
- `customer_reviews.html` - Reviews page

### Generated Pages (`templates/generators/`)
- `item/item.html` - Product detail (Website Item generator)
- `item_group.html` - Category page (Item Group generator)

### Includes (`templates/includes/`)

#### Cart components (`includes/cart/`)
- `cart_items.html` - Line item rows in cart table
- `cart_items_total.html` - Net total footer row
- `cart_payment_summary.html` - Right sidebar: net total, taxes, grand total
- `cart_dropdown.html` - Navbar cart dropdown wrapper
- `cart_items_dropdown.html` - Navbar cart item rows
- `coupon_code.html` - Applied coupon badge
- `cart_address.html` - Address selection (shipping + billing)
- `address_card.html` - Single address display card
- `address_picker_card.html` - Address in picker dialog
- `cart_macros.html` - Address display macro
- `place_order.html` - Place order / Request quote button

#### Order components (`includes/order/`)
- `order_macros.html` - Item display macros for orders
- `order_taxes.html` - Tax breakdown with savings display

#### Other
- `macros.html` - Shared macros (product_image, filters)
- `navbar/navbar_items.html` - Cart icon in navbar
- `product_page.js` - Shared product page JS

## SCSS
- `public/scss/webshop-web.bundle.scss` - Main stylesheet
- `public/scss/webshop_cart.scss` - Cart-specific styles

## Bundles
- `public/web.bundle.js` - Combined JS for web pages (built by frappe build)
- CSS bundle built from SCSS via frappe build

---

## Related Wiki Pages

- [03 - Shopping Cart & Quotation Deep Dive](03-Shopping-Cart-Quotation-Deep-Dive.md) - What data each cart template reads from the Quotation
- [04 - Product Pages & Browsing](04-Product-Pages-and-Browsing.md) - How product page templates work
- [10 - Feature Gap: Cart Discounts](10-Feature-Gap-Cart-Discounts.md) - Which template files need changes for discount display
- [14 - Hypothesis: Discount & Deadline Visibility](14-Hypothesis-Discount-Deadline-Visibility.md) - File-by-file change map for template modifications
- [Back to Home](00-Home.md)
