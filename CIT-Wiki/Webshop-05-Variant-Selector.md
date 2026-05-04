# 05 - Variant Selector

**Parent:** [Webshop Index](Webshop-Index)  
**Previous:** [04 - Product Pages & Browsing](Webshop-04-Product-Pages-and-Browsing)  
**Next:** [06 - Pricing & Discounts](Webshop-06-Pricing-and-Discounts)  
**Source:** [Comfac Webshop Wiki - Chapter 05](https://github.com/Comfac-Global-Group/comfac-webshop/wiki/05-Variant-Selector)

---

## How Variants Work in ERPNext + Webshop

ERPNext has a built-in **Item Variant** system:

- **Template Item**: defines attributes (e.g., Color, Size, RAM, Storage)
- **Variant Items**: concrete products with specific attribute values (e.g., "Laptop - 16GB RAM - 512GB SSD")

The webshop uses this to create a step-by-step configurator on product pages.

## Key Files

- `webshop/variant_selector/utils.py` - Core variant logic
- `webshop/variant_selector/item_variants_cache.py` - Redis caching layer
- `templates/generators/item/item_configure.html` - Configurator UI
- `templates/generators/item/item_configure.js` - Configurator JS

## Variant Selection Flow

1. User visits a Template Item page (has_variants=True)
2. `item_configure.html` renders attribute dropdowns
3. `item_configure.js` calls `get_next_attribute_and_values` API on each selection
4. Backend filters valid combinations, returns:
   - `next_attribute` - which attribute to select next
   - `valid_options_for_attributes` - valid values given current selections
   - `filtered_items_count` - how many variants match
   - `exact_match` - if one variant is fully selected
   - `product_info` - price for the matched variant
   - `available_qty` - stock quantity
5. When exact match found, "Add to Cart" button appears with variant item_code

## Cache System (`ItemVariantsCacheManager`)

Uses Redis to cache:

- `item_variants_data` - all variant attribute values
- `item_attribute_value_map` - attribute -> variant mapping
- `optional_attributes` - which attributes are optional

Cache is invalidated on Item save/rename via crud_events hooks.

## API Endpoints

### `get_attributes_and_values(item_code)`

Returns all attributes and their possible values for a template item.

### `get_next_attribute_and_values(item_code, selected_attributes)`

Progressive filtering - returns valid options given current selections.

### `get_item_variant_price_dict(item_code, cart_settings)`

Gets price for a specific variant item.

## Relevance to System Builder

The existing variant selector is a **single-item configurator**. The planned System Builder would need:

- **Multi-item configuration** (CPU + RAM + Storage + etc.)
- **Cross-item compatibility rules** (not just attribute filtering within one template)
- **Template/preset system** (save configurations)
- **Aggregated pricing** (total system price with combined discounts)

The variant_selector's caching and attribute filtering logic could be extended, but the System Builder is fundamentally a different scope.

---

**See Also:** [Feature Plan: System Builder](Webshop-11-Feature-Plan-System-Builder)

**Navigation:** [Webshop Index](Webshop-Index) | [Previous: 04 - Product Pages](Webshop-04-Product-Pages-and-Browsing) | [Next: 06 - Pricing & Discounts](Webshop-06-Pricing-and-Discounts)
