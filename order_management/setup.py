import frappe


def ensure_roles():
    for role in ("Order Sales", "Order Warehouse"):
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(
                ignore_permissions=True
            )
