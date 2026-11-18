from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import frappe
from frappe.tests.utils import FrappeTestCase

from order_management.test_utils import make_item


class TestStockConcurrency(FrappeTestCase):
    def race(self, names):
        site, sites_path = frappe.local.site, frappe.local.sites_path
        barrier = Barrier(2)

        def deliver(name):
            frappe.init(site=site, sites_path=sites_path)
            frappe.connect()
            frappe.set_user("Administrator")
            try:
                order = frappe.get_doc("Simple Order", name)
                barrier.wait(timeout=15)
                order.status = "Đã giao"
                order.save()
                frappe.db.commit()
                return "ok"
            except (frappe.ValidationError, frappe.TimestampMismatchError) as error:
                frappe.db.rollback()
                return type(error).__name__
            finally:
                frappe.destroy()

        with ThreadPoolExecutor(max_workers=2) as pool:
            return list(pool.map(deliver, names))

    def run_stock_race(self, same_order):
        item = make_item(stock=1)
        orders = [frappe.get_doc({
            "doctype": "Simple Order", "customer_name": "Race test", "item": item.name,
            "quantity": 1, "unit_price": 100,
        }).insert() for _ in range(1 if same_order else 2)]
        names = [order.name for order in orders]
        receipts = frappe.get_all("Stock Receipt", filters={"item": item.name}, pluck="name")
        # Independent database connections need committed fixtures; remove only these fixtures below.
        frappe.db.commit()
        try:
            results = self.race([names[0], names[0]] if same_order else names)
            self.assertEqual(results.count("ok"), 1, results)
            frappe.db.rollback()
            self.assertEqual(frappe.db.get_value("Stock Item", item.name, "stock_qty"), 0)
            statuses = [frappe.db.get_value("Simple Order", name, "status") for name in names]
            self.assertEqual(statuses.count("Đã giao"), 1)
            self.assertEqual(frappe.db.count("Stock Movement", {"item": item.name, "movement_type": "Xuất"}), 1)
            if not same_order:
                self.assertEqual(statuses.count("Mới"), 1)
        finally:
            frappe.db.rollback()
            frappe.db.delete("Stock Movement", {"item": item.name})
            for name in names:
                frappe.db.delete("Version", {"ref_doctype": "Simple Order", "docname": name})
                frappe.db.delete("Simple Order", {"name": name})
            for name in receipts:
                frappe.db.delete("Stock Receipt", {"name": name})
            frappe.db.delete("Stock Item", {"name": item.name})
            frappe.db.commit()

    def test_two_orders_cannot_oversell_last_item(self):
        self.run_stock_race(same_order=False)

    def test_two_confirmations_deduct_stock_once(self):
        self.run_stock_race(same_order=True)
