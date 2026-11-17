import frappe
from frappe.tests.utils import FrappeTestCase


class TestSimpleOrder(FrappeTestCase):
    def make_order(self, **values):
        return frappe.get_doc(
            {
                "doctype": "Simple Order",
                "customer_name": "Khách thử nghiệm",
                "item_name": "Bàn phím",
                "quantity": 2,
                "unit_price": 150000,
                **values,
            }
        )

    def test_server_calculates_total_and_sets_initial_status(self):
        order = self.make_order(total=1, status="Đã giao").insert()

        order.reload()
        self.assertEqual(order.total, 300000)
        self.assertEqual(order.status, "Mới")

    def test_total_changes_when_order_is_edited(self):
        order = self.make_order().insert()
        order.quantity = 3
        order.total = 1
        order.save()

        order.reload()
        self.assertEqual(order.total, 450000)

    def test_fractional_quantity(self):
        order = self.make_order(quantity=1.5, unit_price=10.25).insert()
        self.assertEqual(order.total, 15.38)

    def test_rejects_nonpositive_numbers(self):
        for field in ("quantity", "unit_price"):
            for value in (0, -1):
                with self.subTest(field=field, value=value):
                    with self.assertRaises(frappe.ValidationError):
                        self.make_order(**{field: value}).insert()

    def test_rejects_nonfinite_numbers(self):
        for field in ("quantity", "unit_price"):
            for value in (float("nan"), float("inf"), float("-inf")):
                with self.subTest(field=field, value=value):
                    with self.assertRaises(frappe.ValidationError):
                        self.make_order(**{field: value}).validate()

    def test_requires_customer_and_item(self):
        for field in ("customer_name", "item_name"):
            with self.subTest(field=field):
                with self.assertRaises(frappe.MandatoryError):
                    self.make_order(**{field: ""}).insert()

    def test_rejects_total_overflow(self):
        with self.assertRaises(frappe.ValidationError):
            self.make_order(quantity=1e200, unit_price=1e200).validate()

    def test_new_orders_can_be_delivered_or_cancelled(self):
        for status in ("Đã giao", "Hủy"):
            with self.subTest(status=status):
                order = self.make_order().insert()
                order.status = status
                order.save()
                order.reload()
                self.assertEqual(order.status, status)

    def test_closed_orders_reject_edits_and_status_changes(self):
        for status in ("Đã giao", "Hủy"):
            order = self.make_order().insert()
            order.status = status
            order.save()
            for field, value in (
                ("customer_name", "Changed customer"), ("item_name", "Changed item"),
                ("quantity", 3), ("unit_price", 1), ("total", 1),
                ("status", "Mới"), ("status", "Hủy" if status == "Đã giao" else "Đã giao"),
            ):
                with self.subTest(status=status, field=field):
                    changed = frappe.get_doc("Simple Order", order.name)
                    changed.set(field, value)
                    with self.assertRaises(frappe.ValidationError):
                        changed.save()
            order.reload()
            self.assertEqual(order.status, status)
            self.assertEqual(order.total, 300000)

    def test_rejects_unknown_status(self):
        order = self.make_order().insert()
        order.status = "Unknown"
        with self.assertRaises(frappe.ValidationError):
            order.save()

    def test_stale_save_cannot_reopen_a_delivered_order(self):
        order = self.make_order().insert()
        stale = frappe.get_doc("Simple Order", order.name)
        order.status = "Đã giao"
        order.save()
        stale.quantity = 3
        with self.assertRaises(frappe.TimestampMismatchError):
            stale.save()

    def test_closed_orders_cannot_be_deleted(self):
        for status in ("Đã giao", "Hủy"):
            order = self.make_order().insert()
            order.status = status
            order.save()
            with self.assertRaises(frappe.ValidationError):
                order.delete()
            self.assertTrue(frappe.db.exists("Simple Order", order.name))
