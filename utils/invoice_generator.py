import fitz  # PyMuPDF
import random
import os
from faker import Faker
from datetime import datetime, timedelta

# Initialise Faker
fake = Faker()

# Output directory
OUTPUT_DIR = "data/invoices"

OUR_COMPANY = {
    "name": "Horizon Financial Services Ltd",
    "address": "Level 15, DIFC, Dubai, UAE"
}

# Make sure the output folder exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

VENDORS = [
    {
        "name": "TechCorp Solutions",
        "address": "123 Silicon Valley Blvd, San Francisco, CA 94025, USA",
        "currency": "USD",
        "currency_symbol": "$",
        "tax_label": "Tax",
        "tax_rate": 0.10,
        "has_po_number": True,
        "style": "modern"
    },
    {
        "name": "Al Fardan Trading LLC",
        "address": "Office 401, Al Fardan Tower, Sheikh Zayed Road, Dubai, UAE",
        "currency": "AED",
        "currency_symbol": "AED ",
        "tax_label": "VAT",
        "tax_rate": 0.05,
        "has_po_number": False,
        "style": "arabic"
    },
    {
        "name": "EuroSupply GmbH",
        "address": "Industriestrasse 47, 80339 München, Germany",
        "currency": "EUR",
        "currency_symbol": "€",
        "tax_label": "MwSt",
        "tax_rate": 0.19,
        "has_po_number": True,
        "style": "european"
    },
    {
        "name": "Sharma & Associates",
        "address": "B-204, Nehru Place Commercial Complex, New Delhi, 110019, India",
        "currency": "INR",
        "currency_symbol": "₹",
        "tax_label": "GST",
        "tax_rate": 0.18,
        "has_po_number": False,
        "style": "indian"
    },
    {
        "name": "FastFreight Ltd",
        "address": "Unit 7, Logistics Park, Heathrow, London, TW6 2GE, UK",
        "currency": "USD",
        "currency_symbol": "$",
        "tax_label": "Tax",
        "tax_rate": 0.08,
        "has_po_number": True,
        "style": "logistics"
    }
]


PRODUCTS = [
    "Software License Fee",
    "Cloud Infrastructure Services",
    "IT Consulting Hours",
    "Network Equipment Supply",
    "Data Storage Solutions",
    "Cybersecurity Audit",
    "API Integration Services",
    "Technical Support Package",
    "Hardware Maintenance",
    "Project Management Fee",
    "Freight Forwarding Charges",
    "Customs Clearance Fee",
    "Warehouse Storage",
    "Last Mile Delivery",
    "Insurance Premium"
]

def generate_line_items(num_items, currency_symbol):
    """Generate realistic invoice line items"""
    items = []
    for _ in range(num_items):
        quantity = random.randint(1, 20)
        unit_price_raw = random.uniform(50, 5000)
        unit_price_display = round(unit_price_raw, 2)
        total = round(quantity * unit_price_raw, 2)  # Raw price for accuracy
        
        items.append({
            "description": random.choice(PRODUCTS),
            "quantity": quantity,
            "unit_price": unit_price_display,  # Display rounded price
            "total": total  # Total calculated from raw price
        })
    
    return items


def calculate_totals(line_items, tax_rate, inject_error=False):
    """Calculate invoice totals with optional error injection"""
    
    subtotal = round(sum(item["total"] for item in line_items), 2)
    
    if inject_error:
        error_type = random.choice([
            "wrong_tax",
            "wrong_total",
            "inflated_line_item"
        ])
        
        if error_type == "wrong_tax":
            # Apply wrong tax rate deliberately
            tax_amount = round(subtotal * (tax_rate * 2), 2)
            error_description = "Tax calculated at double the correct rate"
            
        elif error_type == "wrong_total":
            # Calculate correct tax but corrupt the grand total
            tax_amount = round(subtotal * tax_rate, 2)
            error_description = "Grand total does not match subtotal plus tax"
            
        elif error_type == "inflated_line_item":
            # Correct tax but secretly inflate one line item total
            tax_amount = round(subtotal * tax_rate, 2)
            line_items[-1]["total"] = round(line_items[-1]["total"] * 1.5, 2)
            error_description = "Last line item total inflated by 50 percent"
        
        grand_total = round(subtotal + tax_amount, 2)
        
        if error_type == "wrong_total":
            grand_total = round(grand_total * 1.1, 2)
            
        return subtotal, tax_amount, grand_total, error_description
    
    else:
        tax_amount = round(subtotal * tax_rate, 2)
        grand_total = round(subtotal + tax_amount, 2)
        return subtotal, tax_amount, grand_total, None
    

def generate_invoice_pdf(vendor, invoice_number, inject_error=False):
    """Generate a single invoice PDF with vendor-specific layout"""

    # Generate invoice data
    invoice_date = fake.date_between(start_date="-90d", end_date="today")
    due_date = invoice_date + timedelta(days=random.choice([15, 30, 45, 60]))
    num_items = random.randint(3, 8)

    # Generate line items and totals
    line_items = generate_line_items(num_items, vendor["currency_symbol"])
    subtotal, tax_amount, grand_total, error_description = calculate_totals(
        line_items, vendor["tax_rate"], inject_error
    )

    # Create PDF
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    style = vendor["style"]

    # ── MODERN LAYOUT (TechCorp) ──
    if style == "modern":
        y = 50
        page.insert_text((50, y), vendor["name"], fontsize=18, fontname="helv")
        page.insert_text((400, y), "INVOICE", fontsize=18, fontname="helv")
        y += 20
        page.insert_text((50, y), vendor["address"], fontsize=8, fontname="helv")
        y += 15
        page.draw_line((50, y), (545, y))
        y += 15

        page.insert_text((50, y), f"Invoice #: {invoice_number}", fontsize=10, fontname="helv")
        page.insert_text((350, y), f"Date: {invoice_date.strftime('%B %d, %Y')}", fontsize=10, fontname="helv")
        y += 15
        if vendor["has_po_number"]:
            po_number = f"PO-{random.randint(10000, 99999)}"
            page.insert_text((50, y), f"PO Number: {po_number}", fontsize=10, fontname="helv")
        page.insert_text((350, y), f"Due: {due_date.strftime('%B %d, %Y')}", fontsize=10, fontname="helv")
        y += 25

        page.insert_text((50, y), "Bill To:", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((50, y), OUR_COMPANY["name"], fontsize=10, fontname="helv")
        y += 13
        page.insert_text((50, y), OUR_COMPANY["address"], fontsize=9, fontname="helv")
        y += 25

        page.insert_text((50, y), "Description", fontsize=10, fontname="helv")
        page.insert_text((280, y), "Qty", fontsize=10, fontname="helv")
        page.insert_text((340, y), "Unit Price", fontsize=10, fontname="helv")
        page.insert_text((460, y), "Amount", fontsize=10, fontname="helv")
        y += 5
        page.draw_line((50, y), (545, y))
        y += 12

        for item in line_items:
            page.insert_text((50, y), item["description"][:35], fontsize=9, fontname="helv")
            page.insert_text((280, y), str(item["quantity"]), fontsize=9, fontname="helv")
            page.insert_text((340, y), f"{vendor['currency_symbol']}{item['unit_price']:,.2f}", fontsize=9, fontname="helv")
            page.insert_text((460, y), f"{vendor['currency_symbol']}{item['total']:,.2f}", fontsize=9, fontname="helv")
            y += 15

        page.draw_line((50, y), (545, y))
        y += 15
        page.insert_text((350, y), f"Subtotal: {vendor['currency_symbol']}{subtotal:,.2f}", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((350, y), f"{vendor['tax_label']} ({int(vendor['tax_rate']*100)}%): {vendor['currency_symbol']}{tax_amount:,.2f}", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((350, y), f"TOTAL DUE: {vendor['currency_symbol']}{grand_total:,.2f}", fontsize=12, fontname="helv")
        y += 30
        page.insert_text((50, y), "Payment due within 30 days. Please include invoice number on payment.", fontsize=8, fontname="helv")

    # ── ARABIC LAYOUT (Al Fardan) ──
    elif style == "arabic":
        y = 50
        page.insert_text((50, y), "TAX INVOICE", fontsize=16, fontname="helv")
        y += 25
        page.insert_text((50, y), vendor["name"], fontsize=14, fontname="helv")
        y += 18
        page.insert_text((50, y), vendor["address"], fontsize=9, fontname="helv")
        y += 15
        vat_number = f"VAT-{random.randint(100000000000000, 999999999999999)}"
        page.insert_text((50, y), f"VAT Registration No: {vat_number}", fontsize=9, fontname="helv")
        y += 25

        page.draw_line((50, y), (545, y))
        y += 15

        page.insert_text((50, y), f"Invoice No:", fontsize=10, fontname="helv")
        page.insert_text((200, y), invoice_number, fontsize=10, fontname="helv")
        page.insert_text((350, y), f"Invoice Date:", fontsize=10, fontname="helv")
        page.insert_text((450, y), invoice_date.strftime('%d/%m/%Y'), fontsize=10, fontname="helv")
        y += 15
        page.insert_text((350, y), f"Due Date:", fontsize=10, fontname="helv")
        page.insert_text((450, y), due_date.strftime('%d/%m/%Y'), fontsize=10, fontname="helv")
        y += 25

        page.insert_text((50, y), "Invoice To:", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((50, y), OUR_COMPANY["name"], fontsize=10, fontname="helv")
        y += 13
        page.insert_text((50, y), OUR_COMPANY["address"], fontsize=9, fontname="helv")
        y += 25

        page.insert_text((50, y), "Description of Services", fontsize=10, fontname="helv")
        page.insert_text((300, y), "Qty", fontsize=10, fontname="helv")
        page.insert_text((360, y), "Unit Rate", fontsize=10, fontname="helv")
        page.insert_text((460, y), "Amount", fontsize=10, fontname="helv")
        y += 5
        page.draw_line((50, y), (545, y))
        y += 12

        for item in line_items:
            page.insert_text((50, y), item["description"][:35], fontsize=9, fontname="helv")
            page.insert_text((300, y), str(item["quantity"]), fontsize=9, fontname="helv")
            page.insert_text((360, y), f"{vendor['currency_symbol']} {item['unit_price']:,.2f}", fontsize=9, fontname="helv")
            page.insert_text((460, y), f"{vendor['currency_symbol']} {item['total']:,.2f}", fontsize=9, fontname="helv")
            y += 15

        page.draw_line((50, y), (545, y))
        y += 15
        page.insert_text((350, y), f"Amount (excl. VAT):", fontsize=10, fontname="helv")
        page.insert_text((460, y), f"{vendor['currency_symbol']} {subtotal:,.2f}", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((350, y), f"VAT @ {int(vendor['tax_rate']*100)}%:", fontsize=10, fontname="helv")
        page.insert_text((460, y), f"{vendor['currency_symbol']} {tax_amount:,.2f}", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((350, y), f"Total Amount Due:", fontsize=11, fontname="helv")
        page.insert_text((460, y), f"{vendor['currency_symbol']} {grand_total:,.2f}", fontsize=11, fontname="helv")
        y += 30
        page.insert_text((50, y), "This is a computer generated invoice.", fontsize=8, fontname="helv")

    # ── EUROPEAN LAYOUT (EuroSupply GmbH) ──
    elif style == "european":
        y = 50
        page.insert_text((50, y), vendor["name"], fontsize=16, fontname="helv")
        y += 20
        page.insert_text((50, y), vendor["address"], fontsize=9, fontname="helv")
        y += 15
        iban = f"DE{random.randint(10,99)} {random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(10,99)}"
        page.insert_text((50, y), f"IBAN: {iban}", fontsize=9, fontname="helv")
        y += 13
        page.insert_text((50, y), f"USt-IdNr: DE{random.randint(100000000, 999999999)}", fontsize=9, fontname="helv")
        y += 30

        page.insert_text((50, y), "Rechnung", fontsize=18, fontname="helv")
        y += 5
        page.insert_text((50, y), "(Invoice)", fontsize=10, fontname="helv")
        y += 25

        page.insert_text((50, y), f"Rechnungsnummer: {invoice_number}", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((50, y), f"Rechnungsdatum: {invoice_date.strftime('%d.%m.%Y')}", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((50, y), f"Faelligkeitsdatum: {due_date.strftime('%d.%m.%Y')}", fontsize=10, fontname="helv")
        y += 25

        page.insert_text((50, y), "Rechnungsempfaenger (Bill To):", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((50, y), OUR_COMPANY["name"], fontsize=10, fontname="helv")
        y += 13
        page.insert_text((50, y), OUR_COMPANY["address"], fontsize=9, fontname="helv")
        y += 25

        page.insert_text((50, y), "Pos.", fontsize=10, fontname="helv")
        page.insert_text((90, y), "Beschreibung", fontsize=10, fontname="helv")
        page.insert_text((280, y), "Menge", fontsize=10, fontname="helv")
        page.insert_text((340, y), "Einzelpreis", fontsize=10, fontname="helv")
        page.insert_text((450, y), "Betrag", fontsize=10, fontname="helv")
        y += 5
        page.draw_line((50, y), (545, y))
        y += 12

        for idx, item in enumerate(line_items, 1):
            page.insert_text((50, y), str(idx), fontsize=9, fontname="helv")
            page.insert_text((90, y), item["description"][:32], fontsize=9, fontname="helv")
            page.insert_text((280, y), str(item["quantity"]), fontsize=9, fontname="helv")
            page.insert_text((340, y), f"{vendor['currency_symbol']}{item['unit_price']:,.2f}", fontsize=9, fontname="helv")
            page.insert_text((450, y), f"{vendor['currency_symbol']}{item['total']:,.2f}", fontsize=9, fontname="helv")
            y += 15

        page.draw_line((50, y), (545, y))
        y += 15
        page.insert_text((340, y), f"Nettobetrag:", fontsize=10, fontname="helv")
        page.insert_text((450, y), f"{vendor['currency_symbol']}{subtotal:,.2f}", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((340, y), f"MwSt {int(vendor['tax_rate']*100)}%:", fontsize=10, fontname="helv")
        page.insert_text((450, y), f"{vendor['currency_symbol']}{tax_amount:,.2f}", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((340, y), f"Gesamtbetrag:", fontsize=11, fontname="helv")
        page.insert_text((450, y), f"{vendor['currency_symbol']}{grand_total:,.2f}", fontsize=11, fontname="helv")
        y += 30
        page.insert_text((50, y), f"Bitte ueberweisen Sie den Betrag auf das oben genannte Konto.", fontsize=8, fontname="helv")
        y += 12
        page.insert_text((50, y), f"(Please transfer the amount to the bank account listed above.)", fontsize=8, fontname="helv")

    # ── INDIAN LAYOUT (Sharma & Associates) ──
    elif style == "indian":
        y = 50
        page.insert_text((50, y), vendor["name"], fontsize=16, fontname="helv")
        y += 20
        page.insert_text((50, y), vendor["address"], fontsize=9, fontname="helv")
        y += 15
        gstin = f"27AAAAA{random.randint(1000,9999)}A{random.randint(1,9)}Z{random.randint(1,9)}"
        page.insert_text((50, y), f"GSTIN: {gstin}", fontsize=9, fontname="helv")
        y += 25

        page.insert_text((200, y), "TAX INVOICE", fontsize=16, fontname="helv")
        y += 25
        page.draw_line((50, y), (545, y))
        y += 15

        page.insert_text((50, y), f"Invoice No: {invoice_number}", fontsize=10, fontname="helv")
        page.insert_text((350, y), f"Date: {invoice_date.strftime('%d-%m-%Y')}", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((350, y), f"Due Date: {due_date.strftime('%d-%m-%Y')}", fontsize=10, fontname="helv")
        y += 25

        page.insert_text((50, y), "Billed To:", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((50, y), OUR_COMPANY["name"], fontsize=10, fontname="helv")
        y += 13
        page.insert_text((50, y), OUR_COMPANY["address"], fontsize=9, fontname="helv")
        y += 25

        page.insert_text((50, y), "Sr.", fontsize=10, fontname="helv")
        page.insert_text((80, y), "Particulars", fontsize=10, fontname="helv")
        page.insert_text((280, y), "Qty", fontsize=10, fontname="helv")
        page.insert_text((330, y), "Rate", fontsize=10, fontname="helv")
        page.insert_text((420, y), "Amount", fontsize=10, fontname="helv")
        y += 5
        page.draw_line((50, y), (545, y))
        y += 12

        for idx, item in enumerate(line_items, 1):
            page.insert_text((50, y), str(idx), fontsize=9, fontname="helv")
            page.insert_text((80, y), item["description"][:32], fontsize=9, fontname="helv")
            page.insert_text((280, y), str(item["quantity"]), fontsize=9, fontname="helv")
            page.insert_text((330, y), f"{vendor['currency_symbol']}{item['unit_price']:,.2f}", fontsize=9, fontname="helv")
            page.insert_text((420, y), f"{vendor['currency_symbol']}{item['total']:,.2f}", fontsize=9, fontname="helv")
            y += 15

        page.draw_line((50, y), (545, y))
        y += 15
        page.insert_text((50, y), "Taxable Amount:", fontsize=10, fontname="helv")
        page.insert_text((420, y), f"{vendor['currency_symbol']}{subtotal:,.2f}", fontsize=10, fontname="helv")
        y += 15

        # GST split into CGST and SGST
        cgst = round(tax_amount / 2, 2)
        sgst = round(tax_amount / 2, 2)
        page.insert_text((50, y), f"CGST @ {int(vendor['tax_rate']*100/2)}%:", fontsize=10, fontname="helv")
        page.insert_text((420, y), f"{vendor['currency_symbol']}{cgst:,.2f}", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((50, y), f"SGST @ {int(vendor['tax_rate']*100/2)}%:", fontsize=10, fontname="helv")
        page.insert_text((420, y), f"{vendor['currency_symbol']}{sgst:,.2f}", fontsize=10, fontname="helv")
        y += 15
        page.draw_line((50, y), (545, y))
        y += 10
        page.insert_text((50, y), "Total Invoice Value:", fontsize=11, fontname="helv")
        page.insert_text((420, y), f"{vendor['currency_symbol']}{grand_total:,.2f}", fontsize=11, fontname="helv")
        y += 30
        page.insert_text((50, y), "Subject to Mumbai jurisdiction.", fontsize=8, fontname="helv")
        y += 12
        page.insert_text((50, y), "E & OE", fontsize=8, fontname="helv")

    # ── LOGISTICS LAYOUT (FastFreight Ltd) ──
    elif style == "logistics":
        y = 50
        page.insert_text((50, y), vendor["name"], fontsize=16, fontname="helv")
        page.insert_text((380, y), "FREIGHT INVOICE", fontsize=13, fontname="helv")
        y += 20
        page.insert_text((50, y), vendor["address"], fontsize=9, fontname="helv")
        y += 25

        page.draw_line((50, y), (545, y))
        y += 15

        page.insert_text((50, y), f"Invoice No: {invoice_number}", fontsize=10, fontname="helv")
        page.insert_text((350, y), f"Issue Date: {invoice_date.strftime('%d %b %Y')}", fontsize=10, fontname="helv")
        y += 15
        shipment_ref = f"SHP-{random.randint(100000, 999999)}"
        page.insert_text((50, y), f"Shipment Ref: {shipment_ref}", fontsize=10, fontname="helv")
        page.insert_text((350, y), f"Due Date: {due_date.strftime('%d %b %Y')}", fontsize=10, fontname="helv")
        y += 15
        if vendor["has_po_number"]:
            po_number = f"PO-{random.randint(10000, 99999)}"
            page.insert_text((50, y), f"PO Reference: {po_number}", fontsize=10, fontname="helv")
        y += 25

        page.insert_text((50, y), "Invoice To:", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((50, y), OUR_COMPANY["name"], fontsize=10, fontname="helv")
        y += 13
        page.insert_text((50, y), OUR_COMPANY["address"], fontsize=9, fontname="helv")
        y += 25

        page.insert_text((50, y), "Service Description", fontsize=10, fontname="helv")
        page.insert_text((250, y), "Tracking Ref", fontsize=10, fontname="helv")
        page.insert_text((360, y), "Qty", fontsize=10, fontname="helv")
        page.insert_text((400, y), "Rate", fontsize=10, fontname="helv")
        page.insert_text((470, y), "Charges", fontsize=10, fontname="helv")
        y += 5
        page.draw_line((50, y), (545, y))
        y += 12

        for item in line_items:
            tracking = f"TRK{random.randint(100000000, 999999999)}"
            page.insert_text((50, y), item["description"][:25], fontsize=9, fontname="helv")
            page.insert_text((250, y), tracking, fontsize=8, fontname="helv")
            page.insert_text((360, y), str(item["quantity"]), fontsize=9, fontname="helv")
            page.insert_text((400, y), f"{vendor['currency_symbol']}{item['unit_price']:,.2f}", fontsize=9, fontname="helv")
            page.insert_text((470, y), f"{vendor['currency_symbol']}{item['total']:,.2f}", fontsize=9, fontname="helv")
            y += 15

        page.draw_line((50, y), (545, y))
        y += 15
        page.insert_text((350, y), f"Net Charges:", fontsize=10, fontname="helv")
        page.insert_text((470, y), f"{vendor['currency_symbol']}{subtotal:,.2f}", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((350, y), f"{vendor['tax_label']} ({int(vendor['tax_rate']*100)}%):", fontsize=10, fontname="helv")
        page.insert_text((470, y), f"{vendor['currency_symbol']}{tax_amount:,.2f}", fontsize=10, fontname="helv")
        y += 15
        page.insert_text((350, y), "Total Payable:", fontsize=11, fontname="helv")
        page.insert_text((470, y), f"{vendor['currency_symbol']}{grand_total:,.2f}", fontsize=11, fontname="helv")
        y += 30
        page.insert_text((50, y), f"Shipment Ref: {shipment_ref} | Terms: Net 30", fontsize=8, fontname="helv")

    # ── ERROR WATERMARK ──
    if error_description:
        page.insert_text((50, 800), f"[TEST FLAG: {error_description}]", fontsize=8, fontname="helv")

    # ── SAVE PDF ──
    filename = f"{OUTPUT_DIR}/{invoice_number}.pdf"
    doc.save(filename)
    doc.close()

    return filename, error_description


def main():
    """Generate a full batch of test invoices"""
    
    print("Starting FinSight AI Invoice Generator...")
    print(f"Output directory: {OUTPUT_DIR}")
    print("-" * 50)
    
    generated = []
    invoice_counter = 1
    invoices_per_vendor = 6
    
    for vendor in VENDORS:
        print(f"\nGenerating invoices for: {vendor['name']}")
        
        for i in range(invoices_per_vendor):
            # Every 3rd invoice gets an error injected
            inject_error = (i % 3 == 0)
            
            # Generate unique invoice number
            invoice_number = f"INV-{vendor['currency']}-{str(invoice_counter).zfill(4)}"
            
            # Generate the PDF
            filename, error_description = generate_invoice_pdf(
                vendor=vendor,
                invoice_number=invoice_number,
                inject_error=inject_error
            )
            
            # Track what we generated
            generated.append({
                "invoice_number": invoice_number,
                "vendor": vendor["name"],
                "currency": vendor["currency"],
                "has_error": inject_error,
                "error_type": error_description,
                "filename": filename
            })
            
            status = "❌ ERROR INJECTED" if inject_error else "✅ CLEAN"
            print(f"  {invoice_number} — {status}")
            
            invoice_counter += 1
    
    print("\n" + "-" * 50)
    print(f"Generation complete.")
    print(f"Total invoices generated: {len(generated)}")
    print(f"Clean invoices: {sum(1 for i in generated if not i['has_error'])}")
    print(f"Invoices with errors: {sum(1 for i in generated if i['has_error'])}")
    print(f"\nAll invoices saved to: {OUTPUT_DIR}")
    
    return generated



if __name__ == "__main__":
    main()