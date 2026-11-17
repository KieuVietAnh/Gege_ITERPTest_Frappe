frappe.ui.form.on("Simple Order", {
    refresh(frm) {
        const closed = ["Đã giao", "Hủy"].includes(frm.doc.status);
        for (const field of ["customer_name", "item_name", "quantity", "unit_price"]) {
            frm.set_df_property(field, "read_only", closed ? 1 : 0);
        }
        if (closed) {
            frm.disable_save();
            frm.set_intro("Đơn đã kết thúc, chỉ được xem.", "blue");
        } else {
            frm.enable_save();
            if (!frm.is_new() && frm.perm[0].write) {
                frm.add_custom_button("Đã giao", () => change_status(frm, "Đã giao"));
                frm.add_custom_button("Hủy", () => change_status(frm, "Hủy"));
            }
        }
        frm.add_custom_button("Doanh thu theo ngày", () => {
            frappe.set_route("query-report", "Daily Revenue");
        });
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
