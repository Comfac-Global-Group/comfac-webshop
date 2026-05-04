# Comfac Webshop

**Open Source E-commerce Platform with Enhanced Discount Visibility & System Builder**

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/Comfac-Global-Group/comfac-webshop)
[![Base Project](https://img.shields.io/badge/Base-Frappe%20Webshop-green)](https://github.com/frappe/webshop)
[![ERPNext](https://img.shields.io/badge/Powered%20by-ERPNext-orange)](https://erpnext.com)

---

## Quick Links

| Resource | Link | Description |
|----------|------|-------------|
| **GitHub Repository** | [Comfac-Global-Group/comfac-webshop](https://github.com/Comfac-Global-Group/comfac-webshop) | Source code, issues, and pull requests |
| **Base Project** | [frappe/webshop](https://github.com/frappe/webshop) | Upstream Frappe Webshop project |
| **ERPNext Docs** | [E-commerce Setup Guide](https://docs.erpnext.com/docs/user/manual/en/set_up_e_commerce) | Official ERPNext e-commerce documentation |
| **Frappe Framework** | [frappe.io](https://frappe.io) | Framework documentation |

---

## Project Overview

Comfac Webshop is a **fork of Frappe Webshop** customized for Comfac Global Group's needs. It extends the base e-commerce platform with two major feature areas:

### 🎯 Key Enhancements

1. **Discount Visibility & Offer Urgency** - Make promotions transparent and create urgency
   - Show original vs. discounted prices in cart
   - Display "You Save" amounts per item and total
   - Urgency indicators for expiring offers (deadline countdowns)
   - Visual badges for active promotions

2. **System Builder** - Multi-component product configurator
   - Build servers, desktops, maker kits from compatible components
   - Real-time compatibility checking
   - Save and share configurations
   - Bundle pricing with discounts

### 📊 Project Stats

- **Base:** Frappe Webshop (172 files, ~988KB)
- **Dependencies:** frappe, erpnext, payments
- **Module:** Single "Webshop" module
- **Python:** >= 3.10
- **Build System:** Flit

---

## Documentation Index

### 🔧 Understanding the Codebase

These chapters provide deep technical understanding of how the webshop works:

| # | Chapter | Description | Key Topics |
|---|---------|-------------|------------|
| [01](ANALYSIS.md#01---architecture-overview) | **Architecture Overview** | Framework stack, app structure, data flow | Frappe Framework, ERPNext integration, Cart=Quotation design |
| [02](ANALYSIS.md#02---doctypes) | **DocTypes** | All custom DocTypes and key ERPNext DocTypes | Webshop Settings, Website Item, Wishlist, Overrides |
| [03](ANALYSIS.md#03---shopping-cart--quotation-deep-dive) | **Shopping Cart & Quotation Deep Dive** | Detailed breakdown of cart UI and hidden fields | Cart-quotation relationship, AJAX updates, decorator function |
| [04](ANALYSIS.md#04---product-pages--browsing) | **Product Pages & Browsing** | Product listing, search engine, filters | /all-products, /shop-by-category, Item Group pages |
| [05](ANALYSIS.md#05---variant-selector) | **Variant Selector** | How item variants/attributes work | Template items, configurator UI, Redis caching |
| [06](ANALYSIS.md#06---pricing--discounts) | **Pricing & Discounts** | Price lists, pricing rules, coupon codes | ERPNext pricing engine, hidden discount fields |
| [07](ANALYSIS.md#07---checkout--orders) | **Checkout & Orders** | Place order flow, payment, order tracking | Sales Order creation, Payment Request |
| [08](ANALYSIS.md#08---templates--frontend) | **Templates & Frontend** | Complete map of Jinja templates, JS, SCSS | Cart templates, product pages, includes |
| [09](ANALYSIS.md#09---hooks--events) | **Hooks & Events** | doc_events, class overrides, CRUD handlers | hooks.py structure, event handlers |

### ✨ Feature Requirements & Plans

These sections define the missing features and enhancement plans:

| # | Chapter | Description | Status |
|---|---------|-------------|--------|
| [10](ANALYSIS.md#10---feature-gap-cart-discounts-from-wiki) | **Feature Gap: Cart Discounts** | Analysis of why discounts don't show, files to modify | 🔴 Not Implemented |
| [11](ANALYSIS.md#11---feature-plan-system-builder-from-wiki) | **Feature Plan: System Builder** | Multi-component configurator design, new DocTypes | 🔴 Not Implemented |

### 🚀 Development & Deployment

Guidelines for testing and implementing features:

| # | Chapter | Description | Key Topics |
|---|---------|-------------|------------|
| [12](ANALYSIS.md#12---staging-sandbox-deployment-from-wiki) | **Staging Sandbox: Testing & Deployment** | How to clone production, validate seamless replacement | Phase 0/1/2 approach, validation checklist |
| [13](ANALYSIS.md#13---discount-visibility--offer-urgency-specifications-from-wiki) | **Discount Visibility & Offer Urgency** | Detailed UI specs, urgency indicators, test scenarios | Urgency levels, deadline display, mockups |
| [14](ANALYSIS.md#14---hypothesis-making-discounts-and-deadlines-visible-from-wiki) | **Hypothesis: Discount & Deadline Visibility** | Exact implementation plan, field targeting, risk assessment | File-by-file changes, summation formulas, verification |

---

## Missing Features Status

### 🔴 Feature 1: Cart Discount Visibility

**Status:** Not Implemented | **Priority:** High

**Problem:** Discounts are calculated on the Quotation but hidden from customers. They see only final prices without understanding savings or offer deadlines.

**What's Missing:**
- ❌ Original price (`price_list_rate`) display with strikethrough
- ❌ Discount percentage badges (-20%)
- ❌ "You save" amounts per item
- ❌ Total savings in payment summary
- ❌ Offer deadline/urgency display
- ❌ Visual indicators for expiring promotions

**What EXISTS on Quotation (Backend):**
- ✅ `price_list_rate` - Original price
- ✅ `discount_percentage` - Discount %
- ✅ `pricing_rules` - JSON of applied rules
- ✅ `discount_amount` - Additional order discount
- ✅ All calculated by ERPNext's pricing engine

**Files to Modify:**
1. `webshop/webshop/shopping_cart/cart.py` - Enhance decorator
2. `templates/includes/cart/cart_items.html` - Add per-item display
3. `templates/includes/cart/cart_payment_summary.html` - Add savings total
4. `templates/includes/cart/cart_items_total.html` - Add pre-discount total
5. `templates/includes/cart/cart_items_dropdown.html` - Update mini-cart
6. `public/scss/webshop_cart.scss` - Add styles

**Implementation Approach:**
- Purely frontend/template changes
- No backend calculation changes needed
- Read existing hidden fields from Quotation
- Enrich decorator to pass offer metadata

**See:** [Chapter 10](ANALYSIS.md#10---feature-gap-cart-discounts-from-wiki) | [Chapter 13](ANALYSIS.md#13---discount-visibility--offer-urgency-specifications-from-wiki) | [Chapter 14](ANALYSIS.md#14---hypothesis-making-discounts-and-deadlines-visible-from-wiki)

---

### 🔴 Feature 2: System Builder

**Status:** Not Implemented | **Priority:** High

**Problem:** No way to configure multi-component systems (servers, desktops, maker kits) with compatibility checking and bundle pricing.

**What's Missing:**
- ❌ System Builder Template DocType
- ❌ Component Slot child table
- ❌ Compatibility Rule engine
- ❌ Saved Configuration storage
- ❌ Customer configurator UI
- ❌ Bundle discount application
- ❌ Configuration sharing via URL

**New DocTypes Required:**

1. **System Builder Template**
   - Template name, category, image
   - Child table: Component Slots

2. **Component Slot (Child Table)**
   - Slot name, required flag
   - Min/max quantity
   - Allowed Item Groups/Items
   - Default selection

3. **Compatibility Rule**
   - Rule type: Requires, Excludes, Max Qty, Min Qty
   - Source/target slots with filters
   - Error messages

4. **Saved Configuration**
   - Customer reference
   - Selected items per slot
   - Share token for URLs

**Implementation Phases:**

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Phase 1: Foundation** | Weeks 1-4 | DocTypes, basic UI, add to cart |
| **Phase 2: Compatibility** | Weeks 5-8 | Rule engine, real-time filtering |
| **Phase 3: Save & Share** | Weeks 9-12 | Dashboard, share URLs, cloning |
| **Phase 4: Advanced** | Future | Power budgets, AI recommendations |

**See:** [Chapter 11](ANALYSIS.md#11---feature-plan-system-builder-from-wiki)

---

## Development Workflow

### Phase 0: Baseline Validation (REQUIRED)

**Before ANY feature work:**

1. Clone production ERPNext instance to staging
2. Install comfac-webshop fork on staging
3. Validate seamless replacement:
   - Site loads without errors
   - Product listing works
   - Add to cart works
   - Checkout flow works
   - No regressions from base webshop
4. Create backup of validated staging

**⚠️ Do not skip Phase 0. This is the foundation for all feature work.**

### Phase 1: Feature Implementation

1. Clone validated staging to experiment environment
2. Implement features in experiment environment
3. Test all scenarios thoroughly
4. Document changes

### Phase 2: Production Merge

1. All validation checks pass
2. No regressions detected
3. Documentation complete
4. Rollback plan ready

**See:** [Chapter 12](ANALYSIS.md#12---staging-sandbox-deployment-from-wiki) for detailed deployment guide

---

## Key Technical Insights

### 💡 The Cart IS a Quotation

The webshop has no separate "cart" table. The shopping cart is literally an ERPNext **Quotation** document with `order_type="Shopping Cart"` and `docstatus=0` (Draft).

This means:
- All ERPNext pricing features work automatically
- Discounts ARE calculated (just hidden)
- Taxes work out of the box
- No custom cart logic needed

**See:** [Chapter 03](ANALYSIS.md#03---shopping-cart--quotation-deep-dive)

### 💡 Discount Fields Already Exist

Every Quotation Item already has these fields populated by ERPNext:
- `price_list_rate` - Original price
- `rate` - Final discounted price
- `discount_percentage` - Applied discount %
- `pricing_rules` - JSON of applied Pricing Rules

We just need to DISPLAY them in templates.

**See:** [Chapter 14](ANALYSIS.md#14---hypothesis-making-discounts-and-deadlines-visible-from-wiki#part-1-the-fields-we-will-target)

### 💡 No Backend Changes Needed

For discount visibility, we only need to:
1. Read existing fields (no new DB queries)
2. Enrich decorator to pass metadata
3. Update templates to display data

The ERPNext pricing engine does all the heavy lifting.

---

## Repository Structure

```
comfac-webshop/
├── README.md                          # Project overview
├── LICENSE                            # GNU GPL v3
├── pyproject.toml                     # Package config (Flit)
├── webshop.png                        # Logo
│
├── webshop/                           # Main application
│   ├── hooks.py                       # App hooks (78 lines)
│   ├── modules.txt                    # Module: "Webshop"
│   ├── patches.txt                    # Migration patches
│   ├── patches/                       # Migration scripts
│   ├── setup/                         # Post-install setup
│   ├── config/                        # App configuration
│   │
│   ├── public/                        # Static assets
│   │   ├── js/                        # Frontend JavaScript
│   │   │   ├── shopping_cart.js       # Cart interactions [MODIFY FOR DISCOUNTS]
│   │   │   ├── wishlist.js            # Wishlist functionality
│   │   │   └── product_ui/            # Product page JS
│   │   └── scss/                      # Stylesheets
│   │       └── webshop_cart.scss      # Cart styles [MODIFY FOR DISCOUNTS]
│   │
│   ├── templates/                     # Jinja2 templates
│   │   ├── pages/                     # Full pages
│   │   │   ├── cart.html              # Shopping cart
│   │   │   ├── order.html             # Order details
│   │   │   └── wishlist.html          # Wishlist
│   │   ├── generators/                # Auto-generated pages
│   │   │   ├── item_group.html        # Category pages
│   │   │   └── item/                  # Product pages
│   │   └── includes/                    # Partial templates
│   │       └── cart/                    # Cart components [MODIFY FOR DISCOUNTS]
│   │           ├── cart_items.html              # Line items
│   │           ├── cart_items_total.html        # Subtotal
│   │           ├── cart_payment_summary.html    # Payment summary
│   │           └── cart_items_dropdown.html     # Mini-cart
│   │
│   └── webshop/                       # Python modules
│       ├── doctype/                   # Custom DocTypes
│       │   ├── webshop_settings/        # Settings singleton
│       │   ├── website_item/            # Published products
│       │   ├── wishlist/                # User wishlists
│       │   ├── item_review/             # Product reviews
│       │   └── override_doctype/        # ERPNext overrides
│       │       ├── item.py              # Item override
│       │       ├── item_group.py        # Item Group override
│       │       └── payment_request.py   # Payment override
│       ├── shopping_cart/             # Cart logic
│       │   ├── cart.py                  # Core cart logic [MODIFY FOR DISCOUNTS]
│       │   ├── product_info.py          # Product info API
│       │   └── utils.py                 # Cart utilities
│       ├── variant_selector/          # Product variants
│       │   ├── utils.py                 # Variant logic
│       │   └── item_variants_cache.py   # Redis caching
│       ├── product_data_engine/         # Search & filtering
│       │   ├── query.py                 # Search engine
│       │   └── filters.py               # Filter builders
│       ├── crud_events/               # Document event handlers
│       │   ├── item/                    # Item events
│       │   ├── quotation/               # Quotation events
│       │   ├── price_list/              # Price list events
│       │   └── tax_rule/                # Tax rule events
│       ├── web_template/              # Web block templates
│       └── api.py                     # Public API endpoints
│
└── wiki/                              # Documentation (this repo)
    ├── Home.md                        # This index page
    ├── ANALYSIS.md                    # Full technical analysis
    └── PRD.md                         # Product requirements
```

---

## Contributing

### For Developers

1. **Read the relevant wiki chapters** before making changes
   - Start with [Chapter 01](ANALYSIS.md#01---architecture-overview) for architecture
   - Read [Chapter 03](ANALYSIS.md#03---shopping-cart--quotation-deep-dive) for cart details
   - Check feature chapters for implementation plans

2. **Follow the data flow**
   - Cart is a Quotation
   - All pricing goes through ERPNext
   - Templates render Quotation fields

3. **Use git context in commits**
   ```
   Implement cart discount display (see wiki/10-Feature-Gap-Cart-Discounts.md)
   ```

4. **Update documentation**
   - Add implementation notes to relevant chapters
   - Update this index if adding new features

### For AI Agents

When asking an AI (like Claude Code) to modify the webshop:

1. **Point the agent to [ANALYSIS.md](ANALYSIS.md) first** so it understands the architecture
2. **Reference specific chapters** for the area being modified
3. **Follow the data flow** - the cart is a Quotation, all pricing goes through ERPNext
4. **Check feature gap analysis** - see if there's already a chapter analyzing what needs to change

**Example prompt:**
```
Help me implement cart discount visibility in the Comfac Webshop. 

See the technical analysis at:
- ANALYSIS.md#10---feature-gap-cart-discounts-from-wiki for what needs to change
- ANALYSIS.md#14---hypothesis-making-discounts-and-deadlines-visible-from-wiki for exact implementation details

The cart templates are in templates/includes/cart/
The cart logic is in webshop/webshop/shopping_cart/cart.py

Key fields we need to display:
- price_list_rate (original price)
- discount_percentage
- pricing_rules (for offer deadlines)

All these fields already exist on the Quotation - we just need to show them.
```

---

## Resources & References

### Official Documentation

- [ERPNext E-commerce Setup](https://docs.erpnext.com/docs/user/manual/en/set_up_e_commerce)
- [Frappe Framework Documentation](https://docs.frappe.io)
- [Frappe Webshop Repository](https://github.com/frappe/webshop)

### Related Projects

- [ERPNext](https://github.com/frappe/erpnext) - ERP system
- [Frappe Framework](https://github.com/frappe/frappe) - Web framework
- [Payments App](https://github.com/frappe/payments) - Payment integration

### Comfac Resources

- [Comfac Webshop Repository](https://github.com/Comfac-Global-Group/comfac-webshop)
- [Comfac Global Group](https://github.com/Comfac-Global-Group)

---

## Document Information

**Last Updated:** March 2026  
**Maintained by:** Comfac Global Group Development Team  
**License:** GNU General Public License v3  
**Status:** Active Development

---

**Navigation:** [ANALYSIS.md](ANALYSIS.md) (Technical Analysis) | [PRD.md](PRD.md) (Requirements) | [GitHub](https://github.com/Comfac-Global-Group/comfac-webshop)
