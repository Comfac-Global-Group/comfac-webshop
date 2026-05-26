# Comfac Webstore Agent Instructions

> **For:** Kimi, Claude, DeepSeek, OpenCode, or any AI assistant  
> **Repo:** `comfac-webstore` — web shop setup, product listings, pricing, and e-commerce configuration  
> **Last Updated:** 2026-05-23

---

## Your Job as the Webshop Agent

You work in the webshop repo. Your job is to:
1. **Build and maintain** the web shop product catalog, pricing, and checkout flow.
2. **Report progress** after every session so the comfac-ops agent can monitor webshop development.
3. **Preserve** configuration guides, pricing rules, and integration notes.

---

## Progress Reporting (Required)

After **every session**, append a dated entry to `SESSION_LOG.md` (create it if it doesn't exist). Use this format:

```markdown
## YYYY-MM-DD — <One-line summary>

**Owner:** <Name>  
**Status:** 🟢/🟡/🔴  

### What Was Done
- <Bullet 1>
- <Bullet 2>

### Blockers / Risks
- <None | description>

### Next Actions
- <Action 1> — due <date> — owner <name>
```

**Status colors:**
- 🟢 **Green** — on track, no blockers
- 🟡 **Yellow** — minor delays or dependencies
- 🔴 **Red** — blocked, needs escalation

### Weekly Summary

Every **Friday**:

```markdown
## Week of YYYY-MM-DD

**Focus:** <Theme>
**Overall Status:** 🟢/🟡/🔴

### Completed
- <Item>

### In Progress
- <Item>

### Blockers
- <None | description>

### Next Week
- <Planned work>
```

> **These files are read by the comfac-ops agent.** Keep them factual and concise. The ops agent synthesizes across all repos — your job is to feed it accurate signal.

---

*Agents: The webshop is a revenue channel. Blockers here directly impact sales. Log them.*

---

## Version Numbering Scheme

cws uses **semantic versioning** visible as `vMAJOR.MINOR.PATCH`:

| Component | Meaning | Current |
|-----------|---------|---------|
| MAJOR | 0 = pre-release/development | 0 |
| MINOR | Feature releases (1, 2, 3...) | 1 |
| PATCH | Bugfix/config releases (01, 02, 03...) | 01 |

- **`v0.MINOR.PATCH`**is the display format (e.g.,**v0.1.01**)
- The version lives in `webshop/__init__.py` ( `__version__` ) and `VERSION` file
- Every commit that changes behavior increments PATCH
- Workspace/UI changes are PATCH increments
- New features are MINOR increments
- Production readiness (etest → ecit deploy) is MAJOR 1.0

**Current version:** v0.1.01 — Initial cws release on etest

**Last commit format:** `v0.1.01: <description>`

---

## Upstream Sync (Updating cws from fws)

See **`UPSTREAM-SYNC.md`** for the step-by-step process. Short version:
1. `git fetch upstream` (add remote if missing: `git remote add upstream https://github.com/frappe/webshop.git`)
2. `git merge upstream/develop --no-ff`
3. Resolve conflicts in the 5 Comfac-changed files only (all others: take upstream)
4. `git push origin develop && git push github develop && git push github-private develop`
5. Deploy via Frappe Cloud dashboard + `bench clear-cache` via SSH

---

## CWP Core Principle (read before any change)

> **cws never adds new data sources. It only DISPLAYS information Frappe already provides
> on quotation/cart line items: `discount_percentage`, `price_list_rate`, `rate`, `amount`,
> `taxes_and_charges`. The upstream fws already exposes all these fields.**

Corollary: if a feature is missing or broken in cws, the cause is **never** in cws's templates.
Always look at:
1. **Settings** — Webshop Settings not configured (most common)
2. **Data** — pricing rule / discount not applied to the item
3. **Assets** — CSS/JS bundle not built or not served

The 5% cws delta vs upstream fws:
- `webshop/templates/includes/cart/cart_items.html` — discount row display
- `webshop/templates/includes/cart/cart_items_dropdown.html` — mini-cart discount display
- `webshop/hooks.py` — publisher info, `payments` removed from `required_apps`
- `webshop/__init__.py` — version
- `webshop/webshop/workspace/webshop.json` — workspace registration (new)
- `VERSION` — version file (new)

All SCSS/CSS is **100% upstream fws** — cws does not add or change any stylesheets.

---

## Pre-Deploy Audit Checklist (run before every etest or ecit deploy)

| # | Check | How |
|---|-------|-----|
| 1 | **Webshop Settings parity** | Compare ecit vs etest via API (see below); sync all fields |
| 2 | **Anonymous product view** | Open `/all-products` in incognito — products must show |
| 3 | **JS console clean** | No 404s on bundle files in browser network tab |
| 4 | **Route smoke test** | `/all-products` → product page → `/cart` → Request for Quote |
| 5 | **Discount visible** | Add a discounted item; verify strikethrough + badge + savings row |
| 6 | **VAT applied** | Cart total includes tax row |
| 7 | **fws feature parity** | Everything fws shows, cws also shows |

### Webshop Settings — Required Fields on Both ecit and etest

```
enabled: 1
company: Comfac Corporation
price_list: Standard Selling
default_customer_group: All Customer Groups
quotation_series: SAL-QTN-.YYYY.-
products_per_page: 24
show_price: 1
show_price_in_quotation: 1
show_stock_availability: 1
allow_items_not_in_stock: 1
save_quotations_as_draft: 1
payment_success_url: Orders
enable_wishlist: 1
enable_reviews: 1
enable_recommendations: 1
enable_field_filters: 1
enable_attribute_filters: 1
filter_fields: [brand, item_group]
filter_attributes: [Colour, Size]
login_required_to_view_products: 0   ← MUST be 0 or unset; 1 hides products from guests
```

⚠️ `login_required_to_view_products: 1` is the most dangerous misconfiguration — it silently
hides all products from any visitor who is not logged in. Always verify this is 0.

---

## 2026-05-23 — cws Deployment & Current State

**cws (comfac-webstore-private)** is Comfac's private fork of Frappe WebShop (fws), deployed
standalone on etest (t3.comfac-it.com). payments dependency removed. v0.1.01.

### etest State (as of 2026-05-23 end-of-day)

| Signal | State |
|--------|-------|
| cws installed for site | ✅ `test260204.s.frappe.cloud` |
| `/all-products` | ✅ 200 |
| 89 Website Items | ✅ Created via `make_website_item()` |
| Add to Cart | ✅ QTN-CART-00001 created |
| Cart discount display | ✅ Strikethrough, badge, savings |
| VAT in cart | ✅ @ 12% |
| Request for Quote | ✅ Visible |
| Webshop module in left panel | ✅ Workspace JSON deployed |
| Awesome Bar | 🟡 Pending SSH `git pull` + `bench migrate` |
| SSH access | 🔴 Blocked — "Too many authentication failures" |

**Immediate blocker:** `payments` app is not in the etest bench. Installing cws fails with
`No module named 'payments'`. Resolve via Frappe Cloud dashboard (add payments app) or by removing
the dependency from `hooks.py` if payments features are unused.

**Next step:** Install cws on etest bench, then run `create_website_items.py` (or a console script
using `make_website_item()`) to create Website Item records from the 89 published Items. This
completes the webshop layer on etest.
