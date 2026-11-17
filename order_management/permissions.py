import frappe
from frappe import _

SALES = "Order Sales"
WAREHOUSE = "Order Warehouse"


def is_admin(user=None):
    return (user or frappe.session.user) == "Administrator"


def can_manage_stock(user=None):
    return is_admin(user) or WAREHOUSE in frappe.get_roles(user)


def order_query(user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return ""
    roles = frappe.get_roles(user)
    escaped = frappe.db.escape(user)
    conditions = []
    if SALES in roles:
        conditions.append(f"`tabSimple Order`.owner = {escaped}")
    if WAREHOUSE in roles:
        conditions.append(f"`tabSimple Order`.warehouse_user = {escaped}")
    return "(" + " OR ".join(conditions) + ")" if conditions else "1=0"


def can_access_order(doc, user=None):
    user = user or frappe.session.user
    roles = frappe.get_roles(user)
    return is_admin(user) or (
        SALES in roles and doc.owner == user
    ) or (WAREHOUSE in roles and doc.warehouse_user == user)


def order_permission(doc, ptype=None, user=None):
    user = user or frappe.session.user
    if is_admin(user):
        return True
    if ptype == "create" or doc.is_new():
        return SALES in frappe.get_roles(user)
    if ptype not in (None, "read", "select", "write", "print"):
        return False
    # Check persisted ownership, never a replacement owner/assignee sent by the client.
    stored = frappe.db.get_value("Simple Order", doc.name, ["owner", "warehouse_user"], as_dict=True)
    return bool(stored and can_access_order(stored, user))


def prevent_order_sharing(doc, method=None):
    if doc.share_doctype == "Simple Order":
        frappe.throw(_("Quyền xem đơn theo người tạo/người xử lý kho; không chia sẻ đơn riêng."), frappe.PermissionError)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def warehouse_users(doctype, txt, searchfield, start, page_len, filters):
    if not is_admin() and SALES not in frappe.get_roles():
        frappe.throw(_("Không có quyền phân công kho."), frappe.PermissionError)
    return frappe.db.sql(
        """SELECT u.name, u.full_name FROM `tabUser` u
        INNER JOIN `tabHas Role` r ON r.parent = u.name AND r.parenttype = 'User'
        WHERE u.enabled = 1 AND u.user_type = 'System User' AND r.role = %s
          AND (u.name LIKE %s OR u.full_name LIKE %s)
        ORDER BY u.name LIMIT %s OFFSET %s""",
        (WAREHOUSE, f"%{txt}%", f"%{txt}%", page_len, start),
    )
