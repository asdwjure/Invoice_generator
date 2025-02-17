class InvoiceItem:
    def __init__(self, description, unit_price, quantity):
        self.description = description
        self.unit_price = unit_price
        self.quantity = quantity
        self.total = unit_price * quantity

class Invoice:
    def __init__(self, invoice_number, issue_date, due_date, contractor_info, client_info, items):
        self.invoice_number = invoice_number
        self.issue_date = issue_date
        self.due_date = due_date
        self.contractor_info = contractor_info  # dict with keys: company_name, address, bank_info, swift
        self.client_info = client_info          # dict with keys: company_name, address
        self.items = items  # List of InvoiceItem objects
        self.total_amount = sum(item.total for item in items)
