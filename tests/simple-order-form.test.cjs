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
            session: { user: "Administrator" },
            user: { has_role: () => false },
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
        for (const field of ["customer_name", "item", "quantity", "unit_price", "warehouse_user"]) {
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

    for (const [user, role, owner, assigned, deliver, cancel, editable] of [
        ["sale1@example.com", "Order Sales", "sale1@example.com", "kho1@example.com", false, true, true],
        ["kho1@example.com", "Order Warehouse", "sale1@example.com", "kho1@example.com", true, false, false],
        ["sale2@example.com", "Order Sales", "sale1@example.com", "kho1@example.com", false, false, false],
    ]) {
        context.frappe.session.user = user;
        context.frappe.user.has_role = value => value === role;
        const buttons = {}, properties = {};
        const frm = {
            doc: { status: "Mới", owner, warehouse_user: assigned }, perm: [{ write: 1 }], is_new: () => false,
            set_df_property(field, prop, value) { properties[field] = value; },
            enable_save() {}, disable_save() {}, set_intro() {}, page: { clear_primary_action() {} },
            add_custom_button(label, action) { buttons[label] = action; },
        };
        events.refresh(frm);
        assert.equal(typeof buttons["Đã giao"] === "function", deliver);
        assert.equal(typeof buttons["Hủy"] === "function", cancel);
        assert.equal(buttons["Doanh thu theo ngày"], undefined);
        assert.equal(properties.unit_price, editable ? 0 : 1);
    }

    const pending = [];
    context.frappe.db = { get_value: () => new Promise(resolve => pending.push(resolve)) };
    const selected = {
        doc: { item: "OLD" },
        set_value(field, value) { this.doc[field] = value; return Promise.resolve(); },
    };
    const first = events.item(selected);
    selected.doc.item = "NEW";
    const second = events.item(selected);
    pending[1]({ message: { item_name: "New item", default_unit_price: 200 } });
    await second;
    pending[0]({ message: { item_name: "Old item", default_unit_price: 100 } });
    await first;
    assert.equal(selected.doc.unit_price, 200, "slow item lookup cannot overwrite newer selection");
});
