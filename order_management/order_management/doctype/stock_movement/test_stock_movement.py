from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from order_management.stock import change_stock
from order_management.test_utils import make_item


class TestStockMovement(FrappeTestCase):
    def test_receipt_delivery_and_closed_order_audit(self):
        item = make_item(stock=5)
        incoming = frappe.get_last_doc("Stock Movement", filters={"item": item.name})
        self.assertEqual((incoming.movement_type, incoming.quantity, incoming.balance_before, incoming.balance_after), ("Nhập", 5, 0, 5))
        self.assertTrue(frappe.db.exists("Stock Receipt", incoming.source_name))
        order = frappe.get_doc({"doctype": "Simple Order", "customer_name": "Audit buyer",
                               "item": item.name, "quantity": 2, "unit_price": 100}).insert()
        self.assertEqual(frappe.db.count("Stock Movement", {"item": item.name}), 1)
        order.status = "Đã giao"
        order.save()
        outgoing = frappe.get_last_doc("Stock Movement", filters={"item": item.name, "movement_type": "Xuất"})
        self.assertEqual((outgoing.quantity, outgoing.balance_before, outgoing.balance_after), (2, 5, 3))
        self.assertEqual(outgoing.source_name, order.name)
        self.assertEqual(outgoing.performed_by, "Administrator")
        self.assertTrue(outgoing.name.startswith("OUT-"))
        for operation in (outgoing.save, outgoing.delete, order.save):
            with self.assertRaises(frappe.ValidationError):
                operation()
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc({"doctype": "Stock Movement", "source_key": "forged", "flags": {"stock_write": True}}).insert(ignore_permissions=True)
        self.assertEqual(frappe.db.count("Stock Movement", {"source_name": order.name}), 1)
        self.assertEqual(frappe.db.get_value("Stock Item", item.name, "stock_qty"), 3)

    def test_unique_source_and_transaction_rollback(self):
        item = make_item(stock=5)
        order = frappe.get_doc({"doctype": "Simple Order", "customer_name": "Rollback buyer",
                               "item": item.name, "quantity": 2, "unit_price": 100}).insert()
        frappe.db.savepoint("audit_failure")
        with patch("order_management.order_management.doctype.stock_movement.stock_movement.StockMovement.before_insert",
                   side_effect=frappe.ValidationError("Audit write failed"), create=True):
            order.status = "Đã giao"
            with self.assertRaises(frappe.ValidationError):
                order.save()
        frappe.db.rollback(save_point="audit_failure")
        self.assertEqual(frappe.db.get_value("Stock Item", item.name, "stock_qty"), 5)
        self.assertEqual(frappe.db.get_value("Simple Order", order.name, "status"), "Mới")
        self.assertEqual(frappe.db.count("Stock Movement", {"source_name": order.name}), 0)
        order.reload()
        order.status = "Đã giao"
        order.save()
        frappe.db.savepoint("duplicate_audit")
        with self.assertRaises((frappe.DuplicateEntryError, frappe.UniqueValidationError)):
            change_stock(item.name, -2, order)
        frappe.db.rollback(save_point="duplicate_audit")
        self.assertEqual(frappe.db.get_value("Stock Item", item.name, "stock_qty"), 3)

    def test_cancel_does_not_create_outgoing_movement(self):
        item = make_item(stock=5)
        order = frappe.get_doc({"doctype": "Simple Order", "customer_name": "Cancel buyer",
                               "item": item.name, "quantity": 2, "unit_price": 100}).insert()
        order.status = "Hủy"
        order.save()
        self.assertEqual(frappe.db.count("Stock Movement", {"source_name": order.name}), 0)
        self.assertEqual(frappe.db.get_value("Stock Item", item.name, "stock_qty"), 5)
