import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, 
    QMessageBox, QAbstractItemView, QStyle
)
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta
from invoice_model import Invoice, InvoiceItem
from invoice_metadata import (
    get_next_invoice_number, load_last_items, save_last_items, 
    load_last_info, save_last_info
)
from invoice_generator import generate_invoice_pdf

class InvoiceGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice Generator")
        self.invoice_items = []
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Contractor info group
        contractor_group = QGroupBox("Contractor information")
        contractor_layout = QFormLayout()
        self.company_name_edit = QLineEdit()
        self.address_edit = QLineEdit()
        self.registration_number_edit = QLineEdit()
        self.vat_number_edit = QLineEdit()
        self.bank_info_edit = QLineEdit()
        self.swift_edit = QLineEdit()
        contractor_layout.addRow("Company name:", self.company_name_edit)
        contractor_layout.addRow("Address:", self.address_edit)
        contractor_layout.addRow("Registration number:", self.registration_number_edit)
        contractor_layout.addRow("VAT number:", self.vat_number_edit)
        contractor_layout.addRow("IBAN Bank Account number:", self.bank_info_edit)
        contractor_layout.addRow("SWIFT:", self.swift_edit)
        contractor_group.setLayout(contractor_layout)
        
        # Client info group
        client_group = QGroupBox("Client Information")
        client_layout = QFormLayout()
        self.client_name_edit = QLineEdit()
        self.client_address_edit = QLineEdit()
        client_layout.addRow("Client Company Name:", self.client_name_edit)
        client_layout.addRow("Client Address:", self.client_address_edit)
        client_group.setLayout(client_layout)
        
        main_layout.addWidget(contractor_group)
        main_layout.addWidget(client_group)
        
        # Load last used contractor and client info
        contractor_info, client_info = load_last_info()
        if contractor_info:
            self.company_name_edit.setText(contractor_info.get("company_name", ""))
            self.address_edit.setText(contractor_info.get("address", ""))
            self.registration_number_edit.setText(contractor_info.get("registration_number", ""))
            self.vat_number_edit.setText(contractor_info.get("vat_number", ""))
            self.bank_info_edit.setText(contractor_info.get("bank_info", ""))
            self.swift_edit.setText(contractor_info.get("swift", ""))
        if client_info:
            self.client_name_edit.setText(client_info.get("company_name", ""))
            self.client_address_edit.setText(client_info.get("address", ""))
            
        # Invoice item entry group
        item_entry_group = QGroupBox("Add Invoice Item")
        item_entry_layout = QHBoxLayout()
        self.item_desc_edit = QLineEdit()
        self.item_desc_edit.setPlaceholderText("Description")
        self.unit_price_edit = QLineEdit()
        self.unit_price_edit.setPlaceholderText("Unit Price (EUR)")
        self.quantity_edit = QLineEdit()
        self.quantity_edit.setPlaceholderText("Quantity")
        add_item_btn = QPushButton("Add")
        add_item_btn.clicked.connect(self.add_item)
        item_entry_layout.addWidget(self.item_desc_edit)
        item_entry_layout.addWidget(self.unit_price_edit)
        item_entry_layout.addWidget(self.quantity_edit)
        item_entry_layout.addWidget(add_item_btn)
        item_entry_group.setLayout(item_entry_layout)
        main_layout.addWidget(item_entry_group)
        
        # Table for invoice items
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Description", "Unit Price (EUR)", "Quantity", "Total (EUR)", ""])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        main_layout.addWidget(self.table)
        
        # Load last invoice items from metadata (if any)
        last_items_data = load_last_items()
        for item_data in last_items_data:
            item = InvoiceItem(
                description=item_data["description"],
                unit_price=item_data["unit_price"],
                quantity=item_data["quantity"]
            )
            self.invoice_items.append(item)
            self.add_item_to_table(item)
            
        # Generate Invoice button
        generate_btn = QPushButton("Generate Invoice")
        generate_btn.clicked.connect(self.generate_invoice)
        main_layout.addWidget(generate_btn)
        
        self.setLayout(main_layout)
        
    def add_item(self):
        desc = self.item_desc_edit.text().strip()
        try:
            unit_price = float(self.unit_price_edit.text().strip())
            quantity = int(self.quantity_edit.text().strip())
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please enter valid numeric values for unit price and quantity.")
            return
        
        if not desc:
            QMessageBox.critical(self, "Input Error", "Item description cannot be empty.")
            return
        
        item = InvoiceItem(description=desc, unit_price=unit_price, quantity=quantity)
        self.invoice_items.append(item)
        self.add_item_to_table(item)
        
        # Clear the entry fields
        self.item_desc_edit.clear()
        self.unit_price_edit.clear()
        self.quantity_edit.clear()
        
    def add_item_to_table(self, item):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(item.description))
        self.table.setItem(row_position, 1, QTableWidgetItem(f"{item.unit_price:.2f}"))
        self.table.setItem(row_position, 2, QTableWidgetItem(str(item.quantity)))
        self.table.setItem(row_position, 3, QTableWidgetItem(f"{item.total:.2f}"))
        
        # Add remove button with trash icon
        remove_btn = QPushButton()
        remove_btn.setFlat(True)
        trash_icon = self.style().standardIcon(QStyle.SP_TrashIcon)
        remove_btn.setIcon(trash_icon)
        # Capture the row index in a lambda (note: using default argument to bind current row)
        remove_btn.clicked.connect(lambda _, row=row_position: self.remove_item(row))
        self.table.setCellWidget(row_position, 4, remove_btn)
        
    def remove_item(self, row):
        # Remove the row from the table and corresponding item from invoice_items list
        self.table.removeRow(row)
        if row < len(self.invoice_items):
            del self.invoice_items[row]
        # After removal, update all remove button connections since row indices have changed.
        self.update_remove_buttons()
        
    def update_remove_buttons(self):
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 4)
            if widget:
                widget.clicked.disconnect()
                widget.clicked.connect(lambda _, r=row: self.remove_item(r))
        
    def generate_invoice(self):
        if not self.company_name_edit.text().strip() or not self.address_edit.text().strip():
            QMessageBox.critical(self, "Input Error", "Please fill in your company information.")
            return
        if not self.client_name_edit.text().strip() or not self.client_address_edit.text().strip():
            QMessageBox.critical(self, "Input Error", "Please fill in the client information.")
            return
        if not self.invoice_items:
            QMessageBox.critical(self, "Input Error", "Please add at least one invoice item.")
            return
        
        invoice_number = get_next_invoice_number()
        issue_date = datetime.now().date()
        due_date = issue_date + timedelta(days=15)
        
        contractor_info = {
            "company_name": self.company_name_edit.text().strip(),
            "address": self.address_edit.text().strip(),
            "registration_number": self.registration_number_edit.text().strip(),
            "vat_number": self.vat_number_edit.text().strip(),
            "bank_info": self.bank_info_edit.text().strip(),
            "swift": self.swift_edit.text().strip()
        }
        client_info = {
            "company_name": self.client_name_edit.text().strip(),
            "address": self.client_address_edit.text().strip()
        }
        
        invoice = Invoice(
            invoice_number=invoice_number,
            issue_date=issue_date,
            due_date=due_date,
            contractor_info=contractor_info,
            client_info=client_info,
            items=self.invoice_items
        )
        
        try:
            generate_invoice_pdf(invoice)
            save_last_items(self.invoice_items)
            save_last_info(contractor_info, client_info)
            QMessageBox.information(self, "Invoice Generated", f"Invoice {invoice.invoice_number} generated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        
def main():
    app = QApplication(sys.argv)
    gui = InvoiceGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
