import os
import re


def markdown_to_wikitext(md_content, chapter_num):
    """Convert Markdown to MediaWiki wikitext format"""

    wt = md_content

    # Convert headers: # to =
    wt = re.sub(r"^# (.*?)$", r"= \1 =", wt, flags=re.MULTILINE)
    wt = re.sub(r"^## (.*?)$", r"== \1 ==", wt, flags=re.MULTILINE)
    wt = re.sub(r"^### (.*?)$", r"=== \1 ===", wt, flags=re.MULTILINE)

    # Convert bold: **text** to '''text'''
    wt = re.sub(r"\*\*(.*?)\*\*", r"'''\1'''", wt)

    # Convert italic: *text* to ''text'' (but not already converted bold)
    # Handle carefully to avoid double-converting
    wt = re.sub(r"(?<!\')\*(.*?)\*(?!\')", r"''\1''", wt)

    # Convert code blocks
    wt = wt.replace("```", "<pre>")

    # Convert inline code: `text` to <code>text</code>
    wt = re.sub(r"`(.*?)`", r"<code>\1</code>", wt)

    # Convert links [text](url) to [url text]
    wt = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"[\2 \1]", wt)

    # Convert horizontal rules
    wt = wt.replace("---", "----")

    # Update navigation links
    wt = wt.replace(
        "[Webshop Index](Webshop-Index)", "[[Frappe ERPNext/Webshop|Webshop Index]]"
    )
    wt = wt.replace(
        "(Webshop-01-Architecture-Overview)",
        "(Frappe ERPNext/Webshop/01-Architecture-Overview)",
    )
    wt = wt.replace("(Webshop-02-DocTypes)", "(Frappe ERPNext/Webshop/02-DocTypes)")
    wt = wt.replace(
        "(Webshop-03-Shopping-Cart-Quotation-Deep-Dive)",
        "(Frappe ERPNext/Webshop/03-Shopping-Cart-Quotation-Deep-Dive)",
    )
    wt = wt.replace(
        "(Webshop-04-Product-Pages-and-Browsing)",
        "(Frappe ERPNext/Webshop/04-Product-Pages-and-Browsing)",
    )
    wt = wt.replace(
        "(Webshop-05-Variant-Selector)", "(Frappe ERPNext/Webshop/05-Variant-Selector)"
    )
    wt = wt.replace(
        "(Webshop-06-Pricing-and-Discounts)",
        "(Frappe ERPNext/Webshop/06-Pricing-and-Discounts)",
    )
    wt = wt.replace(
        "(Webshop-07-Checkout-and-Orders)",
        "(Frappe ERPNext/Webshop/07-Checkout-and-Orders)",
    )
    wt = wt.replace(
        "(Webshop-08-Templates-and-Frontend)",
        "(Frappe ERPNext/Webshop/08-Templates-and-Frontend)",
    )
    wt = wt.replace(
        "(Webshop-09-Hooks-and-Events)", "(Frappe ERPNext/Webshop/09-Hooks-and-Events)"
    )
    wt = wt.replace(
        "(Webshop-10-Feature-Gap-Cart-Discounts)",
        "(Frappe ERPNext/Webshop/10-Feature-Gap-Cart-Discounts)",
    )
    wt = wt.replace(
        "(Webshop-11-Feature-Plan-System-Builder)",
        "(Frappe ERPNext/Webshop/11-Feature-Plan-System-Builder)",
    )
    wt = wt.replace(
        "(Webshop-12-Staging-Sandbox-Deployment)",
        "(Frappe ERPNext/Webshop/12-Staging-Sandbox-Deployment)",
    )
    wt = wt.replace(
        "(Webshop-13-Discount-Visibility-and-Urgency)",
        "(Frappe ERPNext/Webshop/13-Discount-Visibility-and-Urgency)",
    )
    wt = wt.replace(
        "(Webshop-14-Hypothesis-Discount-Deadline-Visibility)",
        "(Frappe ERPNext/Webshop/14-Hypothesis-Discount-Deadline-Visibility)",
    )

    # Convert tables (Markdown | to MediaWiki {| | |})
    # Simple table conversion
    lines = wt.split("\n")
    in_table = False
    new_lines = []

    for line in lines:
        if line.startswith("| ") and "|" in line[2:]:
            if not in_table:
                new_lines.append('{| class="wikitable"')
                in_table = True
            # Convert markdown table row to wikitable row
            cells = [cell.strip() for cell in line.split("|")[1:-1]]
            new_lines.append("|-")
            for cell in cells:
                new_lines.append(f"| {cell}")
        else:
            if in_table:
                new_lines.append("|}")
                in_table = False
            new_lines.append(line)

    if in_table:
        new_lines.append("|}")

    wt = "\n".join(new_lines)

    # Remove duplicate wikitable headers
    wt = re.sub(
        r"\{\| class=\"wikitable\"\n\|-\n\| ----", '{| class="wikitable"\n|-', wt
    )

    return wt


# List of all chapters
chapters = [
    ("01-Architecture-Overview.md", "01-Architecture-Overview.txt"),
    ("02-DocTypes.md", "02-DocTypes.txt"),
    (
        "03-Shopping-Cart-Quotation-Deep-Dive.md",
        "03-Shopping-Cart-Quotation-Deep-Dive.txt",
    ),
    ("04-Product-Pages-and-Browsing.md", "04-Product-Pages-and-Browsing.txt"),
    ("05-Variant-Selector.md", "05-Variant-Selector.txt"),
    ("06-Pricing-and-Discounts.md", "06-Pricing-and-Discounts.txt"),
    ("07-Checkout-and-Orders.md", "07-Checkout-and-Orders.txt"),
    ("08-Templates-and-Frontend.md", "08-Templates-and-Frontend.txt"),
    ("09-Hooks-and-Events.md", "09-Hooks-and-Events.txt"),
    ("10-Feature-Gap-Cart-Discounts.md", "10-Feature-Gap-Cart-Discounts.txt"),
    ("11-Feature-Plan-System-Builder.md", "11-Feature-Plan-System-Builder.txt"),
    ("12-Staging-Sandbox-Deployment.md", "12-Staging-Sandbox-Deployment.txt"),
    ("13-Discount-Visibility-and-Urgency.md", "13-Discount-Visibility-and-Urgency.txt"),
    (
        "14-Hypothesis-Discount-Deadline-Visibility.md",
        "14-Hypothesis-Discount-Deadline-Visibility.txt",
    ),
]

source_dir = "/home/justin/opencode260220/comfac-webshop/CIT-Wiki/"
output_dir = "/home/justin/opencode260220/comfac-webshop/wikitext-upload/"

success_count = 0

for md_file, txt_file in chapters:
    source_path = os.path.join(source_dir, f"Webshop-{md_file}")
    output_path = os.path.join(output_dir, txt_file)

    if not os.path.exists(source_path):
        print(f"❌ Source file not found: {source_path}")
        continue

    # Read markdown
    with open(source_path, "r") as f:
        md_content = f.read()

    # Convert
    wt_content = markdown_to_wikitext(md_content, md_file[:2])

    # Write wikitext
    with open(output_path, "w") as f:
        f.write(wt_content)

    print(f"✅ Created: {txt_file} ({len(wt_content)} chars)")
    success_count += 1

print(f"\n=== COMPLETED ===")
print(f"Successfully converted: {success_count}/{len(chapters)} files")
print(f"Output directory: {output_dir}")
