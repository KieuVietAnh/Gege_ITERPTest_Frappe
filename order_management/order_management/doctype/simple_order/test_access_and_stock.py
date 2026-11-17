from uuid import uuid4

import frappe
from frappe.tests.utils import FrappeTestCase

from order_management.order_management.report.daily_revenue.daily_revenue import execute
from order_management.permissions import SALES, WAREHOUSE
from order_management.test_utils import make_item


class TestAccessAndStock(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        self.item = make_item(stock=5)
        self.sale1 = self.make_user(SALES)
        self.sale2 = self.make_user(SALES)
        self.kho1 = self.make_user(WAREHOUSE)
        self.kho2 = self.make_user(WAREHOUSE)
        self.manager = self.make_user("System Manager")

    def tearDown(self):
        frappe.set_user("Administrator")
        super().tearDown()

    def make_user(self, role):
        email = f"test-{uuid4().hex[:12]}@example.com"
        frappe.get_doc({
            "doctype": "User", "email": email, "first_name": "Access test",
            "user_type": "System User", "send_welcome_email": 0, "roles": [{"role": role}],
        }).insert()
        return email

    def order(self, user=None, warehouse=None, quantity=2):
        with self.set_user(user or self.sale1):
            return frappe.get_doc({
                "doctype": "Simple Order", "customer_name": "Access test", "item": self.item.name,
                "quantity": quantity, "unit_price": 150000, "warehouse_user": warehouse or self.kho1,
            }).insert()

    def names(self, user):
        with self.set_user(user):
            return frappe.get_list("Simple Order", pluck="name", limit_page_length=1000)

    def test_lists_and_direct_reads_are_scoped(self):
        first = self.order()
        second = self.order(self.sale2, self.kho2)
        for user, visible, hidden in (
            (self.sale1, first, second), (self.sale2, second, first),
            (self.kho1, first, second), (self.kho2, second, first),
        ):
            self.assertIn(visible.name, self.names(user))
            self.assertNotIn(hidden.name, self.names(user))
            with self.set_user(user):
                visible.check_permission("read")
                with self.assertRaises(frappe.PermissionError):
                    hidden.check_permission("read")
        self.assertIn(first.name, self.names("Administrator"))
        self.assertIn(second.name, self.names("Administrator"))
        with self.set_user(self.manager):
            with self.assertRaises(frappe.PermissionError):
                first.check_permission("read")

    def test_sale_can_edit_cancel_but_cannot_deliver_or_change_owner(self):
        order = self.order()
        with self.set_user(self.sale1):
            order.quantity = 3
            order.save()
            for changes in ({"status": "Đã giao"}, {"owner": self.sale2}, {"creation": "2000-01-01 00:00:00"}):
                attempt = frappe.get_doc("Simple Order", order.name).update(changes)
                with self.assertRaises(frappe.PermissionError):
                    attempt.save()
            order.reload()
            order.status = "Hủy"
            order.save()
        self.assertEqual(frappe.db.get_value("Stock Item", self.item.name, "stock_qty"), 5)

    def test_sale_cannot_forge_creator_or_initial_status(self):
        with self.set_user(self.sale1):
            order = frappe.get_doc({
                "doctype": "Simple Order", "owner": self.sale2, "status": "Đã giao",
                "customer_name": "Creator test", "item": self.item.name,
                "quantity": 1, "unit_price": 100,
            }).insert()
        self.assertEqual(order.owner, self.sale1)
        self.assertEqual(order.status, "Mới")
        self.assertEqual(frappe.db.get_value("Stock Item", self.item.name, "stock_qty"), 5)

    def test_warehouse_only_confirms_assigned_order_without_changing_data(self):
        order = self.order()
        with self.set_user(self.kho1):
            for changes in (
                {"status": "Hủy"}, {"status": "Đã giao", "unit_price": 1},
                {"status": "Đã giao", "quantity": 1}, {"status": "Đã giao", "warehouse_user": self.kho2},
            ):
                attempt = frappe.get_doc("Simple Order", order.name).update(changes)
                with self.assertRaises(frappe.PermissionError):
                    attempt.save()
            order.reload()
            order.status = "Đã giao"
            order.save()
            with self.assertRaises(frappe.ValidationError):
                order.save()
        self.assertEqual(frappe.db.get_value("Stock Item", self.item.name, "stock_qty"), 3)

    def test_forging_assignee_cannot_steal_order(self):
        order = self.order()
        with self.set_user(self.kho2):
            order.warehouse_user = self.kho2
            order.status = "Đã giao"
            with self.assertRaises(frappe.PermissionError):
                order.save()
        with self.set_user(self.sale2):
            order.owner = self.sale2
            with self.assertRaises(frappe.PermissionError):
                order.save()

    def test_reassignment_revokes_old_warehouse_access(self):
        order = self.order()
        stale = frappe.get_doc("Simple Order", order.name)
        with self.set_user(self.sale1):
            order.warehouse_user = self.kho2
            order.save()
        self.assertNotIn(order.name, self.names(self.kho1))
        self.assertIn(order.name, self.names(self.kho2))
        with self.set_user(self.kho1):
            stale.status = "Đã giao"
            with self.assertRaises(frappe.PermissionError):
                stale.save()

    def test_reports_and_sharing_are_admin_only(self):
        order = self.order()
        for user in (self.sale1, self.kho1, self.manager, "Guest"):
            with self.set_user(user):
                with self.assertRaises(frappe.PermissionError):
                    execute()
        with self.assertRaises(frappe.PermissionError):
            frappe.share.add("Simple Order", order.name, self.sale2, read=1)

    def test_invalid_assignee_and_missing_stock_are_rejected(self):
        with self.assertRaises(frappe.ValidationError):
            self.order(warehouse=self.sale2)
        order = self.order(quantity=6)
        with self.set_user(self.kho1):
            order.status = "Đã giao"
            with self.assertRaises(frappe.ValidationError):
                order.save()
        self.assertEqual(frappe.db.get_value("Simple Order", order.name, "status"), "Mới")
        self.assertEqual(frappe.db.get_value("Stock Item", self.item.name, "stock_qty"), 5)

    def test_catalog_and_receipt_permissions_and_immutability(self):
        with self.set_user(self.sale1):
            self.item.check_permission("read")
            with self.assertRaises(frappe.PermissionError):
                frappe.get_doc({"doctype": "Stock Receipt", "item": self.item.name, "quantity": 2}).insert()
            with self.assertRaises(frappe.PermissionError):
                self.item.default_unit_price = 1
                self.item.save()
        with self.set_user(self.kho1):
            receipt = frappe.get_doc({"doctype": "Stock Receipt", "item": self.item.name, "quantity": 2}).insert()
            self.assertEqual(receipt.balance_after, 7)
            item = frappe.get_doc("Stock Item", self.item.name)
            for balance in (999, 7.0001, float("nan")):
                item.stock_qty = balance
                with self.assertRaises(frappe.ValidationError):
                    item.save()
            with self.assertRaises(frappe.ValidationError):
                receipt.save()
        with self.assertRaises(frappe.ValidationError):
            receipt.save()
        with self.assertRaises(frappe.ValidationError):
            receipt.delete()
        self.assertEqual(frappe.db.get_value("Stock Item", self.item.name, "stock_qty"), 7)

    def test_invalid_receipt_quantities_and_item_prices(self):
        for quantity in (0, -1, float("nan"), float("inf")):
            with self.assertRaises(frappe.ValidationError):
                frappe.get_doc({"doctype": "Stock Receipt", "item": self.item.name, "quantity": quantity}).insert()
        for price in (-1, float("inf"), float("nan")):
            self.item.reload()
            self.item.default_unit_price = price
            with self.assertRaises(frappe.ValidationError):
                self.item.save()

    def test_delivery_and_stock_roll_back_together(self):
        order = self.order()
        frappe.db.savepoint("before_delivery")
        with self.set_user(self.kho1):
            order.status = "Đã giao"
            order.save()
        frappe.db.rollback(save_point="before_delivery")
        self.assertEqual(frappe.db.get_value("Simple Order", order.name, "status"), "Mới")
        self.assertEqual(frappe.db.get_value("Stock Item", self.item.name, "stock_qty"), 5)
