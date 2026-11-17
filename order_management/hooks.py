app_name = "order_management"
app_title = "Order Management"
app_publisher = "ERP Test"
app_description = "A small Frappe app for learning order management."
app_email = "dev@example.com"

before_install = "order_management.setup.ensure_roles"
before_migrate = "order_management.setup.ensure_roles"
after_install = "order_management.demo.setup"
after_migrate = "order_management.demo.setup"

permission_query_conditions = {
    "Simple Order": "order_management.permissions.order_query",
}
has_permission = {
    "Simple Order": "order_management.permissions.order_permission",
}
doc_events = {"DocShare": {"validate": "order_management.permissions.prevent_order_sharing"}}
