from hashlib import sha256

import frappe


def execute():
    for order in frappe.get_all("Simple Order", fields=["name", "item", "item_name", "unit_price"]):
        if order.item:
            continue
        name = order.item_name or "Mặt hàng cũ"
        code = "OLD-" + sha256(name.encode()).hexdigest()[:10].upper()
        if not frappe.db.exists("Stock Item", code):
            frappe.get_doc({
                "doctype": "Stock Item", "item_code": code, "item_name": name,
                "unit": "Cái", "default_unit_price": order.unit_price,
            }).insert(ignore_permissions=True)
        # Link historical orders without inventing opening stock or replaying past deliveries.
        frappe.db.set_value("Simple Order", order.name, "item", code, update_modified=False)
