from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu-Bold', 'DejaVuSans-Bold.ttf'))

def generate_invoice_pdf(invoice, include_vat, include_note):
    """Generate an invoice PDF in English."""
    file_name = f"{invoice.invoice_number}.pdf"
    c = canvas.Canvas(file_name, pagesize=A4)
    width, height = A4
    margin = 20 * mm
    y = height - margin

    # Header
    c.setFont("DejaVu-Bold", 16)
    c.drawString(margin, y, f"Invoice number: {invoice.invoice_number}")
    y -= 20
    c.setFont("DejaVu", 10)
    c.drawString(margin, y, f"Issue Date: {invoice.issue_date}")
    y -= 15
    c.drawString(margin, y, f"Due Date: {invoice.due_date}")
    y -= 30

    # Contractor Information
    c.setFont("DejaVu-Bold", 12)
    c.drawString(margin, y, "From:")
    y -= 15
    c.setFont("DejaVu", 10)
    contractor = invoice.contractor_info
    c.drawString(margin, y, contractor.get("company_name", ""))
    y -= 13
    c.drawString(margin, y, contractor.get("address", ""))
    y -= 13
    c.drawString(margin, y, f"Registration Number: {contractor.get('registration_number')}")
    y -= 13
    c.drawString(margin, y, f"VAT Number: {contractor.get('vat_number')}")
    y -= 13
    c.drawString(margin, y, f"Bank Info: {contractor.get('bank_info', '')}")
    y -= 13
    c.drawString(margin, y, f"SWIFT: {contractor.get('swift', '')}")
    y -= 30

    # Client Information
    c.setFont("DejaVu-Bold", 12)
    c.drawString(margin, y, "Bill To:")
    y -= 15
    c.setFont("DejaVu", 10)
    client = invoice.client_info
    c.drawString(margin, y, client.get("company_name", ""))
    y -= 13
    c.drawString(margin, y, client.get("address", ""))
    if client.get("registration_number"):
        y -= 13
        c.drawString(margin, y, f"Registration Number: {client.get('registration_number')}")
    if client.get("vat_number"):
        y -= 13
        c.drawString(margin, y, f"VAT Number: {client.get('vat_number')}")
    y -= 100

    # Invoice Items Table
    c.setFont("DejaVu-Bold", 10)
    if include_vat:
        # Header with VAT columns
        c.drawRightString(margin + 238, y, "Unit")
        c.drawRightString(margin + 338, y, "VAT")
        c.drawRightString(margin + 416, y, "VAT")
        y -= 12
        c.drawString(margin, y, "Description")
        c.drawRightString(margin + 238, y, "Price (EUR)")
        c.drawRightString(margin + 289, y, "Quantity")
        c.drawRightString(margin + 338, y, "Rate (%)")
        c.drawRightString(margin + 416, y, "Amount (EUR)")
        c.drawRightString(width - margin, y, "Total (EUR)")
    else:
        # Header without VAT columns
        c.drawString(margin, y, "Description")
        c.drawRightString(margin + 330, y, "Unit Price (EUR)")
        c.drawRightString(margin + 400, y, "Quantity")
        c.drawRightString(width - margin, y, "Total (EUR)")
    y -= 15
    c.setFont("DejaVu", 10)
    c.line(margin, y, width - margin, y)
    y -= 10

    # List invoice items
    for item in invoice.items:
        c.drawString(margin, y, item.description)
        if include_vat:
            c.drawRightString(margin + 238, y, f"{item.unit_price:.2f}")
            c.drawRightString(margin + 289, y, f"{item.quantity}")
            c.drawRightString(margin + 338, y, f"{item.vat_rate:.2f}")
            c.drawRightString(margin + 416, y, f"{item.vat_amount:.2f}")
            c.drawRightString(width - margin, y, f"{item.total_gross:.2f}")
        else:
            c.drawRightString(margin + 330, y, f"{item.unit_price:.2f}")
            c.drawRightString(margin + 400, y, f"{item.quantity}")
            c.drawRightString(width - margin, y, f"{item.total_net:.2f}")
        y -= 15

    y -= 10
    c.line(margin, y, width - margin, y)
    y -= 20

    # Totals
    if include_vat:
        subtotal_net = invoice.total_net
        total_vat = invoice.total_vat
        grand_total = subtotal_net + total_vat
        c.setFont("DejaVu", 12)
        c.drawRightString(width - margin, y, f"Subtotal: {subtotal_net:.2f} EUR")
        y -= 15
        c.drawRightString(width - margin, y, f"VAT: {total_vat:.2f} EUR")
        y -= 15
        c.setFont("DejaVu-Bold", 12)
        c.drawRightString(width - margin, y, f"Total: {grand_total:.2f} EUR")
    else:
        total = invoice.total_net  # net equals gross if no VAT
        c.setFont("DejaVu-Bold", 12)
        c.drawRightString(width - margin, y, f"Total: {total:.2f} EUR")
    y -= 100

    if include_note:
        c.setFont("DejaVu", 9)
        note = ["Note: VAT is not charged according to the Article 44 of the Directive ",
                "EU 2006/112/ES – reverse charge (for recipient)."]
        c.drawString(margin, y, note[0])
        y -= 11
        c.drawString(margin, y, note[1])

    c.showPage()
    c.save()

def generate_invoice_pdf_slovene(invoice, include_vat, include_note):
    """Generate an invoice PDF in Slovene."""
    file_name = f"{invoice.invoice_number}.pdf"
    c = canvas.Canvas(file_name, pagesize=A4)
    width, height = A4
    margin = 20 * mm
    y = height - margin

    # Header
    c.setFont("DejaVu-Bold", 16)
    c.drawString(margin, y, f"Račun številka: {invoice.invoice_number}")
    y -= 20
    c.setFont("DejaVu", 10)
    c.drawString(margin, y, f"Datum izdaje: {invoice.issue_date}")
    y -= 15
    c.drawString(margin, y, f"Datum zapadlosti: {invoice.due_date}")
    y -= 30

    # Contractor Information
    c.setFont("DejaVu-Bold", 12)
    c.drawString(margin, y, "Izvajalec:")
    y -= 15
    c.setFont("DejaVu", 10)
    contractor = invoice.contractor_info
    c.drawString(margin, y, contractor.get("company_name", ""))
    y -= 13
    c.drawString(margin, y, contractor.get("address", ""))
    y -= 13
    c.drawString(margin, y, f"Matična številka: {contractor.get('registration_number')}")
    y -= 13
    c.drawString(margin, y, f"Davčna številka: {contractor.get('vat_number')}")
    y -= 13
    c.drawString(margin, y, f"TRR: {contractor.get('bank_info', '')}")
    y -= 13
    c.drawString(margin, y, f"SWIFT: {contractor.get('swift', '')}")
    y -= 30

    # Client Information
    c.setFont("DejaVu-Bold", 12)
    c.drawString(margin, y, "Naročnik:")
    y -= 15
    c.setFont("DejaVu", 10)
    client = invoice.client_info
    c.drawString(margin, y, client.get("company_name", ""))
    y -= 13
    c.drawString(margin, y, client.get("address", ""))
    if client.get("registration_number"):
        y -= 13
        c.drawString(margin, y, f"Matična številka: {client.get('registration_number')}")
    if client.get("vat_number"):
        y -= 13
        c.drawString(margin, y, f"Davčna številka: {client.get('vat_number')}")
    y -= 100

    # Invoice Items Table
    c.setFont("DejaVu-Bold", 10)
    if include_vat:
        # Header with VAT columns
        c.drawRightString(margin + 222, y, "Cena na")
        c.drawRightString(margin + 331, y, "Stopnja")
        c.drawRightString(margin + 400, y, "Znesek")
        y -= 12
        c.drawString(margin, y, "Opis")
        c.drawRightString(margin + 222, y, "enoto (EUR)")
        c.drawRightString(margin + 275, y, "Količina")
        c.drawRightString(margin + 331, y, "DDV (%)")
        c.drawRightString(margin + 400, y, "DDV (EUR)")
        c.drawRightString(width - margin, y, "Skupaj (EUR)")
    else:
        # Header without VAT columns
        c.drawString(margin, y, "Opis")
        c.drawRightString(margin + 330, y, "Cena na enoto (EUR)")
        c.drawRightString(margin + 400, y, "Količina")
        c.drawRightString(width - margin, y, "Skupaj (EUR)")
    y -= 15
    c.setFont("DejaVu", 10)
    c.line(margin, y, width - margin, y)
    y -= 13

    # List invoice items
    for item in invoice.items:
        c.drawString(margin, y, item.description)
        if include_vat:
            c.drawRightString(margin + 222, y, f"{item.unit_price:.2f}".replace(".", ","))
            c.drawRightString(margin + 275, y, f"{item.quantity}")
            c.drawRightString(margin + 331, y, f"{item.vat_rate:.2f}".replace(".", ","))
            c.drawRightString(margin + 400, y, f"{item.vat_amount:.2f}".replace(".", ","))
            c.drawRightString(width - margin, y, f"{item.total_gross:.2f}".replace(".", ","))
        else:
            c.drawRightString(margin + 330, y, f"{item.unit_price:.2f}".replace(".", ","))
            c.drawRightString(margin + 400, y, f"{item.quantity}")
            c.drawRightString(width - margin, y, f"{item.total_net:.2f}".replace(".", ","))
        y -= 15

    y -= 10
    c.line(margin, y, width - margin, y)
    y -= 20

    # Totals
    if include_vat:
        subtotal_net = invoice.total_net
        total_vat = invoice.total_vat
        grand_total = subtotal_net + total_vat
        c.setFont("DejaVu", 12)
        c.drawRightString(width - margin, y, f"Skupaj brez DDV: {subtotal_net:.2f} EUR".replace(".", ","))
        y -= 15
        c.drawRightString(width - margin, y, f"DDV: {total_vat:.2f} EUR".replace(".", ","))
        y -= 7
        c.line(350, y, width - margin, y)
        y -= 18
        c.setFont("DejaVu-Bold", 12)
        c.drawRightString(width - margin, y, f"Skupaj z DDV: {grand_total:.2f} EUR".replace(".", ","))
    else:
        total = invoice.total_net  # net equals gross if no VAT
        c.setFont("DejaVu-Bold", 12)
        c.drawRightString(width - margin, y, f"Skupaj: {total:.2f} EUR".replace(".", ","))
    y -= 100

    if include_note:
        c.setFont("DejaVu", 9)
        note = ["Opomba: DDV se ne obračuna v skladu s 44. členom Direktive EU 2006/112/ES – ",
                "obratno obračunavanje (za prejemnika)."]
        c.drawString(margin, y, note[0])
        y -= 11
        c.drawString(margin, y, note[1])

    c.showPage()
    c.save()