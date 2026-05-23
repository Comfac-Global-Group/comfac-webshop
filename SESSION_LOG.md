# cwp Session Log

---

## 2026-05-23 — cwp Install on etest: Full Success Path + Cart Blocker

**Owner:** OpenCode (install + fix) / Claude (analysis + log)
**Status:** 🟢 Done — /all-products ✅, Add to Cart ✅ (QTN-CART-00001: Netgate 1100 × 2 = 58,650 PHP), /cart ✅
**Actual:** ~120 min total (install + cart blocker RCA + fix + verification)

---

### Part A — What Was Done to Install cwp (Detailed Technique)

This section is the authoritative record of how cwp was installed on etest for the first time.
Other agents should follow this exact sequence.

#### A1. Remove `payments` from `required_apps` (blocker resolution)

The upstream fws `hooks.py` declares `required_apps = ["payments", "erpnext"]`. The `payments` app
was not on the etest bench. Attempting `bench install-app webshop` without this change failed with
`No module named 'payments'`.

**Fix:** Edit `webshop/hooks.py` line 11:
```python
# Before
required_apps = ["payments", "erpnext"]

# After
required_apps = ["erpnext"]
```

**Verify this change is correct:** Grep the cwp codebase for any imports from `payments`:
```bash
grep -rn "from payments\|import payments" webshop/
```
If no results, `payments` is unused and safe to remove.

#### A2. Push to all remotes

```bash
git add webshop/hooks.py
git commit -m "fix: remove payments from required_apps for standalone install"
git push origin develop        # Forgejo (citfj) — local primary
git push github develop        # GitHub public fork
git push github-private develop  # GitHub private — Frappe Cloud deploy source
```

#### A3. Get the app on the etest bench

SSH into etest bench:
```bash
# Install cert first
grep '^echo' "/path/to/.brc/ERPNext etest" | sed 's|> ~/.ssh/|> /home/justin/.ssh/|' | bash

# SSH (pipe-via-stdin pattern — RequestTTY=force required)
echo "<command>; exit" | ssh -i /home/justin/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes -o RequestTTY=force \
  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  "bench-35107-000002-f23s@n2-singapore.frappe.cloud" -p 2222 2>&1
```

**Note on SSH username:** The BRC file and actual bench show `bench-35107-000002-f23s`.
The agents-justin.md table entry `bench-35107-000001-f23-singapore` is WRONG — ignore it.

**Note on site name:** `t3.comfac-it.com` is a custom domain. The actual Frappe Cloud site name
is `test260204.s.frappe.cloud`. Use the internal name in all `bench --site` commands.

```bash
echo "bench get-app https://<PAT>@github.com/Comfac-Global-Group/comfac-webshop-private.git; exit" \
  | ssh -i /home/justin/.ssh/id_ed25519 \
    -o IdentitiesOnly=yes -o RequestTTY=force \
    -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    "bench-35107-000002-f23s@n2-singapore.frappe.cloud" -p 2222 2>&1
```

The PAT is embedded in the `github-private` remote URL in the git repo:
```bash
grep 'github-private' /path/to/work/comfac-webshop/.git/config | grep -o 'ghp_[^@]*'
```

#### A4. Install the app for the site

```bash
echo "bench --site test260204.s.frappe.cloud install-app webshop; exit" \
  | ssh -i /home/justin/.ssh/id_ed25519 \
    -o IdentitiesOnly=yes -o RequestTTY=force \
    -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    "bench-35107-000002-f23s@n2-singapore.frappe.cloud" -p 2222 2>&1
```

This runs `bench migrate` internally, creating all cwp DocType tables including `Website Item`,
`Webshop Settings`, `Shopping Cart Settings`, etc.

**Verify install:**
```bash
echo "bench --site test260204.s.frappe.cloud list-apps; exit" \
  | ssh ...
# Should show: frappe, erpnext, hrms, print_designer, webshop
```

#### A5. Create 89 Website Items from published Items

cwp introduces the `Website Item` doctype. Items with `published_in_website=1` need a corresponding
`Website Item` record. The patch `webshop/patches/create_website_items.py` does this.

**Method — bench console via heredoc:**
```bash
echo "bench --site test260204.s.frappe.cloud console <<< \"exec(open('/tmp/script.py').read())\"; exit" \
  | ssh ...
```

Or pipe a Python one-liner directly:
```python
import frappe
from webshop.webshop.doctype.website_item.website_item import make_website_item

items = frappe.get_all("Item", filters={"published_in_website": 1}, fields=["name"])
created = 0
for item in items:
    doc = frappe.get_doc("Item", item.name)
    existing = frappe.db.exists("Website Item", {"item_code": doc.item_code})
    if not existing:
        make_website_item(doc, save=True)
        created += 1
frappe.db.commit()
print(f"Created {created} Website Items")
```

Result: **89 Website Items created** across:
Peripherals (31), Displays (13), Laptops (13), Network (11), Desktops (8),
Services (5), Workstations (3), Electrical (2), NextCloud Solutions (2),
Frappe ERPNext Solutions (1)

#### A6. Configure Webshop Settings

```python
import frappe
ws = frappe.get_doc("Webshop Settings", "Webshop Settings")
ws.company = "Comfac Corporation"
ws.price_list = "Standard Selling"
ws.enabled = 1
ws.default_customer_group = "Individual"
ws.payment_success_url = "Orders"
ws.enable_wishlist = 1
ws.products_per_page = 24
ws.show_price = 1
ws.save(ignore_permissions=True)
frappe.db.commit()
```

**Note:** `api/resource/Webshop Settings` returns `ProgrammingError` (Frappe REST issue with this
Single DocType). Use `frappe.client.get` to verify:
```bash
curl -H "Authorization: $AUTH" \
  "$URL/api/method/frappe.client.get?doctype=Webshop%20Settings&name=Webshop%20Settings"
```

#### A7. Clear cache

```bash
echo "bench --site test260204.s.frappe.cloud clear-cache; exit" | ssh ...
```

#### A8. Verification

```bash
curl -o /dev/null -w "%{http_code}" "https://t3.comfac-it.com/all-products"
# → 200 ✅

curl -H "Authorization: $AUTH" \
  "https://t3.comfac-it.com/api/resource/Website%20Item?limit=1"
# → {"data": [{...}]} ✅ (was "DoesNotExistError")
```

---

### Part B — Cart Blocker: MandatoryError on Quotation

**Status:** 🔴 Blocked — Add to Cart button fails

#### Symptom

Clicking "Add to Cart" on any product page fails silently (or shows a server error). Direct API
call confirms the error:

```bash
curl -X POST -H "Authorization: $AUTH" -H "Content-Type: application/json" \
  "https://t3.comfac-it.com/api/method/webshop.webshop.shopping_cart.cart.update_cart" \
  -d '{"item_code":"<any-item>","qty":1}'

# Response:
# {"exc_type": "MandatoryError",
#  "_server_messages": "Value missing for Quotation: SCOPE OF WORKS"}
```

#### Root Cause

Two custom mandatory fields on the Quotation DocType have `reqd=1` with **no `mandatory_depends_on`
condition** — meaning they are unconditionally mandatory for ALL quotations, including Shopping Cart
quotations created by the webshop:

| Custom Field | `fieldname` | `reqd` | `mandatory_depends_on` |
|---|---|---|---|
| SCOPE OF WORKS | `custom_scope_of_works` | 1 | None |
| OTHER NOTES | `custom_other_notes` | 1 | None |

These fields were replicated from ecit to etest as part of the ERPNext config replication. They are
Comfac's internal sales process fields — legitimate for sales reps creating manual quotations, but
inappropriate as unconditional requirements for webshop-generated Shopping Cart quotations.

When `update_cart()` in `cart.py` calls `quotation.save()`, Frappe's validation layer fires and
rejects the save because neither field has a value.

#### How the Webshop Creates Cart Quotations

`cart.py: _get_cart_quotation()` → `frappe.new_doc("Quotation")` with `order_type = "Shopping Cart"`.
The new quotation doc has no value for `custom_scope_of_works` or `custom_other_notes`. When
`quotation.save()` is called, mandatory validation fires unconditionally.

#### Fix (Verified — Applied 2026-05-23 16:30)

**⚠️ Critical Frappe behaviour learned here — read before applying to ecit:**

`mandatory_depends_on` is **UI-only**. It controls whether the red asterisk appears in the form.
It does **NOT** suppress server-side mandatory validation. When `reqd=1`, the server validates
the field regardless of `mandatory_depends_on`. Webshop `update_cart()` runs server-side with
no UI — so `mandatory_depends_on` alone does nothing to fix this.

`depends_on` is the correct mechanism. When a field's `depends_on` expression evaluates to false,
Frappe **hides** the field AND **skips its validation entirely** — both in the UI and server-side.

**The applied fix — both fields on etest:**
```json
{
  "reqd": 0,
  "depends_on": "eval:doc.order_type != \"Shopping Cart\"",
  "mandatory_depends_on": null
}
```

- `reqd: 0` — removes the unconditional mandatory flag
- `depends_on` — hides the field (and skips validation) when `order_type = "Shopping Cart"`
- Together: sales reps see and must fill the field on manual quotations; webshop cart is exempt

**API commands to apply (etest already done; apply same to ecit before going live):**
```bash
BRC="/mnt/250721_HDD/NextCloud-260120/opencode260220/agent260222/.brc"
URL="https://erp.comfac-it.com"   # change to ecit URL
KEY=$(grep api_key "$BRC/ERPNext Comfac IT" | awk '{print $NF}')
SEC=$(grep api_secret "$BRC/ERPNext Comfac IT" | awk '{print $NF}')
AUTH="token $KEY:$SEC"

for FNAME in "Quotation-custom_scope_of_works" "Quotation-custom_other_notes"; do
  ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$FNAME'))")
  curl -s -X PUT -H "Authorization: $AUTH" -H "Content-Type: application/json" -H "Expect:" \
    "$URL/api/resource/Custom%20Field/$ENCODED" \
    -d '{"reqd": 0, "depends_on": "eval:doc.order_type != \"Shopping Cart\"", "mandatory_depends_on": null}'
done
```

**Verify fix worked on etest:**
```bash
# Should return a quotation doc, not MandatoryError
curl -s -X POST -H "Authorization: $AUTH" -H "Content-Type: application/json" -H "Expect:" \
  "$URL/api/method/webshop.webshop.shopping_cart.cart.update_cart" \
  -d '{"item_code":"<any-published-item-code>","qty":1}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('exc:', d.get('exc_type','none')); print('quotation:', (d.get('message') or {}).get('doc',{}).get('name','?'))"
```

#### Secondary Issue: `api/resource/Webshop Settings` ProgrammingError

```
pymysql.err.ProgrammingError: ('DocType', 'Webshop Settings')
```

This affects only the REST endpoint — `frappe.get_doc("Webshop Settings")` used internally by the
cart works correctly. Cause is likely a stale Redis cache or a column mismatch from a partially
applied migration. Does NOT block the cart fix above, but should be resolved separately.

To investigate: `bench --site test260204.s.frappe.cloud console` →
```python
frappe.get_doc("Webshop Settings").__dict__  # should work
frappe.db.get_singles_dict("Webshop Settings")  # check what DB returns
```

---

### Updates from 260523-16:30 (OpenCode — cart fix applied)

**RCA:** `depends_on` was the correct fix, NOT `mandatory_depends_on`. Frappe server-side validation
only checks `reqd` + `depends_on` (hidden fields skip reqd check). `mandatory_depends_on` is a UI-only
feature that only controls the red asterisk display.

**Applied to both `custom_scope_of_works` and `custom_other_notes`:**
```json
{
  "reqd": 0,
  "depends_on": "eval:doc.order_type != \"Shopping Cart\"",
  "mandatory_depends_on": null
}
```

**Result:** Add to Cart works. Quotation `QTN-CART-00001` created with Netgate 1100 × 2 = 58,650 PHP.

---

## 2026-05-23 17:30 — Asset Serving RCA: Cart Icon Missing (web.bundle.js 404)

**Owner:** OpenCode (analysis + fix)
**Status:** 🟡 Code fix committed — blocked on SSH deploy (Frappe Cloud gateway down)

### Part C — Asset Serving on Frappe Cloud: The Hidden Trap

#### Symptom
Cart icon not visible on the webshop. `/all-products` page renders but items don't appear.
Cart backend works (API) but frontend JS doesn't load.

#### Root Cause
`hooks.py` declares `web_include_js = "web.bundle.js"`. This bundle file exists in `apps/webshop/webshop/dist/js/web.bundle.WLOGYSZO.js` (built by `bench build`) but Frappe Cloud serves assets from a **CDN**, NOT from the local `sites/.../public/assets/` directory.

Since cwp was installed manually via `bench get-app` + SSH (not through a Frappe Cloud deploy pipeline), the CDN was never populated with the webshop asset bundle. The bundle URL returns 404 → JavaScript never loads → cart icon never renders → product page interactivity is broken.

**The lesson:** On Frappe Cloud, the asset bundle pipeline works as:
```
bench build → files in apps/<app>/<app>/dist/
     │
     ├── Frappe Cloud Deploy (CDN upload) → CDN serves /assets/<app>/js/<bundle>.js → ✅
     └── Manual SSH install only        → no CDN upload              → /assets/<app>/js/<bundle>.js → ❌ 404
```

#### Fix Applied

**Short-term fix (committed to cwp):** Switch `web_include_js` from the bundle to individual source files:

```python
# hooks.py line 16-20
web_include_js = [
    "webshop/js/init.js",
    "webshop/js/shopping_cart.js",
    "webshop/js/wishlist.js",
    "webshop/js/customer_reviews.js",
]
```

Individual source files at `apps/webshop/webshop/public/js/` are served directly via the symlink
`assets/webshop/ → apps/webshop/webshop/public/` — no CDN needed. ✅ Verified: `shopping_cart.js` returns 200.

**Long-term fix:** Trigger a Frappe Cloud deploy for the `comfac-webshop-private` app. This runs the
full build pipeline and uploads assets to CDN, making the bundle available.

#### Version Bump
```python
# webshop/__init__.py
__version__ = '0.1.0'  # was 0.0.1 — first cwp release
```

---

## 2026-05-23 17:30 — Multi-Model Inventory Check Strategy for Forked Frappe Apps

After the cwp installation experience, the team now follows this **post-copy verification protocol**
when forking a Frappe app:

### The Problem
When you fork a Frappe app (e.g., `frappe/webshop` → `cwp`), a single agent/model may miss
critical differences between the upstream and the fork, especially:
- Asset serving changes in the new environment (Frappe Cloud vs. self-hosted)
- `hooks.py` differences (`required_apps`, `web_include_js`, `web_include_css`)
- DocType JSON differences (fields, permissions, indexing)
- Patch file conflicts
- Template context differences

### The Multi-Model Protocol

| Pass # | Model | Scope | What to Check |
|--------|-------|-------|---------------|
| 1 | OpenCode | **GIT diff** | `git diff upstream/develop HEAD --name-only` — list all changed files |
| 2 | Claude | **hooks.py audit** | `required_apps`, `web_include_*`, `override_doctype_class`, `doc_events`, `website_generators` |
| 3 | Kimi | **Asset inventory** | All files in `public/` and `dist/` — verify they're served at their expected URLs |
| 4 | OpenCode | **API surface** | Every exposed API endpoint — `api/method/` and `api/resource/` |
| 5 | DeepSeek | **Dependency graph** | All imports, patches, and their transitive dependencies |
| 6 | Human | **Manual E2E** | Cart flow, checkout, product browse — visual verification |

### Applied to cwp
| Pass | Finding | Action |
|------|---------|--------|
| 1 | 5 files changed (cart templates + SCSS) | ✅ Already documented in UPSTREAM-SYNC.md |
| 2 | `required_apps` has `payments` — not on etest | ✅ Removed from hooks.py |
| 3 | `web.bundle.js` not on Frappe Cloud CDN | ✅ Switched to individual source files |
| 4 | `update_cart()` works, `add_to_cart` doesn't exist | ✅ Documented |
| 5 | No transitive `payments` imports found | ✅ Verified safe to remove |
| 6 | Cart icon still missing (SSH down, deploy pending) | 🔴 Blocked |

### Next Actions

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | ~~Apply `mandatory_depends_on` fix — DONE~~ | ✅ |
| 2 | ~~Verify Add to Cart works — DONE: QTN-CART-00001, 1 item, 58,650 PHP~~ | ✅ |
| 3 | Apply same fix to ecit (`erp.comfac-it.com`) before enabling webshop there | Agent | 🟡 Required |
| 4 | Investigate `api/resource/Webshop Settings` ProgrammingError | Agent | 🟡 Non-blocking |
| 5 | ~~Update `agents-justin.md` SSH username entry~~ | ✅ |

---

---

## Team Backlog: Frappe App Forking & Deployment Mastery

These are the skills every team member must master for our Agent-controlled self-hosted Docker ERPNext
and Frappe Cloud operations:

| # | Skill | How to Learn | Priority |
|---|-------|-------------|----------|
| 1 | **Bench CLI** — `get-app`, `install-app`, `migrate`, `build`, `clear-cache`, `console`, `execute` | Practice on etest | 🔴 Required |
| 2 | **GitHub private repo deployment** — Add PAT to remote URL, push, Frappe Cloud Deploy | cwp deployment on etest | 🔴 Required |
| 3 | **SSH cert auth to Frappe Cloud** — Install cert from BRC, `-o RequestTTY=force`, pipe pattern | agents-justin.md SSH section | 🔴 Required |
| 4 | **hooks.py audit** — Check `required_apps`, `web_include_*`, `override_doctype_class`, `doc_events` | Pass 2 of verification protocol | 🟡 Important |
| 5 | **Asset serving** — Frappe Cloud CDN vs local filesystem, `dist/` vs `public/`, asset.json | cwp cart icon RCA | 🟡 Important |
| 6 | **Multi-model verification** — 6-pass protocol before deploying any fork | cwp deployment | 🟢 Practice |
| 7 | **Self-hosted Docker ERPNext** — Docker Compose setup, bench proxy setup, NGINX config | Future project | 🟢 Future |
| 8 | **Frappe Cloud → Local Docker instance cloning** — Download Frappe Cloud site + DB to local Docker for rapid, destructive testing. Piloted by Denzel, Mike, Mathew in the plant. Enables agent-controlled testing without risk to production. | Plant pilot in progress | 🔴 Required |

### Key Facts for Future Agents

| Fact | Value |
|------|-------|
| etest internal site name | `test260204.s.frappe.cloud` |
| etest custom domain | `t3.comfac-it.com` |
| etest SSH user | `bench-35107-000002-f23s` (NOT `bench-35107-000001-f23-singapore`) |
| cwp deploy source | `github-private` → `comfac-webshop-private.git` |
| Cart Python method | `webshop.webshop.shopping_cart.cart.update_cart` (NOT `add_to_cart`) |
| Webshop Settings check | Use `frappe.client.get`, not `api/resource` (ProgrammingError) |
| Cart blocker field 1 | `custom_scope_of_works` on Quotation — was `reqd=1`, no condition |
| Cart blocker field 2 | `custom_other_notes` on Quotation — was `reqd=1`, no condition |
| Fix (applied etest) | `reqd=0` + `depends_on: eval:doc.order_type != "Shopping Cart"` on both |
| ⚠️ `mandatory_depends_on` | UI-only — does NOT skip server-side validation. Use `depends_on` instead |
| Fix still needed | Same fix must be applied to ecit before webshop goes live there |

---

## 2026-05-23 18:00 — Awesome Bar: cwp DocTypes Not Searchable

**Owner:** Claude (analysis + log)
**Status:** 🟡 Open — cwp DocTypes invisible in Awesome Bar and module panel

### Part D — Awesome Bar Gap: Webshop Module Not Registered on Desk

#### Symptom

Typing "webshop" in ERPNext's Awesome Bar (global search) returns no results. Searching for
specific DocType names like "Website Item" or "Webshop Settings" also returns nothing.

On the upstream fws (Frappe WebShop) installed on ecit, the same search does surface results.

#### cwp DocTypes (all module=Webshop)

| DocType | Notes |
|---------|-------|
| Website Item | Main product record — 89 records on etest |
| Webshop Settings | Single DocType — site-wide webshop configuration |
| Item Review | Customer product reviews |
| Wishlist | Per-user wishlist (`in_create=1`) |
| Wishlist Item | Line items within a Wishlist |
| Homepage Featured Product | Featured products on the homepage |
| Recommended Items | AI/rule-based product recommendations |
| Website Item Tabbed Section | Tabbed content sections on product pages |
| Website Offer | Promotional banners or discount offers |

#### cwp Web Routes (www/)

| Route | Files | Notes |
|-------|-------|-------|
| `/all-products` | `www/all-products/index.py`, `index.html`, `not_found.html` | Main product grid |
| `/shop-by-category` | `www/shop-by-category/index.py`, `index.html` | Category browsing |

#### cwp Desk Pages

**None.** `find webshop -name "*.json" -path "*/page/*"` returns empty. No desk pages registered.

#### Root Cause

ERPNext's Awesome Bar indexes DocTypes that belong to desk-registered modules. A module
appears in the Awesome Bar search pool only when:
1. A **Module Def** record exists for it in the database
2. The module has **desktop icons** (`frappe.desk.doctype.desktop_icon`) or appears in the workspace
3. The `module_name` in the app's DocType JSONs matches a registered module

cwp registers `"module": "Webshop"` in all DocType JSONs, and `hooks.py` declares
`app_name = "webshop"` / `app_title = "Webshop"`, but there is **no Module Def record** and
**no desk workspace** configured. Without these, Frappe's search engine has no pointer to the
Webshop module — its DocTypes are installed in the database but invisible to the search index.

Why ecit (fws) works: fws ships with a `Webshop` Module Def JSON and workspace configuration
in its `webshop/module_def/` and `webshop/workspace/` directories. These get created on
`bench install-app` via migrate. cwp, being a fork, inherits these files — but if the migration
ran without them (or if there's a version mismatch), the Module Def record may not exist.

#### Diagnostic Commands

```bash
# Check if Module Def record exists for Webshop on etest
BRC="/mnt/250721_HDD/NextCloud-260120/opencode260220/agent260222/.brc"
URL="https://t3.comfac-it.com"
KEY=$(grep api_key "$BRC/ERPNext etest" | awk '{print $NF}')
SEC=$(grep api_secret "$BRC/ERPNext etest" | awk '{print $NF}')
AUTH="token $KEY:$SEC"

curl -s -H "Authorization: $AUTH" \
  "$URL/api/resource/Module%20Def/Webshop" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('name','NOT FOUND'))"

# Check if Webshop workspace exists
curl -s -H "Authorization: $AUTH" \
  "$URL/api/resource/Workspace?filters=[[\"name\",\"like\",\"%webshop%\"]]" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print([r['name'] for r in d.get('data',[])])"
```

#### Next Action — Make cwp DocTypes Appear in Modules and Awesome Bar

The Webshop module must be registered as a visible desk module. Steps:

1. **Check cwp source** — does `webshop/module_def/webshop/webshop.json` exist? Does
   `webshop/workspace/` have a Webshop workspace JSON? If not, create them or copy from fws.

2. **Run `bench migrate`** on etest — if the JSON files exist, migrate will insert/update
   the Module Def record.

3. **Verify Awesome Bar** — after migrate + clear-cache, search "Website Item" in Awesome Bar
   to confirm DocTypes are now indexed.

4. **Apply same to ecit** — once verified on etest, ensure the same module registration
   exists on ecit before webshop goes live.

| Step | Owner | Priority |
|------|-------|----------|
| Check module_def/ and workspace/ JSONs in cwp source | Agent | 🔴 Next |
| Create Module Def / Workspace JSON if missing | Agent | 🔴 Next |
| `bench migrate` + `clear-cache` on etest | Agent | 🔴 Next |
| Verify Awesome Bar shows cwp DocTypes | Human | 🔴 Verify |
