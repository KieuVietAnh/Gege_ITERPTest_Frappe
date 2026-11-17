frappe.ui.form.on("Stock Receipt", {
    setup(frm) {
        frm.set_query("item", () => ({ filters: { enabled: 1 } }));
    },
    refresh(frm) {
        if (!frm.is_new()) {
            for (const field of ["item", "quantity", "note"]) {
                frm.set_df_property(field, "read_only", 1);
            }
            frm.disable_save();
            frm.set_intro("Phiếu đã nhập kho, chỉ được xem.", "blue");
        }
    },
});
