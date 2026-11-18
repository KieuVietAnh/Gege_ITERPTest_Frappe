from math import isfinite

import frappe
from frappe import _
from frappe.utils import flt


def change_stock(item, quantity, source):
    from order_management.order_management.doctype.stock_movement.stock_movement import STOCK_WRITE

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
    movement = frappe.get_doc({
        "doctype": "Stock Movement", "item": item,
        "movement_type": "Nhập" if quantity > 0 else "Xuất",
        "quantity": abs(quantity), "balance_before": rows[0].stock_qty, "balance_after": balance,
        "source_type": source.doctype, "source_name": source.name,
        "source_key": f"{source.doctype}:{source.name}",
        "performed_by": frappe.session.user, "note": source.get("note"),
    })
    movement.flags.stock_write = STOCK_WRITE
    # A receipt's before_save runs before its source row is inserted.
    movement.flags.ignore_links = True
    movement.insert(ignore_permissions=True)
    frappe.db.set_value("Stock Item", item, "stock_qty", balance)
    return balance
