const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

test("field edits update the preview using Frappe's number helpers", async () => {
    let events;
    const context = vm.createContext({
        window: {},
        cint: (value) => parseInt(value, 10) || 0,
        frappe: {
            boot: { sysdefaults: { rounding_method: "Banker's Rounding", number_format: "#,###.##" } },
            ui: { form: { on(doctype, handlers) {
                assert.equal(doctype, "Simple Order");
                events = handlers;
            } } },
        },
    });
    // Run from frappe-bench so the test uses the installed framework's rounding.
    const numberFormat = readFileSync("apps/frappe/frappe/public/js/frappe/utils/number_format.js", "utf8")
        .replace(/^import "\.\/datatype";\r?\n/m, "");
    vm.runInContext(numberFormat, context);
    const script = path.join(__dirname, "../order_management/order_management/doctype/simple_order/simple_order.js");
    vm.runInContext(readFileSync(script, "utf8"), context);

    for (const event of ["quantity", "unit_price"]) {
        for (const [quantity, unit_price, expected] of [
            [2, 150000, 300000],
            [3, 150000, 450000],
            [1.5, 10.25, 15.38],
            [1, 1.245, 1.24],
            [null, 150000, 0],
            [2, null, 0],
        ]) {
            const frm = {
                doc: { quantity, unit_price, total: 999 },
                set_value(field, value) {
                    assert.equal(field, "total");
                    this.doc[field] = value;
                    return Promise.resolve();
                },
            };
            await events[event](frm);
            assert.equal(frm.doc.total, expected, `${event}: ${quantity} x ${unit_price}`);
            assert.equal(frm.doc.quantity, quantity);
            assert.equal(frm.doc.unit_price, unit_price);
        }
    }

    for (const status of ["Mới", "Đã giao", "Hủy"]) {
        const buttons = {};
        const properties = {};
        let saveEnabled;
        const frm = {
            doc: { status }, perm: [{ write: 1 }], is_new: () => false,
            set_df_property(field, property, value) { properties[field] = value; },
            enable_save() { saveEnabled = true; },
            disable_save() { saveEnabled = false; },
            set_intro() {},
            add_custom_button(label, action) { buttons[label] = action; },
        };
        events.refresh(frm);
        const closed = status !== "Mới";
        assert.equal(saveEnabled, !closed);
        for (const field of ["customer_name", "item_name", "quantity", "unit_price"]) {
            assert.equal(properties[field], closed ? 1 : 0);
        }
        assert.equal(typeof buttons["Đã giao"], closed ? "undefined" : "function");
        assert.equal(typeof buttons["Hủy"], closed ? "undefined" : "function");
        assert.equal(typeof buttons["Doanh thu theo ngày"], "function");
        if (!closed) {
            let confirm;
            context.frappe.confirm = (message, yes) => { confirm = yes; };
            frm.set_value = async (field, value) => { frm.doc[field] = value; };
            frm.save = async () => { throw new Error("Server rejected the save"); };
            buttons["Đã giao"]();
            await confirm();
            assert.equal(frm.doc.status, "Mới", "failed save restores the previous status");
            frm.save = async () => {};
            buttons["Hủy"]();
            await confirm();
            assert.equal(frm.doc.status, "Hủy");
        }
    }
});
