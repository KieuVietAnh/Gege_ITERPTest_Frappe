frappe.listview_settings["Simple Order"] = {
    add_fields: ["status"],

    onload(listview) {
        listview.page.add_inner_button("Doanh thu theo ngày", () => {
            frappe.set_route("query-report", "Daily Revenue");
        });
    },

    get_indicator(doc) {
        const colors = { "Mới": "blue", "Đã giao": "green", "Hủy": "red" };
        return [doc.status, colors[doc.status], `status,=,${doc.status}`];
    },
};
