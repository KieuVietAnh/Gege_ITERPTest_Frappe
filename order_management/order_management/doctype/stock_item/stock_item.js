frappe.ui.form.on("Stock Item", {
    refresh(frm) {
        if (!frm.is_new() && (frappe.session.user === "Administrator" || frappe.user.has_role("Order Warehouse"))) {
            frm.add_custom_button("Nhập kho", () => frappe.new_doc("Stock Receipt", { item: frm.doc.name }));
        }
    },
});
