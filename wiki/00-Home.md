# Comfac Webshop Wiki

## Purpose

This wiki exists to **break down every aspect of how this webshop works** so that anyone - developer, contributor, or AI agent - can understand, modify, and extend it in a **targeted, clean, traceable, and auditable** way.

Every change made to this codebase should be:
- **Informed** by the documentation here, so modifications are precise rather than guesswork
- **Traceable** via git commits with clear context linking back to wiki sections
- **Auditable** by others who can review changes against the documented architecture
- **Commented** with enough context that anyone following - whether they fork, contribute, or suggest improvements - can understand the "why" behind every decision

This wiki is designed to work **hand-in-hand with AI agents** (like Claude Code). By providing comprehensive documentation of the codebase structure, data flows, and feature gaps, an AI assistant can guide users through modifications with precision - knowing exactly which files to touch, what data is available, and what the side effects will be.

**If you're forking this repo:** Start here. Read the architecture overview, understand the cart-quotation relationship, then dive into whichever feature area you need. The wiki will tell you exactly where to look and what to change.

---

## Overview

Comfac Webshop is a **Frappe/ERPNext app** that provides an open-source e-commerce storefront. It extends ERPNext's selling module (Quotation, Sales Order) with a customer-facing web shop including product browsing, variant selection, shopping cart, checkout, wishlists, and coupon support.

This is a **fork** of the official [Frappe Webshop](https://github.com/frappe/webshop), customized for Comfac's needs with planned enhancements around discount visibility and a System Builder configurator.

**Required apps:** `frappe`, `erpnext`, `payments`

**Codebase size:** ~172 files, ~988KB (excluding `.git`)

---

## Table of Contents

### Understanding the Codebase

| # | Page | Description |
|---|------|-------------|
| 01 | [Architecture Overview](01-Architecture-Overview.md) | Framework stack, app structure, data flow, how webshop integrates with ERPNext |
| 02 | [DocTypes](02-DocTypes.md) | All custom DocTypes (Website Item, Webshop Settings, Wishlist, etc.) and key ERPNext DocTypes used |
| 03 | [Shopping Cart & Quotation Deep Dive](03-Shopping-Cart-Quotation-Deep-Dive.md) | **Detailed breakdown** of the cart UI, every field it reads from the Quotation, what's shown vs hidden, AJAX update cycle |
| 04 | [Product Pages & Browsing](04-Product-Pages-and-Browsing.md) | Product listing, search engine, filters, individual item pages, category pages |
| 05 | [Variant Selector](05-Variant-Selector.md) | How item variants/attributes work, the configurator UI, Redis caching |
| 06 | [Pricing & Discounts](06-Pricing-and-Discounts.md) | Price lists, pricing rules, coupon codes, where discounts are calculated vs displayed |
| 07 | [Checkout & Orders](07-Checkout-and-Orders.md) | Place order flow, payment request, Sales Order creation, stock validation |
| 08 | [Templates & Frontend](08-Templates-and-Frontend.md) | Complete map of Jinja templates, JS files, SCSS, bundles |
| 09 | [Hooks & Events](09-Hooks-and-Events.md) | doc_events, class overrides, CRUD event handlers, session hooks |

### Feature Gaps & Planned Enhancements

| # | Page | Description |
|---|------|-------------|
| 10 | [Feature Gap: Cart Discounts](10-Feature-Gap-Cart-Discounts.md) | Analysis of why discounts don't show in cart, exactly which files need changes, proposed code |
| 11 | [Feature Plan: System Builder](11-Feature-Plan-System-Builder.md) | Multi-component configurator design - new DocTypes, compatibility engine, UI flow, implementation phases |

### Development & Deployment

| # | Page | Description |
|---|------|-------------|
| 12 | [Staging Sandbox: Testing & Deployment](12-Staging-Sandbox-Deployment.md) | How to clone production, install the fork, validate seamless replacement, set up test data, iteration workflow |
| 13 | [Discount Visibility & Offer Urgency](13-Discount-Visibility-and-Urgency.md) | Detailed UI specs for showing discounts, offer deadlines, urgency indicators, sample test scenarios |
| 14 | [Hypothesis: Discount & Deadline Visibility](14-Hypothesis-Discount-Deadline-Visibility.md) | **Implementation hypothesis** - exact fields targeted, summation formulas, file-by-file change map, risk assessment |

---

## Key Directories

```
comfac-webshop/
  wiki/                               # THIS WIKI - documentation for contributors
  webshop/
    hooks.py                          # App hooks, doc_events, overrides
    __init__.py                       # Version
    modules.txt                       # Module: "Webshop"
    patches.txt                       # Migration patches
    patches/                          # Data migration scripts
    setup/                            # Post-install setup
    config/                           # (empty, placeholder)
    public/
      js/                             # Frontend JS (shopping_cart, wishlist, product UI)
      scss/                           # Styles
      images/                         # Static assets
    templates/
      pages/                          # Full pages: cart, order, wishlist, search
      generators/                     # Auto-generated pages: item, item_group
      includes/                       # Partials: cart components, macros, navbar
    www/
      all-products/                   # /all-products listing page
      shop-by-category/               # /shop-by-category page
    webshop/
      doctype/                        # All custom DocTypes
        webshop_settings/             # Main settings singleton
        website_item/                 # Published product (links to Item)
        wishlist/                     # User wishlists
        override_doctype/             # Class overrides for Item, Item Group, Payment Request
      shopping_cart/
        cart.py                       # Core cart logic (Quotation CRUD)
        product_info.py               # Product price/stock API
      variant_selector/
        utils.py                      # Variant attribute filtering
        item_variants_cache.py        # Redis cache for variant data
      product_data_engine/
        query.py                      # Product search/filter engine
        filters.py                    # Filter builders
      crud_events/                    # Hooks on Item, Quotation, Price List, Tax Rule
      api.py                          # Public API endpoints
      web_template/                   # Web block templates (hero slider, product cards)
```

---

## How to Use This Wiki with AI Agents

1. **Point the agent here first.** When asking an AI to modify the webshop, reference the relevant wiki page so it understands the architecture before making changes.

2. **Follow the data flow.** The cart is a Quotation. All pricing goes through ERPNext's pricing engine. Templates render Quotation fields. Understanding this chain prevents surprises.

3. **Check the feature gap analysis.** Before implementing something, see if there's already a wiki page analyzing exactly what needs to change and where.

4. **Document your changes.** When you add a feature, update or add a wiki page. This keeps the knowledge base current for the next contributor.

5. **Use git context.** Commit messages should reference wiki sections: "Implement cart discount display (see wiki/10-Feature-Gap-Cart-Discounts.md)"

---

## Contributing

- Fork this repo
- Read the relevant wiki sections for the area you want to modify
- Make changes in a feature branch
- Update wiki documentation to reflect your changes
- Submit a PR with clear description linking to wiki context
- Reviewers can audit changes against the documented architecture
