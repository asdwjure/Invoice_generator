class InvoiceItem:
    def __init__(self, description, unit_price, quantity, vat_rate=0.0):
        self.description = description
        self.unit_price = unit_price
        self.quantity = quantity
        self.vat_rate = vat_rate
        self.total_net = unit_price * quantity
        self.vat_amount = self.total_net * (vat_rate / 100)
        self.total_gross = self.total_net + self.vat_amount

class Invoice:
    def __init__(self, invoice_number, issue_date, due_date, contractor_info, client_info, items):
        self.invoice_number = invoice_number
        self.issue_date = issue_date
        self.due_date = due_date
        self.contractor_info = contractor_info  # dict with keys: company_name, address, bank_info, swift
        self.client_info = client_info          # dict with keys: company_name, address
        self.items = items  # List of InvoiceItem objects

    @property
    def total_net(self):
        return sum(item.total_net for item in self.items)
    
    @property
    def total_vat(self):
        return sum(item.vat_amount for item in self.items)
    
    @property
    def total_gross(self):
        return self.total_net + self.total_vat
