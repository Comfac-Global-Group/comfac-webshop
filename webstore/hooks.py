from . import __version__ as _version

app_name = "webstore"
app_title = "Webstore"
app_publisher = "Comfac Global Group (cws fork)"
app_description = "Comfac WebStore — eCommerce platform (fork of Frappe WebShop)"
app_email = "contact@comfac-it.com"
app_license = "GNU General Public License (v3)"
app_version = _version

required_apps = ["erpnext"]  # payments removed for standalone cws deploy

web_include_css = "webstore-web.bundle.css"

# Bundle path: dist/ has the hashed files. Source files at public/js/ are fallback.
# The asset.json on the bench maps web.bundle.js -> /assets/webstore/dist/js/web.bundle.WLOGYSZO.js
web_include_js = "web.bundle.js"

# Additional source files not included in the bundle (if asset.json resolution fails)
# web_include_js can also be a list — revert to this if bundle 404 persists:
# web_include_js = [
#     "webstore/js/init.js",
#     "webstore/js/shopping_cart.js",
#     "webstore/js/wishlist.js",
#     "webstore/js/customer_reviews.js",
# ]

after_install = "webstore.setup.install.after_install"
on_logout = "webstore.webstore.shopping_cart.utils.clear_cart_count"
on_session_creation = [
    "webstore.webstore.utils.portal.update_debtors_account",
    "webstore.webstore.shopping_cart.utils.set_cart_count",
]
update_website_context = [
    "webstore.webstore.shopping_cart.utils.update_website_context",
]

website_generators = ["Website Item", "Item Group"]

override_doctype_class = {
    "Payment Request": "webstore.webstore.doctype.override_doctype.payment_request.PaymentRequest",
    "Item Group": "webstore.webstore.doctype.override_doctype.item_group.WebstoreItemGroup",
    "Item": "webstore.webstore.doctype.override_doctype.item.WebstoreItem",
}

doctype_js = {
    "Item": "public/js/override/item.js",
    "Homepage": "public/js/override/homepage.js",
}

doc_events = {
    "Item": {
        "on_update": [
            "webstore.webstore.crud_events.item.update_website_item.execute",
            "webstore.webstore.crud_events.item.invalidate_item_variants_cache.execute",
        ],
        "before_rename": [
            "webstore.webstore.crud_events.item.validate_duplicate_website_item.execute",
        ],
        "after_rename": [
            "webstore.webstore.crud_events.item.invalidate_item_variants_cache.execute",
        ],
    },
    "Sales Taxes and Charges Template": {
        "on_update": [
            "webstore.webstore.doctype.webshop_settings.webshop_settings.validate_cart_settings",
        ],
    },
    "Quotation": {
        "validate": [
            "webstore.webstore.crud_events.quotation.validate_shopping_cart_items.execute",
        ],
    },
    "Price List": {
        "validate": [
            "webstore.webstore.crud_events.price_list.check_impact_on_cart.execute"
        ],
    },
    "Tax Rule": {
        "validate": [
            "webstore.webstore.crud_events.tax_rule.validate_use_for_cart.execute",
        ],
    },
}

has_website_permission = {
    "Website Item": "webstore.webstore.doctype.website_item.website_item.has_website_permission_for_website_item",
    "Item Group": "webstore.webstore.doctype.website_item.website_item.has_website_permission_for_item_group",
}
