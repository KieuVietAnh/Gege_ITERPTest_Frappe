from math import isfinite

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class SimpleOrder(Document):
    def validate(self):
        previous = self.get_doc_before_save()
        if previous and previous.status in ("Đã giao", "Hủy"):
            frappe.throw(_("Đơn đã giao hoặc đã hủy không được sửa hay đổi trạng thái."))

        if self.is_new():
            self.status = "Mới"
        elif self.status not in ("Mới", "Đã giao", "Hủy"):
            frappe.throw(_("Trạng thái đơn hàng không hợp lệ."))

        self.quantity = flt(self.quantity, 3)
        self.unit_price = flt(self.unit_price, 2)

        if not isfinite(self.quantity) or self.quantity <= 0:
            frappe.throw(_("Số lượng phải là số hữu hạn lớn hơn 0."))

        if not isfinite(self.unit_price) or self.unit_price <= 0:
            frappe.throw(_("Đơn giá phải là số hữu hạn lớn hơn 0."))

        total = self.quantity * self.unit_price
        if not isfinite(total):
            frappe.throw(_("Thành tiền vượt quá phạm vi cho phép."))
        self.total = flt(total, 2)

    def on_trash(self):
        if self.status in ("Đã giao", "Hủy"):
            frappe.throw(_("Không được xóa đơn đã giao hoặc đã hủy."))
