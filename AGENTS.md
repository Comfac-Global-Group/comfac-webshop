# Comfac Webshop Agent Instructions

> **For:** Kimi, Claude, DeepSeek, OpenCode, or any AI assistant  
> **Repo:** `comfac-webshop` — web shop setup, product listings, pricing, and e-commerce configuration  
> **Last Updated:** 2026-05-15

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

## Upstream Sync (Updating cwp from fws)

See **`UPSTREAM-SYNC.md`** for the step-by-step process. Short version:
1. `git fetch upstream` (add remote if missing: `git remote add upstream https://github.com/frappe/webshop.git`)
2. `git merge upstream/develop --no-ff`
3. Resolve conflicts in the 5 Comfac-changed files only (all others: take upstream)
4. `git push origin develop && git push github develop && git push github-private develop`
5. Deploy via Frappe Cloud dashboard + `bench clear-cache` via SSH

---

## 2026-05-23 15:19 — cwp Deployment & Standalone Status

**cwp (comfac-webshop-private)** is Comfac's own private fork of Frappe WebShop (fws). It is
Comfac's designated webshop engine and the long-term goal is for it to be deployable standalone
on any bench — **not** dependent on the upstream fws app being installed alongside it.

### Current State (as of 2026-05-23)

**cwp is 95% identical to upstream fws.** The 5% delta is Comfac's UI additions:
- Cart item discount display (strikethrough original price, savings summary, green rate badge)
- Cart payment summary savings row
- Mini-cart navbar dropdown price/discount display
- Associated SCSS/CSS for discount elements

Everything else — routing, DocTypes (`Website Item`, `Webshop Settings`, `Shopping Cart Settings`),
search, checkout, cart logic — is inherited from upstream fws unchanged.

**`hooks.py` line 11 — OPEN BLOCKER for standalone install:**
```python
required_apps = ["payments", "erpnext"]
```
This is unchanged from upstream fws. Installing cwp on any bench without the `payments` app will
fail with `No module named 'payments'`. To achieve true standalone deployment:
- Either remove `payments` from `required_apps` (safe only if cwp uses no payments gateway features)
- Or add the `payments` app to the bench before installing cwp

### Deployment Source

- **Primary remote:** `github-private` → `github.com/Comfac-Global-Group/comfac-webshop-private.git`
- **Frappe Cloud** only accepts GitHub as an app source — this private remote is the deployment path
- **Forgejo** (`git.comfac-it.net/cgg/comfac-webshop`) is the local origin; changes are pushed to
  both remotes manually (not an automated mirror)
- **Public GitHub** (`github.com/Comfac-Global-Group/comfac-webshop`) is the public fork reference —
  keep in sync but do not use as the Frappe Cloud deploy source

### cwp DocTypes

cwp's own `Website Item` doctype is the source of truth for published products on any cwp-powered
bench. When cwp is installed, agents should use `make_website_item()` (in
`webshop/webshop/doctype/website_item/website_item.py`) or the patch
`webshop/patches/create_website_items.py` to create Website Item records from Items that already
have `published_in_website=1`.

### etest Gap (t3.comfac-it.com)

| Signal | State |
|--------|-------|
| cwp in bench `apps/` | ✅ Present |
| cwp installed for site | ❌ Not installed |
| `Website Item` DocType | ❌ DoesNotExistError |
| `/all-products` | ❌ 404 (route handler missing — cwp not installed) |
| Items with `published_in_website=1` | ✅ 89 items |
| Website Item records | ❌ 0 records |

**Root cause of 404:** cwp provides the route handler at `webshop/www/all-products/`. Without cwp
installed for the site, the route doesn't exist, so Frappe returns 404.

**Immediate blocker:** `payments` app is not in the etest bench. Installing cwp fails with
`No module named 'payments'`. Resolve via Frappe Cloud dashboard (add payments app) or by removing
the dependency from `hooks.py` if payments features are unused.

**Next step:** Install cwp on etest bench, then run `create_website_items.py` (or a console script
using `make_website_item()`) to create Website Item records from the 89 published Items. This
completes the webshop layer on etest.
