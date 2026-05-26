# Comfac WebStore

**A turnkey eCommerce fork of [Frappe WebShop](https://github.com/frappe/webshop), customized and extended by Comfac Global Group.**

Comfac WebStore is built on top of Frappe WebShop — an open-source eCommerce platform developed by Frappe Technologies as part of the Frappe framework. We credit and thank the Frappe team for the solid foundation.

This fork diverges from upstream to provide Comfac-specific customizations (discount visibility, cart UI enhancements, checkout flow improvements) and will evolve into a turnkey eCommerce solution with add-ons tailored for our use cases.

> **Upstream:** [github.com/frappe/webshop](https://github.com/frappe/webshop)  
> **License:** GNU General Public License v3 (same as upstream)

---

## What's Different from Frappe WebShop?

| Feature | Frappe WebShop | Comfac WebStore |
|---------|---------------|-----------------|
| **Upstream sync** | ✅ Active | ❌ Independent fork |
| **Discount display** | Basic | Enhanced (strikethrough, badge, savings summary) |
| **Cart UI** | Standard | Custom cart totals & payment summary |
| **Payment integration** | `payments` app required | Standalone (`erpnext` only) |
| **Roadmap** | Frappe-led | Comfac-led turnkey add-ons |

---

## Table of Contents

- [Setup](#setup)
  - [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

---

## Setup

### Prerequisites

- Frappe Bench ([installation guide](https://github.com/frappe/bench))
- ERPNext installed on your site

### Installation

```bash
# 1. Get the app
bench get-app webstore https://github.com/Comfac-Global-Group/comfac-webshop-private.git

# 2. Install on your site
bench --site sitename install-app webstore

# 3. Build assets
bench build
```

> **Frappe Cloud users:** Deploy via the Frappe Cloud dashboard using the `github-private` remote.

---

## Usage

After installation, configure **Webshop Settings** (DocType name retained from upstream) in ERPNext:

1. Go to **Webshop Settings** in the ERPNext search bar
2. Set your company, price list, and default customer group
3. Publish items as **Website Items** to make them visible on the store
4. Visit `/all-products` to browse the storefront

For detailed setup instructions, see the [Frappe WebShop documentation](https://docs.erpnext.com/docs/user/manual/en/set_up_e_commerce).

---

## Contributing

This is a **private fork** maintained by Comfac Global Group. We do not accept external pull requests.

For the upstream project, contributions are welcome at [github.com/frappe/webshop](https://github.com/frappe/webshop).

---

## License

Licensed under the **GNU General Public License v3**.  
See [LICENSE](LICENSE) for details.  
Original work copyright © Frappe Technologies Pvt. Ltd.  
Modifications copyright © Comfac Global Group.
