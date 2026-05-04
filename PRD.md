# Product Requirements Document (PRD)
# Comfac Webshop - Feature Enhancements

**Version:** 1.0  
**Date:** March 2026  
**Status:** Draft - Pending Staging Sandbox Validation  
**Repository:** https://github.com/Comfac-Global-Group/comfac-webshop  
**Base:** Fork of Frappe Webshop (https://github.com/frappe/webshop)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Requirements: Cart Discount Visibility](#2-requirements-cart-discount-visibility)
3. [Requirements: System Builder](#3-requirements-system-builder)
4. [Implementation Approach](#4-implementation-approach)
5. [Testing & Validation](#5-testing--validation)
6. [Appendix: References](#6-appendix-references)

---

## 1. Executive Summary

### 1.1 Purpose

This document defines the product requirements for new features in Comfac Webshop, an enhanced e-commerce platform built on the Frappe Framework and ERPNext. The enhancements include:

- **Discount visibility** in shopping cart with urgency indicators
- **System Builder** for multi-component configurable products

### 1.2 Target Users

- **B2B Customers:** System builders, IT departments, hardware integrators
- **B2C Customers:** Tech enthusiasts, makers, DIY builders
- **Admin Users:** Store managers, product catalog managers

### 1.3 Key Goals

1. Provide transparent pricing with clear discount visibility
2. Enable complex product configuration (servers, desktops, maker kits)
3. Maintain compatibility with existing ERPNext workflows
4. Ensure seamless upgrade path from base Frappe Webshop

### 1.4 Prerequisites

**CRITICAL:** All feature development follows a strict phased approach:

1. **Phase 0 (Staging Sandbox):** Validate that comfac-webshop fork runs identically to base webshop on production-like ERPNext instance
2. **Phase 1 (Experiment Clone):** Implement features on cloned sandbox, validate all scenarios
3. **Phase 2 (Production):** Merge only after Phase 1 validation passes

**Do not skip Phase 0.**

---

## 2. Requirements: Cart Discount Visibility

### 2.1 Problem Statement

Discounts (from Pricing Rules, Coupon Codes, etc.) are calculated on the Quotation backend but are NOT displayed to the customer in the shopping cart UI. Customers see only the final price without understanding what promotions are active or how much they're saving.

### 2.2 Current State vs. Desired State

#### Current State (What Customer Sees)

- Item name, code, image
- Quantity (editable)
- Rate (final price per unit)
- Amount (total for that line)
- Net Total, Taxes, Grand Total
- Coupon code badge (if applied)

#### Current State (What's Hidden on Quotation)

- Original price (`price_list_rate`) before discount
- Discount percentage (`discount_percentage`)
- Per-item discount amount
- Total savings
- Which pricing rules are active
- Additional discount on total (`discount_amount`, `additional_discount_percentage`)
- Offer deadlines (from Pricing Rule `valid_upto`)

#### Desired State

```
+-----------------------------------------------------------------+
| [IMG] Server RAM DDR5 32GB                          Qty: 2      |
|       SKU: RAM-DDR5-32GB                                        |
|                                                                 |
|       Was: $149.99  (strikethrough)                             |
|       Now: $119.99  (-20%)                                      |
|       You save: $60.00 on this item                             |
|       [clock icon] Offer ends: March 1, 2026 (10 days left)    |
|                                                   Total: $239.98|
+-----------------------------------------------------------------+
```

### 2.3 Functional Requirements

#### RQ-2.1: Per-Item Discount Display

**Priority:** High

**Description:** For each cart item with a discount, display:
- Original price (`price_list_rate`) struck through
- Discounted price (`rate`)
- Discount percentage badge (-X%)
- "You save" amount per line

**Template:** `templates/includes/cart/cart_items.html`

**Data Source:** Quotation Item fields: `price_list_rate`, `rate`, `discount_percentage`

**Acceptance Criteria:**
- [ ] Original price shown with strikethrough when `price_list_rate != rate`
- [ ] Discount badge shows percentage (e.g., "-20%")
- [ ] "You save" amount calculated as `(price_list_rate - rate) * qty`
- [ ] Free items show "FREE" badge (existing behavior preserved)
- [ ] Items without discount show no strikethrough or badge

#### RQ-2.2: Payment Summary with Savings

**Priority:** High

**Description:** In the payment summary section, show:
- Original subtotal (struck through) if discounts exist
- Total savings amount (green text)
- Additional discount row if `doc.discount_amount` exists
- Net total and grand total (existing)

**Template:** `templates/includes/cart/cart_payment_summary.html`

**Calculation:**
```
original_total = sum(item.price_list_rate * item.qty for all items)
total_savings = original_total - doc.total
```

**Acceptance Criteria:**
- [ ] Original subtotal shown with strikethrough when savings exist
- [ ] "Your Savings" row shows total savings in green
- [ ] Additional discount row appears if `doc.discount_amount > 0`
- [ ] Grand total remains unchanged (existing behavior)

#### RQ-2.3: Cart Total Display

**Priority:** Medium

**Description:** Update cart items total template to show:
- Original total (struck through) if savings exist
- Net total (current)

**Template:** `templates/includes/cart/cart_items_total.html`

**Acceptance Criteria:**
- [ ] Original total shown with strikethrough when `has_any_discount` is true
- [ ] Net total displayed as current behavior
- [ ] No duplicate calculations in template (use decorated doc fields)

#### RQ-2.4: Navbar Mini-Cart

**Priority:** Medium

**Description:** Update navbar dropdown mini-cart to show:
- Strike-through original price when discounted
- Discount badge

**Template:** `templates/includes/cart/cart_items_dropdown.html`

**Acceptance Criteria:**
- [ ] Mini-cart shows strikethrough price for discounted items
- [ ] Badge shows discount percentage
- [ ] Layout remains compact for dropdown

### 2.4 Non-Functional Requirements

#### RQ-2.5: Performance

- Discount calculations must not add database queries (use cached Pricing Rule lookups)
- AJAX cart updates must complete within 500ms

#### RQ-2.6: Mobile Responsiveness

- Discount badges must be readable on screens down to 320px width
- Strikethrough prices must not break layout on mobile

#### RQ-2.7: Accessibility

- Color must not be the only indicator of discount (use badges with text)
- Screen readers must announce "You save X dollars" 

### 2.5 Files to Modify

| File | Change Type | Description |
|------|-------------|-------------|
| `webshop/webshop/shopping_cart/cart.py` | Modify | Add `decorate_quotation_doc()` enhancements: `offer_details`, `original_total`, `total_savings`, `has_any_discount` |
| `templates/includes/cart/cart_items.html` | Modify | Add original price, discount % display, savings per item, offer deadline badges |
| `templates/includes/cart/cart_payment_summary.html` | Modify | Add savings row, original subtotal with strikethrough, additional discount row |
| `templates/includes/cart/cart_items_total.html` | Modify | Add pre-discount total with strikethrough |
| `templates/includes/cart/cart_items_dropdown.html` | Modify | Add strike-through price and discount badge |
| `public/scss/webshop_cart.scss` | Modify | Add styles for discount badges, strikethrough, urgency indicators |

### 2.6 Edge Cases

| Case | Handling |
|------|----------|
| Free items (`is_free_item=True`) | Show "FREE" badge, include full `price_list_rate * qty` in savings |
| Items with no discount (`price_list_rate == rate`) | No strikethrough, no badge |
| Additional discount on total (`doc.discount_amount`) | Show separate row in payment summary |
| Multiple pricing rules per item | Show all offer details, use `price_list_rate - rate` for savings calc |
| Margin-based pricing | Use `rate_with_margin` if present |
| `price_list_rate` is null | Fall back to showing `rate` only, no error |

### 2.7 Urgency Display Requirements

#### RQ-2.8: Offer Deadline Display

**Priority:** High

**Description:** Show offer expiration dates from Pricing Rules with visual urgency indicators.

**Data Source:**
- `Quotation Item.pricing_rules` (JSON string of Pricing Rule names)
- `Pricing Rule.valid_upto` (deadline date)
- `Pricing Rule.title` (offer name)

**Urgency Levels:**

| Days Remaining | Display Style | Example |
|----------------|---------------|---------|
| > 14 days | Green text, informational | "Offer until March 1, 2026" |
| 7-14 days | Yellow/orange badge | "Ends soon" |
| 1-7 days | Red badge | "Only X days left!" |
| < 24 hours | Red pulsing | "Ends today!" |
| Expired | Remove discount, recalculate | N/A |

**Acceptance Criteria:**
- [ ] Deadline displayed for each item with `valid_upto` in Pricing Rule
- [ ] Days remaining calculated correctly
- [ ] Visual urgency indicator appropriate for time remaining
- [ ] Multiple offers on one item show all deadlines

---

## 3. Requirements: System Builder

### 3.1 Vision

A configurable product builder where customers can assemble multi-component systems (servers, desktops, maker kits, open-source hardware platforms) from a template of compatible components, with real-time pricing, compatibility enforcement, and the ability to save/load configurations.

### 3.2 Use Cases

1. **Server Builder** - Customer selects: chassis, CPU, RAM (qty/type), storage (multiple drives), NIC, PSU, OS
2. **Desktop Builder** - Case, motherboard, CPU, GPU, RAM, storage, PSU, peripherals
3. **Maker Kit Builder** - Board (RPi, Arduino, etc.), sensors, actuators, enclosure, power supply
4. **Future platforms** - Any multi-component configurable product

### 3.3 Functional Requirements

#### RQ-3.1: System Builder Template Management

**Priority:** High

**Description:** Admin interface for creating and managing system builder templates.

**New DocType: System Builder Template**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Data | Yes | Template name (e.g., "1U Rack Server") |
| `description` | Text | No | Template description |
| `image` | Attach Image | No | Template image |
| `category` | Select | Yes | Category (Server, Desktop, Maker Kit, etc.) |
| `component_slots` | Table | Yes | Child table of Component Slots |

**New DocType: Component Slot (Child Table)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `slot_name` | Data | Yes | Slot name (e.g., "CPU", "RAM") |
| `required` | Check | Yes | Is this slot required? |
| `min_qty` | Int | No | Minimum quantity (default 1) |
| `max_qty` | Int | No | Maximum quantity (default 1) |
| `allowed_items` | Table | No | Child table of allowed items/groups |
| `default_selection` | Link | No | Default item for this slot |

**Acceptance Criteria:**
- [ ] Admin can create templates with multiple slots
- [ ] Each slot can be marked required/optional
- [ ] Slots can allow multiple items (qty > 1)
- [ ] Slots can be restricted by Item Group or specific Items
- [ ] Templates can have default selections

#### RQ-3.2: Compatibility Rules

**Priority:** High

**Description:** Rules engine to enforce component compatibility across slots.

**New DocType: Compatibility Rule**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rule_name` | Data | Yes | Rule name |
| `template` | Link | Yes | Parent System Builder Template |
| `rule_type` | Select | Yes | "Requires", "Excludes", "Max Qty", "Min Qty" |
| `source_slot` | Link | Yes | Source component slot |
| `source_filter` | Code | No | JSON filter for source attributes |
| `target_slot` | Link | Yes | Target component slot |
| `target_filter` | Code | No | JSON filter for target attributes |
| `error_message` | Text | Yes | Message shown when rule violated |

**Rule Types:**
- **Requires**: Source selection requires specific target selection
  - Example: "CPU Socket LGA1700 REQUIRES Motherboard Socket LGA1700"
- **Excludes**: Source selection excludes specific target selection
  - Example: "RAM Type DDR5 EXCLUDES Motherboard Type DDR4"
- **Max Qty**: Maximum quantity based on other slot selection
  - Example: "Max 4 RAM sticks if Motherboard RAM Slots = 4"
- **Min Qty**: Minimum quantity required
  - Example: "Min 1 PSU if Chassis included"

**Acceptance Criteria:**
- [ ] Rules can be created for each template
- [ ] Rules are evaluated in real-time during configuration
- [ ] Violated rules show error messages
- [ ] Valid options are filtered based on rules
- [ ] Complex rule chains work (A requires B, B requires C)

#### RQ-3.3: Customer Configuration UI

**Priority:** High

**Description:** Customer-facing interface for configuring systems.

**UI Flow:**
```
1. Choose Template (e.g., "1U Rack Server")
2. For each slot:
   - Browse/filter compatible components
   - See price, availability, specs
   - Select and configure (qty, variant attributes)
3. Real-time:
   - Compatibility checks
   - Running total
   - Power budget / capacity warnings (Phase 2)
4. Save Configuration (optional)
5. Add to Cart
```

**Acceptance Criteria:**
- [ ] Customer can browse available templates
- [ ] Each slot shows compatible options only
- [ ] Real-time price updates as selections change
- [ ] Compatibility warnings appear immediately
- [ ] Required slots must be filled before add to cart
- [ ] Configuration can be saved for later

#### RQ-3.4: Saved Configurations

**Priority:** Medium

**Description:** Allow customers to save, share, and reload configurations.

**New DocType: Saved Configuration**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `customer` | Link | Yes | Customer who saved |
| `template` | Link | Yes | System Builder Template used |
| `config_name` | Data | Yes | User-defined name |
| `selected_items` | Table | Yes | Child table of selected items per slot |
| `total_price` | Currency | Yes | Total configuration price |
| `status` | Select | Yes | Draft, Shared, Ordered |
| `share_token` | Data | No | Unique token for sharing URL |

**Acceptance Criteria:**
- [ ] Customer can save configuration with custom name
- [ ] Saved configurations appear in user dashboard
- [ ] Configuration can be shared via URL with token
- [ ] Others can view shared configurations (read-only)
- [ ] Configurations can be cloned and modified
- [ ] Ordered configurations are locked (read-only)

#### RQ-3.5: Cart Integration

**Priority:** High

**Description:** Add configured systems to cart as grouped items.

**Approach:**
- Option A: Add all components as separate Quotation Items with reference link
- Option B: Create "Product Bundle" or "Packed Item" representation
- Option C: Single line item with child table of components

**Selected Approach:** Option A with grouping metadata

**Acceptance Criteria:**
- [ ] All components added to cart as individual line items
- [ ] Line items have reference to parent configuration
- [ ] Group can be expanded/collapsed in cart view
- [ ] Individual items can be removed from group (with compatibility warning)
- [ ] Pricing rules apply to both individual items and bundle total

#### RQ-3.6: Pricing Display

**Priority:** High

**Description:** Show component pricing and total with bundle discounts.

**Display Requirements:**
```
Component Breakdown:
  Chassis ............... $299.00
  CPU (Intel Xeon) ...... $899.00
  RAM 64GB (4x16GB) ..... $479.00
  Storage 2TB NVMe ...... $349.00
  PSU 800W .............. $189.00
  --------------------------------
  Subtotal .............. $2,215.00
  
Bundle Discount (5%) .... -$110.75
  --------------------------------
  Total ................. $2,104.25
```

**Acceptance Criteria:**
- [ ] Per-component prices shown during configuration
- [ ] Running total updates in real-time
- [ ] Bundle discounts calculated and displayed
- [ ] Individual item discounts also shown
- [ ] Final total matches cart total after add

### 3.4 Non-Functional Requirements

#### RQ-3.7: Performance

- Compatibility rule evaluation must complete within 200ms for typical templates (< 20 slots)
- Real-time price updates must not block UI
- Cache compatibility matrices for popular templates

#### RQ-3.8: Scalability

- Support templates with up to 50 component slots
- Support up to 1000 items per slot (with pagination in UI)
- Support complex rule chains (up to 10 rule dependencies)

#### RQ-3.9: Maintainability

- Rule engine must be extensible for new rule types
- Template definitions must be exportable/importable (JSON)
- Clear error messages for rule violations

### 3.5 Implementation Phases

#### Phase 1: Foundation (Weeks 1-4)

**Deliverables:**
- [ ] System Builder Template DocType
- [ ] Component Slot child table
- [ ] Basic UI: template selection, slot browsing
- [ ] Simple "add all to cart" (no compatibility engine yet)

**Success Criteria:**
- Admin can create templates
- Customer can select template and browse slots
- Items can be added to cart

#### Phase 2: Compatibility Engine (Weeks 5-8)

**Deliverables:**
- [ ] Compatibility Rule DocType
- [ ] Rule evaluation engine
- [ ] Real-time filtering of valid options
- [ ] Warning/error display

**Success Criteria:**
- Rules can be created and saved
- Rules are evaluated in real-time
- Invalid options are filtered out
- Clear error messages shown

#### Phase 3: Save & Share (Weeks 9-12)

**Deliverables:**
- [ ] Saved Configuration DocType
- [ ] User dashboard for saved configs
- [ ] Share via URL
- [ ] Load/clone/modify functionality

**Success Criteria:**
- Configurations can be saved
- Share links work for external users
- Cloning creates editable copy

#### Phase 4: Advanced Features (Future)

**Deliverables:**
- [ ] Power/thermal budget calculation
- [ ] AI-assisted recommendations
- [ ] Preset "popular configurations"
- [ ] Configuration comparison tool
- [ ] BOM integration for manufacturing

### 3.6 Technical Challenges & Mitigations

| Challenge | Mitigation |
|-----------|------------|
| Performance: Evaluating compatibility across many items/rules | Cache compatibility matrices; lazy evaluation; Redis caching |
| Attribute mapping: Different items have different attributes | Normalize on key attributes (socket type, RAM type, etc.); use Item Attributes |
| Cart representation: How to group system components | Add metadata fields to Quotation Item for grouping; use child table reference |
| Pricing complexity: Component + bundle + system-level discounts | Apply discounts sequentially; show breakdown; validate total |
| Stock: All components must be available | Check stock for all items before add to cart; show availability warnings |

---

## 4. Implementation Approach

### 4.1 Core Thesis for Discount Visibility

**All the data we need already exists on the Quotation document.** ERPNext's pricing engine populates discount fields on every cart save. We do not need to change the backend calculation logic. We need to:

1. **Surface existing hidden fields** in the cart templates
2. **Enrich the decorator** to pass pricing rule metadata (deadlines, titles) to the frontend
3. **Add summation logic** in the payment summary template
4. **Style it** so customers immediately see value and urgency

### 4.2 Fields to Surface (Discount Visibility)

#### 4.2.1 Per-Item Fields (Quotation Item)

| Field | Purpose |
|-------|---------|
| `price_list_rate` | Original price (strikethrough display) |
| `rate` | Final price (current display) |
| `discount_percentage` | Discount badge (-X%) |
| `pricing_rules` | Lookup for offer titles/deadlines |
| `is_free_item` | FREE badge |

#### 4.2.2 Document-Level Fields (Quotation)

| Field | Purpose |
|-------|---------|
| `total` | Sum of item amounts |
| `discount_amount` | Additional order-level discount |
| `coupon_code` | Coupon badge |

### 4.3 Backend Helper for Offer Details

```python
# New utility function to get discount details for cart display
@frappe.whitelist()
def get_cart_discount_details(quotation_name):
    """Returns discount and deadline info for each cart item."""
    doc = frappe.get_doc("Quotation", quotation_name)
    discount_details = []

    for item in doc.items:
        detail = {
            "item_code": item.item_code,
            "price_list_rate": item.price_list_rate,
            "rate": item.rate,
            "discount_percentage": item.discount_percentage,
            "discount_amount": item.discount_amount,
            "is_free_item": item.is_free_item,
            "savings": (item.price_list_rate - item.rate) * item.qty,
            "offers": []
        }

        # Parse applied pricing rules
        if item.pricing_rules:
            import json
            rule_names = json.loads(item.pricing_rules)
            for rule_name in rule_names:
                rule = frappe.get_cached_doc("Pricing Rule", rule_name)
                offer = {
                    "rule_name": rule.name,
                    "title": rule.title or rule.name,
                    "valid_from": rule.valid_from,
                    "valid_upto": rule.valid_upto,
                    "discount_percentage": rule.discount_percentage,
                }
                if rule.valid_upto:
                    from frappe.utils import date_diff, today
                    offer["days_remaining"] = date_diff(rule.valid_upto, today())
                detail["offers"].append(offer)

        discount_details.append(detail)

    return discount_details
```

### 4.4 What We Do NOT Need to Change

| Component | Why No Change Needed |
|-----------|---------------------|
| `set_price_list_and_rate()` | Already resets and repopulates `price_list_rate`, `discount_percentage` on every save |
| `apply_cart_settings()` | Already calls `calculate_taxes_and_totals()` which does all the math |
| `update_cart()` | Already re-renders all three template fragments on AJAX update |
| ERPNext Pricing Rules | Standard feature - we just read the results |
| ERPNext Quotation DocType | All fields we need already exist on the standard DocType |
| `shopping_cart.js` | AJAX update already replaces `.cart-items`, `.cart-tax-items`, `.payment-summary` |

---

## 5. Testing & Validation

### 5.1 Discount Visibility Test Scenarios

| # | Scenario | Expected Result |
|---|----------|-----------------|
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
| 11 | Cart with mixed items | Only discounted items show strikethrough |
| 12 | AJAX qty update | All discount info re-renders correctly |
| 13 | Mobile view | Discount badges readable on small screens |
| 14 | Null price_list_rate | Falls back to showing rate only, no error |

### 5.2 System Builder Test Scenarios

| # | Scenario | Expected Result |
|---|----------|-----------------|
| 1 | Create server template | Admin can define chassis, CPU, RAM, storage slots |
| 2 | Set compatibility rules | CPU socket matches motherboard socket |
| 3 | Customer configures system | Only compatible options shown |
| 4 | Incompatible selection | Warning shown, can't add to cart |
| 5 | Real-time price updates | Total updates as selections change |
| 6 | Save configuration | Configuration saved to user account |
| 7 | Share configuration | Share URL works for external viewing |
| 8 | Add to cart | All components added as grouped items |
| 9 | View in cart | Grouped display, can expand/collapse |
| 10 | Bundle discount | 5% discount applied to total |

### 5.3 Risk Assessment (Discount Visibility)

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `price_list_rate` is 0 or null | Medium | Guard with `{% if item.price_list_rate and item.price_list_rate > 0 %}` |
| `pricing_rules` JSON malformed | Low | Wrap in try/except, return empty list |
| Pricing Rule deleted but referenced | Low | Use `frappe.db.exists()` check |
| Performance hit from Pricing Rule lookups | Low | `get_cached_doc()` uses Frappe cache |
| Multiple pricing rules per item | Medium | Show all offer details; sum savings using `price_list_rate - rate` |

---

## 6. Appendix: References

### 6.1 Related Documents

- [ANALYSIS.md](./ANALYSIS.md) - Technical analysis of codebase including all wiki chapters
- [Frappe Webshop Docs](https://docs.erpnext.com/docs/user/manual/en/set_up_e_commerce) - Official ERPNext e-commerce guide
- [Wiki Home](https://github.com/Comfac-Global-Group/comfac-webshop/wiki) - Original wiki documentation

### 6.2 Key Files Reference

#### Backend
- `webshop/webshop/shopping_cart/cart.py` - Cart logic, decorator function
- `webshop/webshop/api.py` - API endpoints
- `webshop/hooks.py` - App hooks and events

#### Frontend Templates
- `templates/includes/cart/cart_items.html` - Cart line items
- `templates/includes/cart/cart_payment_summary.html` - Payment summary
- `templates/includes/cart/cart_items_total.html` - Cart totals
- `templates/includes/cart/cart_items_dropdown.html` - Mini-cart

#### Styles
- `public/scss/webshop_cart.scss` - Cart styles

### 6.3 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | March 2026 | PRD Generator | Initial document with discount visibility and system builder requirements |

---

**End of Product Requirements Document**
