from datetime import date

import frappe
from frappe.tests.utils import FrappeTestCase

from order_management.order_management.report.daily_revenue.daily_revenue import execute
from order_management.test_utils import make_item


class TestDailyRevenue(FrappeTestCase):
    def test_only_delivered_orders_are_grouped_by_creation_day(self):
        for creation, quantity, unit_price, status in (
            ("2001-01-01 08:00:00", 2, 100, "Đã giao"),
            ("2001-01-01 23:59:59", 3, 100, "Đã giao"),
            ("2001-01-02 00:00:00", 1, 75, "Đã giao"),
            ("2001-01-01 12:00:00", 1, 9999, "Mới"),
            ("2001-01-01 13:00:00", 1, 8888, "Hủy"),
            ("2001-01-03 13:00:00", 1, 8888, "Hủy"),
        ):
            order = frappe.get_doc({
                "doctype": "Simple Order", "customer_name": "Report test", "item": make_item().name,
                "quantity": quantity, "unit_price": unit_price,
            }).insert()
            if status != "Mới":
                order.status = status
                order.save()
            frappe.db.set_value("Simple Order", order.name, "creation", creation, update_modified=False)

        columns, data = execute()
        rows = {row.order_date: row for row in data}
        self.assertEqual(len(columns), 3)
        self.assertEqual(rows[date(2001, 1, 1)].order_count, 2)
        self.assertEqual(rows[date(2001, 1, 1)].revenue, 500)
        self.assertEqual(rows[date(2001, 1, 2)].order_count, 1)
        self.assertEqual(rows[date(2001, 1, 2)].revenue, 75)
        self.assertNotIn(date(2001, 1, 3), rows)

    def test_report_rejects_guests(self):
        with self.set_user("Guest"):
            with self.assertRaises(frappe.PermissionError):
                execute()
