from math import isfinite

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class SimpleOrder(Document):
    def validate(self):
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

        # shortcut: only new orders are supported; add transitions in the next lesson.
        self.status = "Mới"
