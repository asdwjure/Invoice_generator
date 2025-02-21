import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, 
    QMessageBox, QAbstractItemView, QComboBox, QCheckBox, QLabel, QStyle
)
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta
from invoice_model import Invoice, InvoiceItem
from invoice_metadata import (
    get_next_invoice_number, load_last_items, save_last_items, 
    load_last_info, save_last_info, load_invoice_options, save_invoice_options
)
from invoice_generator import generate_invoice_pdf, generate_invoice_pdf_slovene
from client_manager import load_clients

class InvoiceGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice Generator by Jure Rebernik")
        self.invoice_items = []
        self.predefined_clients = load_clients()  # load predefined clients from file
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Contractor Info Group (with extra fields)
        contractor_group = QGroupBox("Contractor Information")
        contractor_layout = QFormLayout()
        self.company_name_edit = QLineEdit()
        self.address_edit = QLineEdit()
        self.registration_number_edit = QLineEdit()
        self.vat_number_edit = QLineEdit()
        self.bank_info_edit = QLineEdit()
        self.swift_edit = QLineEdit()
        contractor_layout.addRow("Company Name:", self.company_name_edit)
        contractor_layout.addRow("Address:", self.address_edit)
        contractor_layout.addRow("Registration Number:", self.registration_number_edit)
        contractor_layout.addRow("VAT Number:", self.vat_number_edit)
        contractor_layout.addRow("Bank Account Info:", self.bank_info_edit)
        contractor_layout.addRow("SWIFT:", self.swift_edit)
        contractor_group.setLayout(contractor_layout)
        
        # Client Info Group with predefined client dropdown
        client_group = QGroupBox("Client Information")
        client_layout = QFormLayout()
        
        # New: Predefined Client dropdown
        self.predefined_client_combo = QComboBox()
        # First option is "Custom" meaning no predefined client is chosen.
        self.predefined_client_combo.addItem("Custom")
        # Then add each predefined client (using their company name as display)
        for client in self.predefined_clients:
            self.predefined_client_combo.addItem(client.get("company_name", ""))
        self.predefined_client_combo.currentIndexChanged.connect(self.on_predefined_client_changed)
        client_layout.addRow("Predefined Client:", self.predefined_client_combo)
        
        # Client fields (editable)
        self.client_name_edit = QLineEdit()
        self.client_address_edit = QLineEdit()
        self.client_registration_edit = QLineEdit()
        self.client_vat_edit = QLineEdit()
        client_layout.addRow("Client Company Name:", self.client_name_edit)
        client_layout.addRow("Client Address:", self.client_address_edit)
        client_layout.addRow("Client Registration Number:", self.client_registration_edit)
        client_layout.addRow("Client VAT Number:", self.client_vat_edit)
        client_group.setLayout(client_layout)
        
        main_layout.addWidget(contractor_group)
        main_layout.addWidget(client_group)
        
        # Load Last Contractor and Client Info (if any)
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
            self.client_registration_edit.setText(client_info.get("registration_number", ""))
            self.client_vat_edit.setText(client_info.get("vat_number", ""))
            
        # Invoice Options Group (Vertical Layout; language first)
        options_group = QGroupBox("Invoice Options")
        options_layout = QVBoxLayout()
        # Due date selection
        due_date_layout = QHBoxLayout()
        due_date_label = QLabel("Due date (days from now):")
        self.due_date_edit = QLineEdit()
        self.due_date_edit.setPlaceholderText("15")
        self.due_date_edit.setMaximumWidth(50)
        due_date_layout.addWidget(due_date_label)
        due_date_layout.addWidget(self.due_date_edit)
        # Language selection
        language_layout = QHBoxLayout()
        language_label = QLabel("Select language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Slovene"])
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        # Include VAT checkbox
        self.include_vat_checkbox = QCheckBox("Include VAT")
        # Reverse charge note checkbox
        self.include_note_checkbox = QCheckBox("Include reverse charge note")
        options_layout.addLayout(due_date_layout)
        options_layout.addLayout(language_layout)
        options_layout.addWidget(self.include_vat_checkbox)
        options_layout.addWidget(self.include_note_checkbox)
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Load Invoice Options
        options = load_invoice_options()
        self.include_vat_checkbox.setChecked(options.get("include_vat", False))
        language = options.get("language", "English")
        index = self.language_combo.findText(language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        self.include_note_checkbox.setChecked(options.get("include_note", False))
            
        # Invoice Item Entry Group (with VAT field)
        item_entry_group = QGroupBox("Add Invoice Item")
        item_entry_layout = QHBoxLayout()
        self.item_desc_edit = QLineEdit()
        self.item_desc_edit.setPlaceholderText("Description")
        self.unit_price_edit = QLineEdit()
        self.unit_price_edit.setPlaceholderText("Unit Price (EUR)")
        self.quantity_edit = QLineEdit()
        self.quantity_edit.setPlaceholderText("Quantity")
        self.item_vat_edit = QLineEdit()
        self.item_vat_edit.setPlaceholderText("VAT Rate (%)")
        self.item_vat_edit.setMaximumWidth(100)
        add_item_btn = QPushButton("Add")
        add_item_btn.clicked.connect(self.add_item)
        item_entry_layout.addWidget(self.item_desc_edit)
        item_entry_layout.addWidget(self.unit_price_edit)
        item_entry_layout.addWidget(self.quantity_edit)
        item_entry_layout.addWidget(self.item_vat_edit)
        item_entry_layout.addWidget(add_item_btn)
        item_entry_group.setLayout(item_entry_layout)
        main_layout.addWidget(item_entry_group)
        
        # Invoice Items Table (7 columns)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Description", "Unit Price (EUR)", "Quantity", "VAT Rate (%)", "VAT Amount (EUR)", "Total (EUR)", ""
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        main_layout.addWidget(self.table)
        
        # Load Last Invoice Items
        last_items_data = load_last_items()
        for item_data in last_items_data:
            vat_rate = item_data.get("vat_rate", 0.0)
            item = InvoiceItem(
                description=item_data["description"],
                unit_price=item_data["unit_price"],
                quantity=item_data["quantity"],
                vat_rate=vat_rate
            )
            self.invoice_items.append(item)
            self.add_item_to_table(item)
            
        # Generate Invoice Button
        generate_btn = QPushButton("Generate Invoice")
        generate_btn.clicked.connect(self.generate_invoice)
        main_layout.addWidget(generate_btn)
        
        self.setLayout(main_layout)
        
    def on_predefined_client_changed(self, index):
        if index == 0:
            self.client_name_edit.clear()
            self.client_address_edit.clear()
            self.client_registration_edit.clear()  # Clear new field
            self.client_vat_edit.clear()  # Clear new field
        else:
            client = self.predefined_clients[index - 1]
            self.client_name_edit.setText(client.get("company_name", ""))
            self.client_address_edit.setText(client.get("address", ""))
            self.client_registration_edit.setText(client.get("registration_number", ""))  # Set new field
            self.client_vat_edit.setText(client.get("vat_number", ""))  # Set new field
            
    def add_item(self):
        desc = self.item_desc_edit.text().strip()
        try:
            unit_price = float(self.unit_price_edit.text().strip())
            quantity = int(self.quantity_edit.text().strip())
            vat_rate = float(self.item_vat_edit.text().strip()) if self.item_vat_edit.text().strip() else 0.0
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please enter valid numeric values for unit price, quantity, and VAT rate.")
            return
        
        if not desc:
            QMessageBox.critical(self, "Input Error", "Item description cannot be empty.")
            return
        
        item = InvoiceItem(description=desc, unit_price=unit_price, quantity=quantity, vat_rate=vat_rate)
        self.invoice_items.append(item)
        self.add_item_to_table(item)
        
        # Clear entry fields
        self.item_desc_edit.clear()
        self.unit_price_edit.clear()
        self.quantity_edit.clear()
        self.item_vat_edit.clear()
        
    def add_item_to_table(self, item):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(item.description))
        self.table.setItem(row_position, 1, QTableWidgetItem(f"{item.unit_price:.2f}"))
        self.table.setItem(row_position, 2, QTableWidgetItem(str(item.quantity)))
        self.table.setItem(row_position, 3, QTableWidgetItem(f"{item.vat_rate:.2f}"))
        self.table.setItem(row_position, 4, QTableWidgetItem(f"{item.vat_amount:.2f}"))
        self.table.setItem(row_position, 5, QTableWidgetItem(f"{item.total_gross:.2f}"))
        
        # Remove button with trash icon
        remove_btn = QPushButton()
        remove_btn.setFlat(True)
        trash_icon = self.style().standardIcon(QStyle.SP_TrashIcon)
        remove_btn.setIcon(trash_icon)
        remove_btn.clicked.connect(lambda _, row=row_position: self.remove_item(row))
        self.table.setCellWidget(row_position, 6, remove_btn)
        
    def remove_item(self, row):
        self.table.removeRow(row)
        if row < len(self.invoice_items):
            del self.invoice_items[row]
        self.update_remove_buttons()
        
    def update_remove_buttons(self):
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 6)
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
        
        include_vat = self.include_vat_checkbox.isChecked()
        language = self.language_combo.currentText()
        include_note = self.include_note_checkbox.isChecked()
        save_invoice_options(include_vat, language, include_note)
        
        invoice_number = get_next_invoice_number()
        issue_date = datetime.now().date()
        due_date = issue_date + timedelta(days=int(self.due_date_edit.text().strip() or 15))
        
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
            "address": self.client_address_edit.text().strip(),
            "registration_number": self.client_registration_edit.text().strip(),  # Add new field
            "vat_number": self.client_vat_edit.text().strip()  # Add new field
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
            if language == "Slovene":
                generate_invoice_pdf_slovene(invoice, include_vat, include_note)
            else:
                generate_invoice_pdf(invoice, include_vat, include_note)
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
