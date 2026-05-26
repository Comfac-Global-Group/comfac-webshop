# Webshop + comfac_cart Development Backlog

**Owner:** Justin Aquino / Comfac IT Team  
**Last updated:** 2026-05-23  
**Repos:**
- `work/comfac-webstore/` — Frappe Webshop fork (private)
- `work/comfac-cart/comfac_cart/` — custom cart Frappe app (private)

---

## Quick Status

| Item | Status | Effort | Priority |
|------|--------|--------|----------|
| DPA/NPC disclaimer on webshop & websites | 🔴 Not started | 1–2 days | High |
| Merge comfac_cart into webshop | 🔴 Research needed | 3–5 days | Medium |
| Consolidate `payments` app into cws (backlog) | 🔴 Backlog — blocked on cws stability | 5–7 days | Medium |

---

## DEV-001 — DPA / NPC Disclaimer on Webshop and Websites

**Priority:** High — legal compliance (RA 10173)  
**Owner:** [Intern / TBD]  
**Estimated:** 1–2 days  
**Status:** 🔴 Not started

### Background

Republic Act 10173 (Data Privacy Act of 2012) and its IRR require that any website or app collecting personal data must:
1. Notify users of what data is collected and why
2. Obtain consent before collection
3. Disclose the Data Protection Officer (DPO) contact
4. Provide a Privacy Policy accessible from every page
5. For cookies: implement a consent banner before placing non-essential cookies

The National Privacy Commission (NPC) can impose penalties for non-compliance. Comfac already has a Data Privacy Manual (`work/comfac-marketing-sales/251015 (Draft) Comfac Data Privacy Manual_signed.pdf`) and marketing data privacy templates (`work/comfac-marketing-sales/260521 Marketing Data Privacy Policy.docx`). These need to be surfaced on the webshop and all public-facing Comfac websites.

### Scope — Where Disclaimers Are Needed

| Site / App | URL | What's needed |
|-----------|-----|----------------|
| ERPNext Webshop | `erp.comfac-it.com/shop` | Privacy policy link, cookie consent, checkout data notice |
| Comfac main website | (WordPress on PC03) | Cookie consent banner, Privacy Policy page, DPO contact |
| gi7b.org | (WordPress staging/production) | Same as above |
| Any lead capture form | ERPNext web forms | Data collection notice before form submission |
| Nextcloud shared links | `nc.gi7b.org` | Data handling notice (if collecting non-users' data) |

### What to Implement

**1. Privacy Policy Page**
- Create a `/privacy-policy` page on each WordPress site
- Content: what data is collected, why, how long kept, DPO contact, NPC registration number
- Source from: `work/comfac-marketing-sales/260521 Marketing Data Privacy Policy.docx`
- Intern task: convert the `.docx` to HTML and add as a WordPress page

**2. Cookie Consent Banner (WordPress)**
- Install and configure a GDPR/DPA-compliant cookie consent plugin
- Recommended: "Cookie Notice & Compliance for GDPR / CCPA" (free, WordPress plugin)
- Banner must appear before any analytics/tracking cookies are set
- "Accept" and "Decline" options must both work

**3. Webshop (Frappe/ERPNext) — Checkout Data Notice**
- Add a data processing notice on the checkout page: "By completing this purchase, you agree to our [Privacy Policy]. Your data is collected under RA 10173."
- Link to the Privacy Policy page
- Implementation: Frappe Client Script or Jinja template override in webshop
- Must be a visible checkbox or inline notice before the "Place Order" button

**4. Lead Capture Forms**
- Any ERPNext web form used for inquiry / lead generation needs:
  - A note: "We collect this information under RA 10173. Read our [Privacy Policy]."
  - Consent checkbox if data will be used for marketing

**5. DPO Contact Disclosure**
- Every Privacy Policy page must include the DPO name and email
- Justin Aquino is the current DPO (verify with management)
- Email: typically `privacy@comfac-it.com` or `dpo@comfac.com.ph` (confirm)

### Intern Tasks

- [ ] **DEV-001-A:** Read `work/comfac-marketing-sales/260521 Marketing Data Privacy Policy.docx` — extract required disclosure elements
- [ ] **DEV-001-B:** Create Privacy Policy WordPress page on Comfac main site — publish at `/privacy-policy`
- [ ] **DEV-001-C:** Install cookie consent plugin on WordPress → configure → test "Decline" prevents analytics load
- [ ] **DEV-001-D:** Add checkout data notice to ERPNext Webshop checkout template — link to Privacy Policy
- [ ] **DEV-001-E:** Add consent note to all active ERPNext lead capture web forms
- [ ] **DEV-001-F:** Verify DPO name + email with Justin → add to all Privacy Policy pages
- [ ] **DEV-001-G:** Check NPC registration status — if not registered, flag to Justin (NPC registration required for orgs processing personal data)

### Acceptance Criteria
- [ ] Privacy Policy page live on all public Comfac websites
- [ ] Cookie consent banner appears before any tracking on first visit
- [ ] Webshop checkout shows data notice with Privacy Policy link
- [ ] All lead forms include consent/notice text
- [ ] DPO contact visible on all Privacy Policy pages

### Reference Documents
- RA 10173 summary: search NPC website (privacy.gov.ph)
- Comfac Data Privacy Manual: `work/comfac-marketing-sales/251015 (Draft) Comfac Data Privacy Manual_signed.pdf`
- Marketing Privacy Policy template: `work/comfac-marketing-sales/260521 Marketing Data Privacy Policy.docx`

---

## DEV-002 — Combine comfac_cart with Webshop into One App

**Priority:** Medium  
**Owner:** [Senior intern / developer / TBD]  
**Estimated:** 3–5 days (after research phase)  
**Status:** 🔴 Research phase — repo audit needed first

### Background

There are currently two separate private Frappe apps:
1. **`comfac-webstore`** (`work/comfac-webstore/`) — fork of Frappe Webshop with Comfac customizations
2. **`comfac_cart`** (`work/comfac-cart/comfac_cart/`) — custom Frappe app with cart-specific logic

Running two Frappe apps that both touch cart/checkout introduces:
- Maintenance overhead (two repos, two update cycles)
- Potential conflicts on hook execution order
- Confusion about which app owns which behavior
- Harder to deploy for new ERPNext instances (must install both apps)

### Goal

Merge the custom cart logic from `comfac_cart` into `comfac-webstore` so there is **one app** to install. Keep all functionality; remove the duplication.

### Research Phase (Do This First)

Before merging, an intern/developer must audit what each app does:

**Step 1 — Audit `comfac_cart`:**
```bash
# Check what hooks comfac_cart registers
cat work/comfac-cart/comfac_cart/hooks.py

# Check what templates/JS it provides
find work/comfac-cart/ -name "*.html" -o -name "*.js" | head -20

# Check what Python logic it contains
find work/comfac-cart/comfac_cart/ -name "*.py" | grep -v __init__
```

**Step 2 — Audit `comfac-webstore`:**
```bash
# Check hooks
cat work/comfac-webstore/hooks.py

# Check what templates/JS it provides
find work/comfac-webstore/ -name "*.html" -o -name "*.js" | head -30

# Check Python logic
find work/comfac-webstore/webshop/ -name "*.py" | head -20
```

**Step 3 — Identify overlap and unique additions:**
- Map each file/hook in `comfac_cart` to: (a) already exists in webshop, (b) new addition, (c) override of upstream
- Document the map before touching any code

### Migration Plan (After Audit)

1. Copy all unique `comfac_cart` code into the equivalent location in `comfac-webstore`
2. Merge hook registrations (check for duplicates, resolve ordering conflicts)
3. Test on `etest` (`t3.comfac-it.com`) — do not test on `ecit` production
4. Once verified on etest, remove `comfac_cart` app from the ERPNext instance
5. Archive `work/comfac-cart/` to `work/backlog/comfac-cart/`

### Intern Tasks

- [ ] **DEV-002-A:** Audit `comfac_cart/hooks.py` — list every hook and what it does
- [ ] **DEV-002-B:** Audit `comfac-webstore/hooks.py` — list every hook and what it does
- [ ] **DEV-002-C:** Find all Python files in `comfac_cart` — list their purpose
- [ ] **DEV-002-D:** Find all HTML/JS template overrides in `comfac_cart`
- [ ] **DEV-002-E:** Write a gap analysis table: what `comfac_cart` adds that `comfac-webstore` lacks
- [ ] **DEV-002-F:** Present gap analysis to Justin for merge decision
- [ ] **DEV-002-G:** (After approval) Copy unique files into `comfac-webstore` with clear commit messages
- [ ] **DEV-002-H:** Test on `etest` — walk through full cart → checkout → order flow
- [ ] **DEV-002-I:** Deploy merged app to `ecit` — remove `comfac_cart` — verify no regressions

### Acceptance Criteria
- [ ] Gap analysis documented and reviewed
- [ ] Merged `comfac-webstore` passes full checkout flow on etest
- [ ] No regression on `ecit` webshop after deploying merged app
- [ ] `comfac_cart` app uninstalled from all ERPNext instances
- [ ] `work/comfac-cart/` moved to `work/backlog/comfac-cart/`

---

---

## DEV-003 — Consolidate Frappe Payments into comfac-webstore (Backlog)

**Priority:** Medium  
**Owner:** Justin / Senior developer  
**Estimated:** 5–7 days (after cws is stable)  
**Status:** 🔴 **Backlog — DO NOT START until cws is fully working**

### Background

Frappe Webshop (`cws`) currently has:
```python
required_apps = ["payments", "erpnext"]
```

This means every ERPNext instance that runs the webshop must also install the separate `payments` Frappe app. We have decided **not to install `payments` as a standalone app** on any Comfac ERPNext instance. Instead, all payment gateway logic will be absorbed into `cws` so that `cws` is a single, self-contained app.

### Goal

Merge the entire `frappe/payments` codebase into `comfac-webstore` so that:
1. `cws` provides **webshop + payments** in one install
2. `required_apps = ["erpnext"]` only
3. No separate `payments` app needed on `ecit`, `etest`, or `egitb`

### Pre-condition (Hard Blocker)

**cws MUST be fully working before starting DEV-003.** This means:
- [ ] Cart → checkout → order flow works end-to-end on `etest`
- [ ] Tax calculation displays correctly in cart (EXP-018 resolved)
- [ ] Discounts display correctly in cart (EXP-019 resolved and deployed)
- [ ] `comfac_cart` merged into `cws` (DEV-002 complete)
- [ ] DPA/NPC compliance notice on checkout (DEV-001 complete)

### Consolidation Plan (High Level)

**Phase 1 — Audit & Prune**
- [ ] Clone `github.com/frappe/payments` (already done: `work/payments/`)
- [ ] Identify which gateways Comfac actually needs (likely: Stripe, PayPal, Razorpay)
- [ ] Prune unused gateways (Mpesa, Paytm, Paymob, GoCardless, Braintree) if not needed
- [ ] Evaluate Web Form payment override — drop if cws doesn't use Web Form payments

**Phase 2 — Namespace Migration**
- [ ] Copy remaining DocTypes (JSON + Python controllers) into `cws` module
- [ ] Migrate website checkout pages (`templates/pages/*`) into `cws/templates/`
- [ ] Migrate public JS assets into `cws/public/js/`
- [ ] Replace all `payments.` imports with `webshop.` namespace
- [ ] Update whitelisted method paths from `payments.payment_gateways...` to `webshop...`

**Phase 3 — Hooks Integration**
- [ ] Merge `payments` hooks into `cws/hooks.py`:
  - `after_install` / `before_uninstall` (custom fields)
  - `scheduler_events` (Razorpay capture)
  - `extend_doctype_class` (Web Form — if kept)
  - `override_whitelisted_methods` (Web Form accept)
- [ ] Merge Python dependencies into `cws/pyproject.toml`

**Phase 4 — Payment Request Compatibility**
- [ ] Ensure `cws`'s existing `PaymentRequest` override works with migrated gateway controllers
- [ ] Verify `on_payment_authorized` contract is satisfied for each gateway
- [ ] Test checkout → payment → order completion on `etest`

**Phase 5 — Cleanup**
- [ ] Uninstall `payments` app from `etest`
- [ ] Verify `cws` alone handles webshop + payments
- [ ] Deploy to `ecit`
- [ ] Archive `work/payments/` or keep as reference

### Acceptance Criteria
- [ ] `payments` app is **not installed** on any Comfac ERPNext instance
- [ ] `cws` installs and runs with `required_apps = ["erpnext"]` only
- [ ] Stripe / PayPal / Razorpay checkout flows work end-to-end on `etest`
- [ ] No regression in existing webshop functionality
- [ ] All gateway callbacks and webhooks function correctly under `webshop.` namespace

### Reference
- Frappe Payments repo (cloned): `work/payments/`
- Deep analysis of payments app: see session log `work/comfac-erpnext/260504-150305-erpnext-log.md` → 2026-05-23 entry
- `cws` hooks.py: `work/comfac-webstore/webshop/hooks.py`
- `cws` pyproject.toml: `work/comfac-webstore/pyproject.toml`

---

## Related Files

- Webshop wiki: `work/comfac-webstore/CIT-Wiki/`
- Webshop PRD: `work/comfac-webstore/PRD.md`
- Webshop analysis: `work/comfac-webstore/ANALYSIS.md`
- Comfac Data Privacy Manual: `work/comfac-marketing-sales/251015 (Draft) Comfac Data Privacy Manual_signed.pdf`
- Marketing Privacy Policy: `work/comfac-marketing-sales/260521 Marketing Data Privacy Policy.docx`
- ERPNext test instance (etest): `t3.comfac-it.com` — credentials in `agent260222/.brc/ERPNext etest`
- ERPNext prod (ecit): `erp.comfac-it.com` — credentials in `agent260222/.brc/ERPNext Comfac IT`
