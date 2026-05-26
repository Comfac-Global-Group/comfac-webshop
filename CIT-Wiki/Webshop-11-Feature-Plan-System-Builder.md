# 11 - Feature Plan: System Builder

**Parent:** [Webshop Index](Webshop-Index)  
**Previous:** [10 - Feature Gap: Cart Discounts](Webshop-10-Feature-Gap-Cart-Discounts)  
**Next:** [12 - Staging Sandbox Deployment](Webshop-12-Staging-Sandbox-Deployment)  
**Source:** [Comfac Webstore Wiki - Chapter 11](https://github.com/Comfac-Global-Group/comfac-webstore/wiki/11-Feature-Plan-System-Builder)

**Status:** 🔴 Not Implemented | **Priority:** High

---

## Vision

A configurable product builder where customers can assemble multi-component systems (servers, desktops, maker kits, open-source hardware platforms) from a template of compatible components, with real-time pricing, compatibility enforcement, and the ability to save/load configurations.

## Use Cases

1. **Server Builder** - Customer selects: chassis, CPU, RAM (qty/type), storage (multiple drives), NIC, PSU, OS
2. **Desktop Builder** - Case, motherboard, CPU, GPU, RAM, storage, PSU, peripherals
3. **Maker Kit Builder** - Board (RPi, Arduino, etc.), sensors, actuators, enclosure, power supply
4. **Future platforms** - Any multi-component configurable product

## New DocTypes Needed

### System Builder Template

- Name, description, image
- Category (Server, Desktop, Maker Kit, etc.)
- Child table: **Component Slots**
  - Slot name (e.g., "CPU", "RAM", "Storage Bay 1")
  - Required (yes/no)
  - Min/Max quantity
  - Allowed Item Group or explicit item list
  - Default selection (if any)

### Compatibility Rule

- Rule name
- Rule type: "Requires", "Excludes", "Max Qty", "Min Qty"
- Source slot + attribute/item filter
- Target slot + attribute/item filter
- Error message

### Saved Configuration

- User (Customer)
- Template reference
- Name (user-defined)
- Child table: selected items per slot
- Total price, status (draft/shared/ordered)

## Integration with Existing Variant System

Each component slot can reference:

- An **Item Group** (e.g., "DDR5 RAM")
- A **Template Item** (using variant attributes for selection)
- Specific **Item** codes

The existing `variant_selector/utils.py` logic for filtering valid combinations can be reused within each slot.

## Compatibility Engine

```
For each user selection:
  1. Check all Compatibility Rules
  2. Filter available options in other slots
  3. Return: valid_options, warnings, errors

Example rules:
  - CPU Socket LGA1700 REQUIRES Motherboard Socket LGA1700
  - RAM Type DDR5 EXCLUDES Motherboard Type DDR4
  - Total PSU Load <= PSU Wattage
  - Max 4 RAM sticks if Motherboard RAM Slots = 4
```

## Pricing

- Each component priced individually from Price List
- Bundle Pricing Rules can apply (e.g., "10% off complete system")
- Show per-component price + total system price
- Discounts visible per-component and total savings

## Cart Integration

When "Add System to Cart":

- Create a **Product Bundle** or **Packed Item** approach
- Add all components as Quotation Items, linked as a group
- Or: create a single "System" line item with packed items detail

## UI Flow

```
1. Choose Template (e.g., "1U Rack Server")
2. For each slot:
   - Browse/filter compatible components
   - See price, availability, specs
   - Select and configure (qty, variant attributes)
3. Real-time:
   - Compatibility checks
   - Running total
   - Power budget / capacity warnings
4. Save Configuration (optional)
5. Add to Cart
```

## Implementation Phases

### Phase 1: Foundation

- Create System Builder Template DocType
- Create Component Slot child table
- Basic UI: template selection, slot browsing
- Simple "add all to cart" (no compatibility engine yet)

### Phase 2: Compatibility

- Create Compatibility Rule DocType
- Build rule evaluation engine
- Real-time filtering of valid options
- Warning/error display

### Phase 3: Save & Share

- Saved Configuration DocType
- User dashboard for saved configs
- Share via URL
- Load/clone/modify

### Phase 4: Advanced

- Power/thermal budget calculation
- AI-assisted recommendations
- Preset "popular configurations"
- Comparison between configurations
- Integration with BOM for manufacturing

## Technical Challenges

1. **Performance**: Evaluating compatibility across many items/rules in real-time
2. **Attribute mapping**: Different items have different attributes; need a normalized way to express compatibility
3. **Cart representation**: How to group system components in a Quotation
4. **Pricing complexity**: Component discounts + bundle discounts + system-level pricing rules
5. **Stock**: All components must be available simultaneously

---

**Navigation:** [Webshop Index](Webshop-Index) | [Previous: 10 - Cart Discounts](Webshop-10-Feature-Gap-Cart-Discounts) | [Next: 12 - Staging Sandbox](Webshop-12-Staging-Sandbox-Deployment)
