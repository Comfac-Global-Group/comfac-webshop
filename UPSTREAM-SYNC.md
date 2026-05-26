# cws Upstream Sync — How to Update from Frappe WebShop

**Last updated:** 2026-05-23  
**Repo:** `work/comfac-webstore` (cws)  
**Upstream:** `https://github.com/frappe/webshop` (fws)

---

## Background

cws is 95% identical to upstream Frappe WebShop (fws). Comfac's changes live in exactly
**5 source files**. Everything else is upstream and safe to overwrite.

When fws ships bug fixes or new features, you pull them into cws by merging upstream into
`develop`, resolving conflicts in those 5 files, then pushing to all remotes.

---

## Comfac's 5 Changed Files

These are the ONLY files where conflicts require manual review. In every other file, take
the upstream version.

| File | What Comfac Added |
|------|-------------------|
| `webshop/public/scss/webshop_cart.scss` | `.original-price`, `.discounted-rate`, `.discount-badge` CSS in `.item-rate` and `.cart-dropdown` contexts |
| `webshop/templates/includes/cart/cart_items.html` | Strikethrough original price + green rate + discount badge when `discount_percentage` is set |
| `webshop/templates/includes/cart/cart_items_dropdown.html` | Same pattern for mini-cart navbar dropdown |
| `webshop/templates/includes/cart/cart_items_total.html` | "Original Subtotal" + "Item Discounts" rows above Net Total when savings > 0 |
| `webshop/templates/includes/cart/cart_payment_summary.html` | "Your Savings" row using `total_savings` namespace calculation |

The full diff of each file against upstream is in git — use `git diff <upstream-commit>..HEAD -- <file>`
to see exactly what Comfac added.

---

## Remote Setup (one-time, per machine)

The upstream fws remote is NOT in the repo by default. Add it once:

```bash
cd work/comfac-webstore
git remote add upstream https://github.com/frappe/webshop.git
git fetch upstream
```

Verify remotes:
```bash
git remote -v
# upstream   https://github.com/frappe/webshop.git (fetch)
# upstream   https://github.com/frappe/webshop.git (push)
# origin     https://git.comfac-it.net/cgg/comfac-webstore.git
# github     https://...github.com/Comfac-Global-Group/comfac-webstore.git
# github-private  https://...github.com/Comfac-Global-Group/comfac-webstore-private.git
```

---

## Step-by-Step: Pulling an Upstream Update

### Step 1 — Fetch upstream

```bash
git fetch upstream
```

### Step 2 — See what's new

```bash
# Upstream commits we don't have yet
git log --oneline HEAD..upstream/develop

# Which of our 5 files upstream touched (potential conflicts)
git diff HEAD..upstream/develop --name-only | grep -E \
  "webshop_cart\.scss|cart_items\.html|cart_items_dropdown\.html|cart_items_total\.html|cart_payment_summary\.html"
```

If the conflict list is empty for our 5 files, the merge will be clean — proceed.
If any of the 5 appear, read the upstream diff for that file before merging:

```bash
git diff HEAD..upstream/develop -- webshop/templates/includes/cart/cart_items.html
```

### Step 3 — Merge upstream

```bash
git merge upstream/develop --no-ff -m "chore: merge upstream fws <version or date>"
```

### Step 4 — Resolve conflicts in the 5 files

For each conflicted file, the rule is:

> **Keep Comfac's additions. Take upstream's structural changes.**

#### `cart_items.html` — conflict strategy

Upstream owns the outer macro structure. Comfac owns the `{% if item.discount_percentage %}` block
inside the `{% else %}` branch (non-free items). If upstream changed the surrounding structure,
adapt Comfac's block to fit — do NOT lose the discount display logic.

Comfac's block (must survive):
```jinja2
{% if item.discount_percentage %}
    {% if item.price_list_rate and item.price_list_rate != item.rate %}
        <span class="original-price text-muted" style="text-decoration: line-through;">
            {{ item.get_formatted('price_list_rate') }}
        </span>
    {% endif %}
    <span class="discounted-rate text-success ml-2">
        {{ item.get_formatted('rate') }}
    </span>
    <span class="discount-badge badge badge-success ml-2">
        -{{ frappe.utils.cstr(item.discount_percentage | int) }}%
    </span>
{% else %}
    <span class="item-rate">
        {{ _('Rate:') }} {{ item.get_formatted('rate') }}
    </span>
{% endif %}
```

#### `cart_items_dropdown.html` — conflict strategy

Comfac owns the `.col-amount` div content. Upstream owns everything else.
The Comfac block is the `{% if d.discount_percentage %}...{% else %}` inside `.col-amount`.

#### `cart_items_total.html` — conflict strategy

Comfac added a `{% set total_savings %}` namespace block and two `<tr>` rows BEFORE the upstream
Net Total `<tr>`. If upstream changed the Net Total row, take upstream's version and keep Comfac's
rows above it.

#### `cart_payment_summary.html` — conflict strategy

Comfac added:
1. A `{% set total_savings %}` namespace calculation block (before `<div class="card">`)
2. A `<tr>` "Your Savings" row (first row inside the `<table>`)

Keep both. If upstream changed the table structure, adapt the Your Savings row to fit.

#### `webshop_cart.scss` — conflict strategy

Comfac added two SCSS blocks. Both are additive (no upstream rules were modified):

1. Inside `.item-rate` (around line 715): `.original-price`, `.discounted-rate`, `.discount-badge`
2. At end of file: `.cart-dropdown { .col-amount { ... } }` block

If upstream added new rules at the end of the file, put Comfac's `.cart-dropdown` block AFTER
upstream's new rules. The file must end with `}` (no trailing newline issue from upstream).

### Step 5 — Mark conflicts resolved and commit

```bash
git add webshop/public/scss/webshop_cart.scss
git add webshop/templates/includes/cart/cart_items.html
git add webshop/templates/includes/cart/cart_items_dropdown.html
git add webshop/templates/includes/cart/cart_items_total.html
git add webshop/templates/includes/cart/cart_payment_summary.html
git merge --continue
```

### Step 6 — Verify Comfac changes survived

```bash
# Each of these should return non-zero line counts
grep -c "discount_percentage" webshop/templates/includes/cart/cart_items.html
grep -c "discount_percentage" webshop/templates/includes/cart/cart_items_dropdown.html
grep -c "total_savings" webshop/templates/includes/cart/cart_items_total.html
grep -c "total_savings" webshop/templates/includes/cart/cart_payment_summary.html
grep -c "discount-badge" webshop/public/scss/webshop_cart.scss
```

All should output `1` or more. If any output `0`, the Comfac block was lost — check the merge.

Also verify the diff from last upstream commit still shows only Comfac additions:

```bash
git diff upstream/develop -- webshop/templates/includes/cart/cart_items.html
```

### Step 7 — Push to all remotes

```bash
git push origin develop           # Forgejo (citfj) — local primary
git push github develop           # GitHub public fork
git push github-private develop   # GitHub private — this is Frappe Cloud's source
```

---

## Step 8 — Deploy on Frappe Cloud

Frappe Cloud fetches from `github-private` (`comfac-webstore-private.git`).

1. Go to `frappecloud.com` → target site (ecit or etest)
2. Apps → comfac-webstore-private → Deploy
3. Wait for deploy to complete
4. **Assets require a build** — trigger via the Frappe Cloud dashboard (SSH `bench build` causes OOM)
5. After deploy: SSH into bench → `bench --site <site> clear-cache` to clear Jinja template cache

```bash
# Cache clear via SSH (Jinja templates take effect immediately after clear)
echo "bench --site erp.comfac-it.com clear-cache; exit" | ssh -i /home/justin/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes -o RequestTTY=force \
  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  bench-27003-000047-f21s@n2-singapore.frappe.cloud -p 2222
```

For etest, use site `test260204.s.frappe.cloud` and bench user `bench-35107-000002-f23s`.

---

## When to Check for Upstream Updates

- Before starting any new cws feature (avoid building on stale code)
- When fws ships a release tag on GitHub
- When a bug in cws might already be fixed upstream

Check if anything new exists:
```bash
git fetch upstream
git log --oneline HEAD..upstream/develop | head -10
```

If the output is empty, cws is current.

---

## What NOT to Sync from Upstream

Do not merge upstream changes to `hooks.py` required_apps without review. The current state:

```python
required_apps = ["payments", "erpnext"]   # line 11, hooks.py
```

This is unchanged from upstream fws. The long-term goal is to remove `payments` from this list
so cws installs standalone. Check whether upstream has already removed it before doing so manually.
If upstream has removed it, take the upstream version. If not, do not remove it without confirming
that cws uses no payment gateway features from the payments app.

---

## Quick Reference

```bash
# Full update sequence (clean case — no conflicts)
git fetch upstream
git log --oneline HEAD..upstream/develop          # preview new commits
git merge upstream/develop --no-ff -m "chore: merge upstream fws $(date +%Y-%m-%d)"
git push origin develop
git push github develop
git push github-private develop
```

Then deploy via Frappe Cloud dashboard + clear-cache via SSH.
