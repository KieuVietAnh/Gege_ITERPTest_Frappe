import json
from unittest.mock import patch
from uuid import uuid4

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils.password import check_password, update_password

from order_management.demo import setup


class TestSeed(FrappeTestCase):
    def test_sql_seed_creates_and_replays_without_resetting_business_data(self):
        key = uuid4().hex[:10]
        sale, kho, code, order = f"seed-sale-{key}@example.com", f"seed-kho-{key}@example.com", f"SEED-{key}", f"SEED-ORD-{key}"
        records = [
            ("User", {"email": sale, "first_name": "Seed Sale", "role": "Order Sales", "password": "Seed@123456!"}),
            ("User", {"email": kho, "first_name": "Seed Kho", "role": "Order Warehouse", "password": "Seed@123456!"}),
            ("Stock Item", {"item_code": code, "item_name": "Seed item", "unit": "Cái", "default_unit_price": 100, "opening_stock": 20}),
            ("Simple Order", {"name": order, "sale": sale, "customer_name": "Seed buyer", "item": code, "quantity": 2, "unit_price": 100, "warehouse_user": kho}),
            ("Simple Order", {"name": order + "-delivered", "sale": sale, "customer_name": "Delivered buyer", "item": code, "quantity": 2, "unit_price": 100, "warehouse_user": kho, "status": "Đã giao"}),
            ("Simple Order", {"name": order + "-cancelled", "sale": sale, "customer_name": "Cancelled buyer", "item": code, "quantity": 1, "unit_price": 100, "warehouse_user": kho, "status": "Hủy"}),
        ]
        sql = " UNION ALL ".join(
            f"SELECT {frappe.db.escape(entity)} AS entity, {frappe.db.escape(json.dumps(data))} AS payload"
            for entity, data in records
        )
        with patch("order_management.demo.Path") as path:
            path.return_value.with_name.return_value.read_text.return_value = sql
            setup()
            self.assertEqual(frappe.db.get_value("Simple Order", order, "owner"), sale)
            self.assertEqual(check_password(sale, "Seed@123456!"), sale)
            self.assertEqual(frappe.db.get_value("Stock Item", code, "stock_qty"), 18)
            self.assertEqual(frappe.db.get_value("Simple Order", order + "-cancelled", "status"), "Hủy")
            self.assertEqual(frappe.db.get_value("Simple Order", order + "-delivered", "status"), "Đã giao")
            with self.set_user(sale):
                doc = frappe.get_doc("Simple Order", order)
                doc.status = "Hủy"
                doc.save()
            frappe.get_doc({"doctype": "Stock Receipt", "item": code, "quantity": 3}).insert()
            update_password(sale, "Changed@123456!")
            setup()
            self.assertEqual(check_password(sale, "Changed@123456!"), sale)
            self.assertEqual(frappe.db.get_value("Simple Order", order, "status"), "Hủy")
            self.assertEqual(frappe.db.get_value("Stock Item", code, "stock_qty"), 21)
            self.assertEqual(frappe.db.count("Stock Movement", {"item": code, "movement_type": "Xuất"}), 1)
            self.assertEqual(frappe.db.count("Stock Movement", {"item": code, "movement_type": "Nhập"}), 2)
            self.assertEqual(frappe.db.count("Stock Receipt", {"item": code}), 2)
            self.assertEqual(frappe.db.count("Simple Order", {"name": order}), 1)

    def test_seed_rejects_non_admin(self):
        with self.set_user("Guest"):
            with self.assertRaises(frappe.PermissionError):
                setup()
