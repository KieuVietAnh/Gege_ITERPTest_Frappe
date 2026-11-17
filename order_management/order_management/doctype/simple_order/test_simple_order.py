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
