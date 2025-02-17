from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

def generate_invoice_pdf(invoice):
    file_name = f"{invoice.invoice_number}.pdf"
    c = canvas.Canvas(file_name, pagesize=A4)
    width, height = A4

    margin = 20 * mm
    y = height - margin

    # Header with Invoice Number, Issue Date, Due Date
    c.setFont("Helvetica-Bold", 20)
    c.drawString(margin, y, f"Invoice: {invoice.invoice_number}")
    y -= 25
    c.setFont("Helvetica", 11)
    c.drawString(margin, y, f"Issue Date: {invoice.issue_date}")
    y -= 15
    c.drawString(margin, y, f"Due Date: {invoice.due_date}")
    y -= 50

    # Contractor Information
    c.setFont("Helvetica-Bold", 13)
    c.drawString(margin, y, "From:")
    y -= 20
    c.setFont("Helvetica", 11)
    contractor = invoice.contractor_info
    c.drawString(margin, y, contractor.get("company_name", ""))
    y -= 15
    c.drawString(margin, y, contractor.get("address", ""))
    y -= 15
    c.drawString(margin, y, f"Registration Number: {contractor.get('registration_number', '')}")
    y -= 15
    c.drawString(margin, y, f"VAT Number: {contractor.get('vat_number', '')}")
    y -= 15
    c.drawString(margin, y, f"IBAN bank account number: {contractor.get('bank_info', '')}")
    y -= 15
    c.drawString(margin, y, f"SWIFT: {contractor.get('swift', '')}")
    y -= 50

    # Client Information
    c.setFont("Helvetica-Bold", 13)
    c.drawString(margin, y, "Bill To:")
    y -= 20
    c.setFont("Helvetica", 11)
    client = invoice.client_info
    c.drawString(margin, y, client.get("company_name", ""))
    y -= 15
    c.drawString(margin, y, client.get("address", ""))
    y -= 100

    # Invoice Items Table Header
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Description")
    c.drawString(margin + 250, y, "Unit Price (EUR)")
    c.drawString(margin + 355, y, "Quantity")
    c.drawString(margin + 420, y, "Total (EUR)")
    y -= 15
    c.setFont("Helvetica", 11)
    c.line(margin, y, width - margin, y)
    y -= 15

    # List each invoice item
    for item in invoice.items:
        c.drawString(margin, y, item.description)
        c.drawRightString(margin + 330, y, f"{item.unit_price:.2f}")
        c.drawRightString(margin + 398, y, f"{item.quantity}")
        c.drawRightString(margin + 480, y, f"{item.total:.2f}")
        y -= 15

    c.line(margin, y, width - margin, y)
    y -= 30

    # Total Amount
    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(width - margin, y, f"Total: {invoice.total_amount:.2f} EUR")

    # Add note
    y -= 100
    c.setFont("Helvetica", 11)
    c.drawString(margin, y, "Note: VAT is not charged according to the Article 44 of the Directive EU 2006/112/ES –")
    y -= 15
    c.drawString(margin, y, "reverse charge (for recipient).")

    # Save the PDF file
    c.showPage()
    c.save()
