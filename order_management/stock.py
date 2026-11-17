from math import isfinite

import frappe
from frappe import _
from frappe.utils import flt


def change_stock(item, quantity):
    # One item row lock serializes receipts and deliveries in the caller's transaction.
    rows = frappe.db.sql(
        "SELECT stock_qty, enabled FROM `tabStock Item` WHERE name = %s FOR UPDATE", (item,), as_dict=True
    )
    if not rows or not rows[0].enabled:
        frappe.throw(_("Mặt hàng không tồn tại hoặc đã ngừng sử dụng."))
    balance = flt(rows[0].stock_qty + quantity, 3)
    if balance < 0:
        frappe.throw(_("Không đủ tồn kho. Hiện còn {0}, cần xuất {1}.").format(rows[0].stock_qty, -quantity))
    if not isfinite(balance):
        frappe.throw(_("Tồn kho vượt quá phạm vi cho phép."))
    frappe.db.set_value("Stock Item", item, "stock_qty", balance)
    return balance
