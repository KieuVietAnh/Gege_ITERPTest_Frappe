from math import isfinite

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, get_datetime

from order_management.permissions import SALES, WAREHOUSE, can_access_order, is_admin
from order_management.stock import change_stock


class SimpleOrder(Document):
    def validate(self):
        previous = self.get_doc_before_save()
        if previous and previous.status in ("Đã giao", "Hủy"):
            frappe.throw(_("Đơn đã giao hoặc đã hủy không được sửa hay đổi trạng thái."))

        if self.is_new():
            self.status = "Mới"
            self.owner = frappe.session.user
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

        self.validate_actor(previous)
        if not self.item:
            frappe.throw(_("Mặt hàng là bắt buộc."), frappe.MandatoryError)
        item = frappe.db.get_value("Stock Item", self.item, ["item_name", "enabled"], as_dict=True)
        if not item or (not item.enabled and self.status != "Hủy"):
            frappe.throw(_("Hãy chọn mặt hàng đang sử dụng từ danh mục."))
        self.item_name = item.item_name if not previous or self.item != previous.item else previous.item_name
        if self.warehouse_user and (not previous or self.warehouse_user != previous.warehouse_user):
            user = frappe.db.get_value("User", self.warehouse_user, ["enabled", "user_type"], as_dict=True)
            if not user or not user.enabled or user.user_type != "System User" or WAREHOUSE not in frappe.get_roles(self.warehouse_user):
                frappe.throw(_("Người xử lý kho phải là tài khoản đang hoạt động có role Order Warehouse."))

    def validate_actor(self, previous):
        if is_admin():
            return
        roles = frappe.get_roles()
        if self.is_new():
            if SALES not in roles:
                frappe.throw(_("Chỉ Sale hoặc Admin được tạo đơn."), frappe.PermissionError)
            return
        # Frappe fetched this previous document FOR UPDATE before validation.
        if not previous or not can_access_order(previous):
            frappe.throw(_("Không có quyền thao tác đơn này."), frappe.PermissionError)
        if (self.owner != previous.owner or self.docstatus != previous.docstatus
                or get_datetime(self.creation) != get_datetime(previous.creation)):
            frappe.throw(_("Không được đổi người tạo, ngày tạo hoặc docstatus."), frappe.PermissionError)
        if self.status == "Đã giao":
            if WAREHOUSE not in roles or previous.warehouse_user != frappe.session.user:
                frappe.throw(_("Chỉ nhân viên kho được phân công mới được xác nhận Đã giao."), frappe.PermissionError)
            protected = ("customer_name", "item", "item_name", "quantity", "unit_price", "total", "warehouse_user")
            if any(self.get(field) != previous.get(field) for field in protected):
                frappe.throw(_("Kho chỉ được xác nhận Đã giao, không sửa nội dung đơn."), frappe.PermissionError)
        elif SALES not in roles or previous.owner != frappe.session.user:
            frappe.throw(_("Kho chỉ được xác nhận Đã giao."), frappe.PermissionError)

    def before_save(self):
        previous = self.get_doc_before_save()
        if previous and previous.status == "Mới" and self.status == "Đã giao":
            change_stock(self.item, -self.quantity)

    def on_trash(self):
        if self.status in ("Đã giao", "Hủy"):
            frappe.throw(_("Không được xóa đơn đã giao hoặc đã hủy."))
