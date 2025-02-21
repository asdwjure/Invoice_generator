import json
import os

CLIENTS_FILE = "clients.json"

def load_clients():
    """Load the list of predefined clients from the JSON file.
    The file should contain a list of objects, e.g.:
      [
         {"company_name": "ABC Ltd.", "address": "123 Main St"},
         {"company_name": "XYZ Inc.", "address": "456 Side Ave"}
      ]
    """
    if os.path.exists(CLIENTS_FILE):
        with open(CLIENTS_FILE, "r") as f:
            return json.load(f)
    return []

def save_clients(clients):
    """Save the given list of client dictionaries to the JSON file."""
    with open(CLIENTS_FILE, "w") as f:
        json.dump(clients, f, indent=2)
