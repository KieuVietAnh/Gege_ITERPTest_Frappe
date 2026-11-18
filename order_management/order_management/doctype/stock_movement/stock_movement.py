import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


# An object identity cannot be supplied through the JSON API, even by Administrator.
STOCK_WRITE = object()


class StockMovement(Document):
    def autoname(self):
        self.name = make_autoname("IN-LOG-.#####" if self.movement_type == "Nhập" else "OUT-.#####")

    def validate(self):
        if not self.is_new() or self.flags.stock_write is not STOCK_WRITE:
            frappe.throw("Lịch sử kho chỉ được tạo tự động từ nhập kho hoặc giao đơn, không được sửa.")

    def on_trash(self):
        frappe.throw("Không được xóa lịch sử kho.")
