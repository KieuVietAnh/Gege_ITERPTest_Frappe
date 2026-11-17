import frappe
from frappe import _


def execute(filters=None):
    if frappe.session.user != "Administrator":
        frappe.throw(_("Chỉ Admin được xem doanh thu toàn hệ thống."), frappe.PermissionError)
    frappe.has_permission("Simple Order", "report", throw=True)
    columns = [
        {"fieldname": "order_date", "label": _("Ngày tạo đơn"), "fieldtype": "Date", "width": 160},
        {"fieldname": "order_count", "label": _("Số đơn đã giao"), "fieldtype": "Int", "width": 160},
        {"fieldname": "revenue", "label": _("Doanh thu"), "fieldtype": "Currency", "width": 200},
    ]
    data = frappe.db.sql(
        """
        SELECT DATE(creation) AS order_date, COUNT(*) AS order_count, SUM(total) AS revenue
        FROM `tabSimple Order`
        WHERE status = %s
        GROUP BY DATE(creation)
        ORDER BY order_date DESC
        """,
        ("Đã giao",),
        as_dict=True,
    )
    return columns, data
