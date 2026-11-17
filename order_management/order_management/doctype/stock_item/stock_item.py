from math import isfinite

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from order_management.permissions import can_manage_stock


class StockItem(Document):
    def validate(self):
        if not can_manage_stock():
            frappe.throw(_("Chỉ Kho hoặc Admin được quản lý mặt hàng."), frappe.PermissionError)
        previous = self.get_doc_before_save()
        if self.is_new():
            self.stock_qty = 0
        elif previous and (not isfinite(flt(self.stock_qty)) or flt(self.stock_qty) != flt(previous.stock_qty)):
            frappe.throw(_("Không sửa trực tiếp tồn kho; hãy lập phiếu nhập hoặc xuất qua đơn hàng."))
        self.default_unit_price = flt(self.default_unit_price)
        if not isfinite(self.default_unit_price) or self.default_unit_price < 0:
            frappe.throw(_("Giá bán mặc định phải là số hữu hạn không âm."))
        self.default_unit_price = flt(self.default_unit_price, 2)

    def on_trash(self):
        frappe.throw(_("Hãy bỏ chọn Đang sử dụng thay vì xóa mặt hàng."))
