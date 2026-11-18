import json
from pathlib import Path

import frappe

from order_management.permissions import is_admin


def setup():
    if not is_admin():
        frappe.throw("Administrator required", frappe.PermissionError)
    # Serialize seed runs on this site; keep the lock until the caller commits/rolls back.
    frappe.db.sql("SELECT name FROM `tabUser` WHERE name = 'Administrator' FOR UPDATE")
    rows = frappe.db.sql(Path(__file__).with_name("seed.sql").read_text(encoding="utf-8"), as_dict=True)
    for entity in ("User", "Stock Item", "Simple Order"):
        for row in rows:
            if row.entity != entity:
                continue
            data = json.loads(row.payload)
            name = data.get("email") or data.get("item_code") or data["name"]
            if frappe.db.get_value(entity, name, "name", for_update=True):
                continue
            if entity == "User":
                role, password = data.pop("role"), data.pop("password")
                frappe.get_doc({
                    "doctype": entity, **data, "user_type": "System User", "send_welcome_email": 0,
                    "new_password": password, "roles": [{"role": role}],
                    "default_workspace": "Order Management",
                }).insert(ignore_permissions=True)
            elif entity == "Stock Item":
                opening = data.pop("opening_stock")
                frappe.get_doc({"doctype": entity, **data}).insert()
                frappe.get_doc({
                    "doctype": "Stock Receipt", "item": name, "quantity": opening, "note": "Tồn đầu demo",
                }).insert()
            else:
                sale = data.pop("sale")
                status = data.pop("status", "Mới")
                data.pop("name")
                try:
                    frappe.set_user(sale)
                    order = frappe.get_doc({"doctype": entity, **data}).insert(set_name=name)
                    if status != "Mới":
                        if status == "Đã giao":
                            frappe.set_user(order.warehouse_user)
                        order.status = status
                        order.save()
                finally:
                    frappe.set_user("Administrator")
