from math import isfinite

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from order_management.stock import change_stock
from order_management.permissions import can_manage_stock


class StockReceipt(Document):
    def validate(self):
        if not can_manage_stock():
            frappe.throw(_("Chỉ Kho hoặc Admin được nhập kho."), frappe.PermissionError)
        if not self.is_new():
            frappe.throw(_("Phiếu đã nhập kho chỉ được xem, không được sửa."))
        self.quantity = flt(self.quantity, 3)
        if not isfinite(self.quantity) or self.quantity <= 0:
            frappe.throw(_("Số lượng nhập phải là số hữu hạn lớn hơn 0."))

    def before_save(self):
        self.balance_after = change_stock(self.item, self.quantity, self)

    def on_trash(self):
        frappe.throw(_("Không được xóa phiếu đã nhập kho."))
