# Staging Sandbox: Testing & Seamless Webshop Replacement

## Concept: "Comfac Staging Sandbox"

A cloned copy of the production ERPNext instance where we install our custom `comfac-webshop` fork, validate it works identically to the existing webshop, then iterate on new features until they're proven stable before deploying to production.

We'll call this process the **Staging Sandbox** - a safe testing ground where we:
1. Verify the fork is a seamless drop-in replacement
2. Add discount visibility features
3. Build the System Builder
4. Test with sample products, services, and promotions

---

## Step 1: Backup the Production Instance

### Full Backup
```bash
# On the production server
bench --site your-site.com backup --with-files

# This creates:
#   ~/frappe-bench/sites/your-site.com/private/backups/
#     - YYYYMMDD_HHMMSS-your_site_com-database.sql.gz    (database)
#     - YYYYMMDD_HHMMSS-your_site_com-files.tar           (uploaded files)
#     - YYYYMMDD_HHMMSS-your_site_com-private-files.tar   (private files)
```

### Verify Backup
```bash
# Check backup files exist and are reasonable size
ls -lh ~/frappe-bench/sites/your-site.com/private/backups/

# Copy backups to a safe location (off-server)
scp ~/frappe-bench/sites/your-site.com/private/backups/* user@backup-host:/backups/
```

### Record Current State
```bash
# Document current app versions
bench version --format table
# Document installed apps
bench --site your-site.com list-apps
# Note the current webshop version specifically
cd ~/frappe-bench/apps/webshop && git log --oneline -5
```

---

## Step 2: Create the Staging Clone

### Option A: Clone on Same Server (different site)

```bash
# Create a new site
bench new-site staging.your-site.com --db-name staging_db

# Restore production backup into staging
bench --site staging.your-site.com restore \
  ~/frappe-bench/sites/your-site.com/private/backups/YYYYMMDD-database.sql.gz \
  --with-private-files ~/frappe-bench/sites/your-site.com/private/backups/YYYYMMDD-private-files.tar \
  --with-public-files ~/frappe-bench/sites/your-site.com/private/backups/YYYYMMDD-files.tar
```

### Option B: Clone on Separate Server/VM (recommended)

```bash
# On the staging server, set up a fresh bench
bench init frappe-bench --frappe-branch version-15
cd frappe-bench

# Install required apps (same versions as production)
bench get-app erpnext --branch version-15
bench get-app payments --branch version-15

# Install our forked webshop INSTEAD of the official one
bench get-app webshop https://github.com/xunema/comfac-webshop.git

# Create site and restore
bench new-site staging.comfac.com
bench --site staging.comfac.com restore /path/to/database.sql.gz \
  --with-private-files /path/to/private-files.tar \
  --with-public-files /path/to/files.tar

# Install apps on the site
bench --site staging.comfac.com install-app erpnext
bench --site staging.comfac.com install-app payments
bench --site staging.comfac.com install-app webshop
```

### Option C: Docker-based Staging

```bash
# Use frappe_docker for isolated environment
git clone https://github.com/frappe/frappe_docker.git
cd frappe_docker

# Configure with custom webshop repo in apps.json
# Build and restore production backup
```

---

## Step 3: Replace Webshop with Our Fork

If the staging site already has the official webshop installed:

```bash
# Navigate to the webshop app directory
cd ~/frappe-bench/apps/webshop

# Add our fork as a remote
git remote add comfac https://github.com/xunema/comfac-webshop.git
git fetch comfac

# Check current branch and status
git status
git log --oneline -5

# Switch to our fork's branch
git checkout comfac/main

# Run migrations in case there are schema changes
bench --site staging.comfac.com migrate

# Rebuild frontend assets
bench build --app webshop

# Restart
bench restart
```

If installing fresh (no existing webshop):
```bash
bench get-app webshop https://github.com/xunema/comfac-webshop.git
bench --site staging.comfac.com install-app webshop
bench --site staging.comfac.com migrate
bench build --app webshop
bench restart
```

---

## Step 4: Validate Seamless Replacement

### Automated Checks
```bash
# Run the webshop's built-in tests
bench --site staging.comfac.com run-tests --app webshop

# Check for migration issues
bench --site staging.comfac.com migrate --dry-run

# Check for JS build errors
bench build --app webshop 2>&1 | tee build.log
```

### Manual Validation Checklist

| Area | Test | Expected |
|------|------|----------|
| Homepage | Load / with webshop products | Products display, hero slider works |
| /all-products | Browse, filter, search | Products list, filters work, pagination works |
| /shop-by-category | Category cards render | Categories show with images |
| Product page | View item with variants | Variant selector works, price shown |
| Add to Cart | Add item, check cart count | Cart updates, cookie set |
| /cart | View cart page | Items shown with correct prices, qty editable |
| Qty change | Increase/decrease qty | Total recalculates, page updates via AJAX |
| Remove item | Click X on item | Item removed, totals recalculate |
| Coupon code | Apply valid coupon | Price recalculates (even if savings not yet shown) |
| Address | Select/add address | Address saved, taxes recalculate |
| Place Order | Complete checkout | Sales Order created, redirect to order page |
| /orders | View past orders | Orders listed with correct details |
| Wishlist | Add/remove items | Wishlist updates |
| Guest access | Browse as guest | Products visible, prices per settings |
| Mobile | Test on mobile viewport | Responsive layout works |

### Troubleshooting Common Issues

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| 500 error on /cart | Missing Webshop Settings | Configure Webshop Settings in desk |
| Missing product images | Files not restored | Re-restore with `--with-public-files` |
| JS errors in console | Asset build needed | `bench build --app webshop` |
| "Price List not found" | Settings mismatch | Set correct Price List in Webshop Settings |
| Migration errors | Schema differences | Check `patches.txt`, run `bench migrate` |
| Redis errors | Cache issues | `bench clear-cache && bench clear-website-cache` |
| Blank product pages | Website Items not created | Run `bench execute webshop.patches.create_website_items.execute` |

---

## Step 5: Set Up Sample Test Data

### Sample Products
Create a mix of product types to test all features:

1. **Simple Items** (no variants) - e.g., "USB Cable", "Mouse Pad"
2. **Variant Items** - e.g., "T-Shirt" with Color + Size variants
3. **Service Items** (non-stock) - e.g., "Installation Service"
4. **Bundle Items** - e.g., "Starter Kit" (for future System Builder)

### Sample Pricing Rules & Promotions

1. **Percentage Discount** - "20% off all RAM modules"
   - Pricing Rule: discount_percentage=20, item_group="RAM"
2. **Fixed Amount Discount** - "$50 off orders over $500"
   - Pricing Rule: discount_amount=50, min_amount=500
3. **Free Item** - "Buy 2 SSDs, get 1 free"
   - Pricing Rule: type=Product, min_qty=2, free_item=SSD
4. **Coupon Code** - "WELCOME10" for 10% off
   - Coupon Code linked to Pricing Rule
5. **Time-Limited Offer** - "Flash Sale: 30% off GPUs until March 1"
   - Pricing Rule with valid_from/valid_upto dates

### Validating Discounts End-to-End
For each promotion:
1. Add qualifying items to cart
2. Check Quotation in desk - verify discount fields populated
3. Check cart UI - note what IS and ISN'T visible
4. This becomes the baseline for building discount visibility features

---

## Step 6: Iteration Cycle

```
1. Make code changes in comfac-webshop fork
2. Push to GitHub
3. On staging: git pull && bench build --app webshop && bench restart
4. Test the specific feature
5. Run full validation checklist
6. If issues found -> fix, repeat
7. When stable -> tag release, plan production deployment
```

### Git Workflow
```bash
# Development branch for discount features
git checkout -b feature/cart-discount-display

# Development branch for system builder
git checkout -b feature/system-builder

# Merge to main when validated
git checkout main
git merge feature/cart-discount-display
```

---

## Step 7: Production Deployment (when ready)

```bash
# On production
bench --site your-site.com backup --with-files

# Switch to fork
cd ~/frappe-bench/apps/webshop
git remote add comfac https://github.com/xunema/comfac-webshop.git
git fetch comfac
git checkout comfac/main

# Migrate and build
bench --site your-site.com migrate
bench build --app webshop
bench restart

# Verify
bench --site your-site.com run-tests --app webshop
```

Rollback plan:
```bash
# If issues arise, revert to original webshop
git checkout origin/main  # or whatever the original branch was
bench --site your-site.com migrate
bench build --app webshop
bench restart
```

---

## Related Wiki Pages

- [14 - Hypothesis: Discount & Deadline Visibility](14-Hypothesis-Discount-Deadline-Visibility.md) - Phase 0 must pass before implementing the hypothesis on a Phase 1 clone
- [10 - Feature Gap: Cart Discounts](10-Feature-Gap-Cart-Discounts.md) - The first feature to implement after seamless replacement
- [01 - Architecture Overview](01-Architecture-Overview.md) - Understanding the app structure before deployment
- [09 - Hooks & Events](09-Hooks-and-Events.md) - Migration-related hooks to watch for
- [Back to Home](00-Home.md)
