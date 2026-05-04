# Webshop Index

**Location:** Frappe ERPNext > Webshop  
**Repository:** [Comfac-Global-Group/comfac-webshop](https://github.com/Comfac-Global-Group/comfac-webshop)  
**Status:** Fork of Frappe Webshop with planned enhancements

---

## Overview

The Comfac Webshop is an open-source e-commerce platform built on the Frappe Framework and integrated with ERPNext. It enables businesses to create online stores with product catalogs, shopping carts, and order management.

This documentation covers the complete architecture, codebase, and planned enhancements for the Comfac Webshop fork.

### Key Information

| Attribute | Value |
|-----------|-------|
| **Base Project** | [Frappe Webshop](https://github.com/frappe/webshop) |
| **Framework** | Frappe Framework (Python 3.10+, MariaDB/PostgreSQL) |
| **Dependencies** | frappe, erpnext, payments |
| **Module** | Webshop (single module) |
| **Build System** | Flit |
| **Codebase Size** | ~172 files, ~988KB |

---

## Documentation Chapters

### Core Architecture & Codebase

Understanding how the webshop works:

| Chapter | Title | Description |
|---------|-------|-------------|
| [01](Webshop-01-Architecture-Overview) | **Architecture Overview** | Framework stack, app integration, data flow, key design decisions |
| [02](Webshop-02-DocTypes) | **DocTypes** | Custom DocTypes (Webshop Settings, Website Item, Wishlist, etc.) and ERPNext DocTypes used |
| [03](Webshop-03-Shopping-Cart-Quotation-Deep-Dive) | **Shopping Cart & Quotation Deep Dive** | How the cart IS a Quotation, template breakdown, hidden fields, AJAX updates |
| [04](Webshop-04-Product-Pages-and-Browsing) | **Product Pages & Browsing** | /all-products, /shop-by-category, Item Group pages, product info API |
| [05](Webshop-05-Variant-Selector) | **Variant Selector** | Item variants system, configurator UI, Redis caching, API endpoints |
| [06](Webshop-06-Pricing-and-Discounts) | **Pricing & Discounts** | Price lists, pricing rules, coupon codes, ERPNext pricing engine |
| [07](Webshop-07-Checkout-and-Orders) | **Checkout & Orders** | Place order flow, payment, order tracking, wishlist |
| [08](Webshop-08-Templates-and-Frontend) | **Templates & Frontend** | Jinja templates, JavaScript files, SCSS structure |
| [09](Webshop-09-Hooks-and-Events) | **Hooks & Events** | App hooks, doc_events, CRUD handlers, class overrides |

### Feature Gaps & Enhancement Plans

Features that need to be developed:

| Chapter | Title | Description | Priority |
|---------|-------|-------------|----------|
| [10](Webshop-10-Feature-Gap-Cart-Discounts) | **Feature Gap: Cart Discounts** | Analysis of missing discount visibility in cart UI | 🔴 High |
| [11](Webshop-11-Feature-Plan-System-Builder) | **Feature Plan: System Builder** | Multi-component configurator for servers, desktops, maker kits | 🔴 High |

### Development & Deployment

Implementation guides:

| Chapter | Title | Description |
|---------|-------|-------------|
| [12](Webshop-12-Staging-Sandbox-Deployment) | **Staging Sandbox Deployment** | Testing environment setup, Phase 0/1/2 approach, validation checklist |
| [13](Webshop-13-Discount-Visibility-and-Urgency) | **Discount Visibility & Offer Urgency** | UI specifications, urgency indicators, test scenarios, mockups |
| [14](Webshop-14-Hypothesis-Discount-Deadline-Visibility) | **Hypothesis: Discount & Deadline Visibility** | Exact implementation plan, field targeting, file-by-file changes, risk assessment |

---

## Missing Features for Comfac

### 🔴 Feature 1: Cart Discount Visibility

**Status:** Not Implemented  
**Priority:** High  
**Effort:** Medium (frontend/template changes only)

**Problem:**  
Discounts from Pricing Rules and Coupon Codes are calculated by ERPNext on the Quotation but are **hidden from customers**. They only see final prices without understanding their savings or offer deadlines.

**What's Missing:**

| Feature | Backend Status | Frontend Status |
|---------|---------------|-----------------|
| Original price display | ✅ Exists (`price_list_rate`) | ❌ Not shown |
| Discount percentage badge | ✅ Exists (`discount_percentage`) | ❌ Not shown |
| "You save" amount per item | ✅ Calculable | ❌ Not shown |
| Total savings in summary | ✅ Calculable | ❌ Not shown |
| Offer deadline display | ✅ Exists (`Pricing Rule.valid_upto`) | ❌ Not shown |
| Urgency indicators | ❌ N/A | ❌ Not implemented |

**Key Insight:**  
All the data already exists on the Quotation document. ERPNext's pricing engine populates these fields on every cart save. This is purely a **frontend/template display issue** - no backend changes needed.

**Files to Modify:**
1. `webshop/webshop/shopping_cart/cart.py` - Enhance decorator to pass offer metadata
2. `templates/includes/cart/cart_items.html` - Add per-item discount display
3. `templates/includes/cart/cart_payment_summary.html` - Add savings total
4. `templates/includes/cart/cart_items_total.html` - Add pre-discount total
5. `templates/includes/cart/cart_items_dropdown.html` - Update mini-cart
6. `public/scss/webshop_cart.scss` - Add discount styles

**Implementation Approach:**
- Read existing hidden fields from Quotation (`price_list_rate`, `discount_percentage`, `pricing_rules`)
- Parse `pricing_rules` JSON to get offer titles and deadlines
- Calculate savings using `(price_list_rate - rate) * qty`
- Display with strikethrough prices, badges, and urgency indicators

**See:** [Chapter 10](Webshop-10-Feature-Gap-Cart-Discounts) | [Chapter 13](Webshop-13-Discount-Visibility-and-Urgency) | [Chapter 14](Webshop-14-Hypothesis-Discount-Deadline-Visibility)

---

### 🔴 Feature 2: System Builder

**Status:** Not Implemented  
**Priority:** High  
**Effort:** Large (new DocTypes, UI, compatibility engine)

**Problem:**  
No way to configure multi-component systems (servers, desktops, maker kits) with:
- Component compatibility checking
- Bundle pricing
- Save/share configurations

**New DocTypes Required:**

1. **System Builder Template**
   - Name, category, description, image
   - Child table: Component Slots

2. **Component Slot** (Child Table)
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
   - Template used
   - Selected items per slot
   - Share token for URLs

**Use Cases:**
- Server Builder: Chassis, CPU, RAM (qty/type), storage, NIC, PSU, OS
- Desktop Builder: Case, motherboard, CPU, GPU, RAM, storage, PSU, peripherals
- Maker Kit Builder: Board (RPi, Arduino), sensors, actuators, enclosure, power

**Implementation Phases:**

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Phase 1: Foundation** | Weeks 1-4 | DocTypes, basic UI, add to cart |
| **Phase 2: Compatibility** | Weeks 5-8 | Rule engine, real-time filtering |
| **Phase 3: Save & Share** | Weeks 9-12 | Dashboard, share URLs, cloning |
| **Phase 4: Advanced** | Future | Power budgets, AI recommendations, BOM integration |

**Technical Challenges:**
- Performance: Evaluating compatibility across many items/rules
- Attribute mapping: Normalizing different item attributes for rules
- Cart representation: Grouping system components in Quotation
- Pricing complexity: Component + bundle + system-level discounts

**See:** [Chapter 11](Webshop-11-Feature-Plan-System-Builder)

---

## Development Workflow

### ⚠️ Phase 0: Baseline Validation (MANDATORY)

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

**⚠️ Do not skip Phase 0.**

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

**See:** [Chapter 12](Webshop-12-Staging-Sandbox-Deployment) for detailed deployment guide

---

## Quick Technical Reference

### The Cart IS a Quotation

The webshop has no separate "cart" table. The shopping cart is literally an ERPNext **Quotation** document with:
- `order_type="Shopping Cart"`
- `docstatus=0` (Draft)

This means all ERPNext pricing features work automatically - we just need to display the fields.

### Key Hidden Fields (Already Exist!)

Every Quotation Item already has:
- `price_list_rate` - Original price (strikethrough this)
- `rate` - Final price (currently shown)
- `discount_percentage` - Discount % (show as badge)
- `pricing_rules` - JSON of applied Pricing Rules (parse for deadlines)
- `is_free_item` - FREE item flag

### No Backend Changes Needed

For discount visibility:
- Read existing fields (no new DB queries)
- Enrich decorator to pass metadata
- Update templates to display data
- Style with CSS

The ERPNext pricing engine does all calculations.

---

## Resources

### Code & Documentation

- [GitHub Repository](https://github.com/Comfac-Global-Group/comfac-webshop)
- [Base Project: Frappe Webshop](https://github.com/frappe/webshop)
- [ERPNext E-commerce Docs](https://docs.erpnext.com/docs/user/manual/en/set_up_e_commerce)
- [Frappe Framework Docs](https://docs.frappe.io)

### Internal Documentation

- [ANALYSIS.md](https://github.com/Comfac-Global-Group/comfac-webshop/blob/main/ANALYSIS.md) - Full technical analysis with all wiki chapters
- [PRD.md](https://github.com/Comfac-Global-Group/comfac-webshop/blob/main/PRD.md) - Product requirements document
- [Home.md](https://github.com/Comfac-Global-Group/comfac-webshop/blob/main/Home.md) - Repository navigation hub

---

## Related Pages

- [Frappe ERPNext Index](../Frappe-ERPNext-Index) - Main ERPNext documentation hub
- [HRMS Index](../HRMS-Index) - Human Resource Management System documentation
- [Payments Integration](../Payments-Integration) - Payment gateway setup

---

**Last Updated:** March 2026  
**Maintained by:** Comfac IT Team  
**Section:** Frappe ERPNext > Webshop
