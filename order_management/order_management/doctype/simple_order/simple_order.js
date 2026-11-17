frappe.ui.form.on("Simple Order", {
    setup(frm) {
        frm.set_query("item", () => ({ filters: { enabled: 1 } }));
        frm.set_query("warehouse_user", () => ({ query: "order_management.permissions.warehouse_users" }));
    },
    refresh(frm) {
        const admin = frappe.session.user === "Administrator";
        const sale = frappe.user.has_role("Order Sales") && (frm.is_new() || frm.doc.owner === frappe.session.user);
        const warehouse = frappe.user.has_role("Order Warehouse") && frm.doc.warehouse_user === frappe.session.user;
        const closed = ["Đã giao", "Hủy"].includes(frm.doc.status);
        for (const field of ["customer_name", "item", "quantity", "unit_price", "warehouse_user"]) {
            frm.set_df_property(field, "read_only", !closed && (admin || sale) ? 0 : 1);
        }
        if (closed) {
            frm.disable_save();
            frm.set_intro("Đơn đã kết thúc, chỉ được xem.", "blue");
        } else {
            frm.enable_save();
            if (!admin && !sale) {
                frm.page.clear_primary_action();
                frm.set_intro("Kho: kiểm tra hàng và xác nhận Đã giao; không sửa nội dung đơn.", "blue");
            }
            if (!frm.is_new() && frm.perm[0].write) {
                if (admin || warehouse) frm.add_custom_button("Đã giao", () => change_status(frm, "Đã giao"));
                if (admin || sale) frm.add_custom_button("Hủy", () => change_status(frm, "Hủy"));
            }
        }
        if (admin) {
            frm.add_custom_button("Doanh thu theo ngày", () => frappe.set_route("query-report", "Daily Revenue"));
        }
    },

    async item(frm) {
        if (!frm.doc.item) return;
        const selected = frm.doc.item;
        const result = await frappe.db.get_value("Stock Item", selected, ["item_name", "default_unit_price"]);
        if (frm.doc.item !== selected) return;
        await frm.set_value("item_name", result.message.item_name);
        await frm.set_value("unit_price", result.message.default_unit_price);
    },

    quantity(frm) {
        return update_total_preview(frm);
    },

    unit_price(frm) {
        return update_total_preview(frm);
    },
});

function change_status(frm, status) {
    frappe.confirm(`Chuyển đơn sang "${status}"? Sau khi lưu sẽ không sửa được nữa.`, async () => {
        const previous_status = frm.doc.status;
        try {
            await frm.set_value("status", status);
            await frm.save();
        } catch (error) {
            await frm.set_value("status", previous_status);
        }
    });
}

function update_total_preview(frm) {
    const quantity = flt(frm.doc.quantity, 3);
    const unit_price = flt(frm.doc.unit_price, 2);
    return frm.set_value("total", flt(quantity * unit_price, 2));
}
