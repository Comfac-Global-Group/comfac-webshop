# CIT Wiki Documentation - Comfac Webshop

This folder contains the complete CIT Wiki documentation for the Comfac Webshop project.

## File Structure

### Main Index
- **Webshop-Index.md** - Main index page that links to all chapters and summarizes missing features

### Core Architecture & Codebase (Chapters 01-09)
These chapters explain how the webshop works:

1. **Webshop-01-Architecture-Overview.md** - Framework stack, app integration, data flow
2. **Webshop-02-DocTypes.md** - Custom DocTypes and ERPNext DocTypes used
3. **Webshop-03-Shopping-Cart-Quotation-Deep-Dive.md** - Cart-quotation relationship, hidden fields
4. **Webshop-04-Product-Pages-and-Browsing.md** - Product listings, search, Item Group pages
5. **Webshop-05-Variant-Selector.md** - Item variants, configurator UI, Redis caching
6. **Webshop-06-Pricing-and-Discounts.md** - Price lists, pricing rules, coupon codes
7. **Webshop-07-Checkout-and-Orders.md** - Place order flow, payment, order tracking
8. **Webshop-08-Templates-and-Frontend.md** - Jinja templates, JS, SCSS structure
9. **Webshop-09-Hooks-and-Events.md** - App hooks, doc_events, CRUD handlers

### Feature Requirements & Plans (Chapters 10-11)
These chapters define features that need to be developed:

10. **Webshop-10-Feature-Gap-Cart-Discounts.md** - Analysis of missing discount visibility in cart
11. **Webshop-11-Feature-Plan-System-Builder.md** - Multi-component configurator design

### Development & Deployment (Chapters 12-14)
Implementation guides:

12. **Webshop-12-Staging-Sandbox-Deployment.md** - Testing environment, Phase 0/1/2 approach
13. **Webshop-13-Discount-Visibility-and-Urgency.md** - UI specs, urgency indicators, test scenarios
14. **Webshop-14-Hypothesis-Discount-Deadline-Visibility.md** - Exact implementation plan with code

## How to Use This Wiki

### For Developers
1. Start with the **Webshop-Index** for an overview
2. Read chapters 01-09 to understand the codebase
3. Check chapters 10-11 for feature requirements
4. Follow chapters 12-14 for implementation guidance

### For AI Agents / Claude Code
When working on the webshop codebase:

1. **First, read the relevant chapter** to understand the area being modified
2. **Use the chapter structure** to navigate the codebase
3. **Follow the data flow** described in Chapter 01 and 03
4. **Check feature gap analysis** in Chapters 10-11 for planned changes

### For Project Managers
- Use the **Webshop-Index** to see status of missing features
- Check Chapter 10 and 11 for detailed feature specifications
- Review Chapter 12 for deployment procedures

## Key Insights from the Documentation

### 💡 The Cart IS a Quotation
The webshop has no separate "cart" table. The shopping cart is literally an ERPNext **Quotation** document. All pricing, taxes, and discounts flow through ERPNext's standard logic.

### 💡 Discount Fields Already Exist
Every Quotation Item already has these fields populated by ERPNext:
- `price_list_rate` - Original price
- `rate` - Final price
- `discount_percentage` - Discount %
- `pricing_rules` - JSON of applied Pricing Rules

For discount visibility, we just need to **display** these fields in templates.

### 💡 No Backend Changes Needed
The discount visibility feature requires only:
1. Reading existing fields (no new DB queries)
2. Enriching decorator to pass metadata
3. Updating templates to display data
4. Adding CSS styles

### 🔴 Missing Features Status

| Feature | Status | Priority | Effort |
|---------|--------|----------|--------|
| Cart Discount Visibility | Not Implemented | High | Medium (frontend only) |
| System Builder | Not Implemented | High | Large (new DocTypes) |

## Related Documentation

### In Repository Root
- **ANALYSIS.md** - Complete technical analysis with all wiki chapters merged
- **PRD.md** - Product requirements document (requirements only)
- **Home.md** - Repository navigation hub

### External
- [GitHub Repository](https://github.com/Comfac-Global-Group/comfac-webshop)
- [Base Project: Frappe Webshop](https://github.com/frappe/webshop)
- [ERPNext Documentation](https://docs.erpnext.com)

## Adding to CIT Wiki

To add these pages to the CIT Wiki under "Frappe ERPNext > Webshop":

1. Create the "Webshop" subpage under "Frappe ERPNext"
2. Upload **Webshop-Index.md** as the main index
3. Upload all chapter files (Webshop-01 through Webshop-14)
4. Ensure navigation links work between pages
5. Update any relative links to point to correct CIT Wiki paths

## Maintenance

When updating code:
1. Update the relevant chapter documentation
2. Keep the Webshop-Index summary current
3. Update the verification checklists after testing

---

**Last Updated:** March 2026  
**Source:** https://github.com/Comfac-Global-Group/comfac-webshop
