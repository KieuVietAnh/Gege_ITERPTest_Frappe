from uuid import uuid4

import frappe


def make_item(stock=100):
    code = "TEST-" + uuid4().hex[:12]
    item = frappe.get_doc({
        "doctype": "Stock Item", "item_code": code, "item_name": "Mặt hàng thử nghiệm",
        "unit": "Cái", "default_unit_price": 150000,
    }).insert()
    if stock:
        frappe.get_doc({"doctype": "Stock Receipt", "item": code, "quantity": stock}).insert()
    return item
