import json
import os
from datetime import datetime

METADATA_FILE = "invoice_metadata.json"
SEQUENCE_LENGTH = 3  # number of digits for the sequence

def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}
    return data

def save_metadata(data):
    with open(METADATA_FILE, "w") as f:
        json.dump(data, f)

def get_next_invoice_number():
    current_year = datetime.now().year
    data = load_metadata()
    # If year is different or no data exists, reset sequence (but keep saved info)
    if str(current_year) != data.get("year"):
        data["year"] = str(current_year)
        data["sequence"] = 0
    # Increment sequence
    data["sequence"] = data.get("sequence", 0) + 1
    save_metadata(data)
    invoice_number = f"{current_year}-{data['sequence']:0{SEQUENCE_LENGTH}d}"
    return invoice_number

def load_last_items():
    data = load_metadata()
    return data.get("last_items", [])

def save_last_items(items):
    # 'items' is expected to be a list of InvoiceItem objects.
    data = load_metadata()
    # Convert each invoice item to a dict
    last_items = [
        {"description": item.description, "unit_price": item.unit_price, "quantity": item.quantity}
        for item in items
    ]
    data["last_items"] = last_items
    save_metadata(data)

def load_last_info():
    """Load the last used contractor and client info."""
    data = load_metadata()
    contractor_info = data.get("contractor_info", {})
    client_info = data.get("client_info", {})
    return contractor_info, client_info

def save_last_info(contractor_info, client_info):
    """Save contractor and client info to metadata."""
    data = load_metadata()
    data["contractor_info"] = contractor_info
    data["client_info"] = client_info
    save_metadata(data)
