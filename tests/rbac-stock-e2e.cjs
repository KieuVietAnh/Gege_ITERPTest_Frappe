const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

(async () => {
    const browser = await chromium.launch({ headless: true });
    const baseURL = process.env.FRAPPE_TEST_URL || "http://127.0.0.1:8080";
    const shots = path.join(__dirname, "../docs/screenshots");
    const pages = [];
    fs.mkdirSync(shots, { recursive: true });
    try {
        async function session(user, password) {
            const context = await browser.newContext({ baseURL, viewport: { width: 1440, height: 1000 } });
            const login = await context.request.post("/api/method/login", { form: { usr: user, pwd: password } });
            assert.equal(login.status(), 200, await login.text());
            const page = await context.newPage();
            page.setDefaultTimeout(30000);
            pages.push(page);
            await page.goto("/app/stock-item");
            await page.waitForFunction(() => window.frappe?.csrf_token);
            const csrf = await page.evaluate(() => frappe.csrf_token);
            return {
                context, page,
                request(method, route, data) {
                    return context.request[method](route, { data, headers: { "X-Frappe-CSRF-Token": csrf } });
                },
            };
        }
        const admin = await session("Administrator", process.env.FRAPPE_TEST_PASSWORD || "admin");
        const sale1 = await session("sale1@example.com", "SaleDemo@12345!");
        const sale2 = await session("sale2@example.com", "SaleDemo@12345!");
        const kho1 = await session("kho1@example.com", "KhoDemo@12345!");
        const kho2 = await session("kho2@example.com", "KhoDemo@12345!");
        await sale1.page.goto("/app/order-management");
        await sale1.page.getByText("Đơn hàng và kho", { exact: true }).waitFor({ state: "visible" });
        await sale1.page.goto("/app/stock-item");
        const docURL = (type, name) => `/api/resource/${encodeURIComponent(type)}${name ? "/" + encodeURIComponent(name) : ""}`;
        async function create(actor, type, data) {
            const response = await actor.request("post", docURL(type), data);
            assert.equal(response.status(), 200, await response.text());
            return (await response.json()).data;
        }
        async function read(actor, type, name) {
            const response = await actor.context.request.get(docURL(type, name));
            assert.equal(response.status(), 200, await response.text());
            return (await response.json()).data;
        }
        async function denied(actor, method, route, data) {
            const response = await actor.request(method, route, data);
            assert.equal(response.status(), 403, await response.text());
        }
        async function save(page) {
            await page.locator(".page-head .primary-action:visible").click();
            await page.waitForFunction(() => cur_frm && !cur_frm.is_new() && !cur_frm.is_dirty());
        }
        const code = `E2E-${Date.now()}`;
        await kho1.page.locator(".page-head .primary-action:visible").click();
        await kho1.page.locator('input[data-fieldname="item_code"]:visible').fill(code);
        await kho1.page.locator('input[data-fieldname="item_name"]:visible').fill("Hàng thử Sale - Kho");
        await kho1.page.locator('input[data-fieldname="default_unit_price"]:visible').fill("125000");
        await kho1.page.locator('input[data-fieldname="default_unit_price"]:visible').press("Tab");
        await save(kho1.page);
        await kho1.page.getByRole("button", { name: "Nhập kho", exact: true }).click();
        await kho1.page.locator('input[data-fieldname="quantity"]:visible').fill("5");
        await kho1.page.locator('input[data-fieldname="quantity"]:visible').press("Tab");
        await save(kho1.page);
        await kho1.page.waitForFunction(() => cur_frm.doc.balance_after === 5);
        const receipt = await kho1.page.evaluate(() => cur_frm.doc.name);
        await kho1.page.screenshot({ path: path.join(shots, "05-stock-receipt.png"), fullPage: true });

        await sale1.page.goto("/app/simple-order");
        await sale1.page.locator(".page-head .primary-action:visible").click();
        await sale1.page.locator('input[data-fieldname="customer_name"]:visible').fill("Khách Sale 1");
        await sale1.page.locator('input[data-fieldname="item"]:visible').fill(code);
        await sale1.page.locator('input[data-fieldname="item"]:visible').press("Tab");
        await sale1.page.waitForFunction(() => cur_frm.doc.unit_price === 125000);
        await sale1.page.locator('input[data-fieldname="quantity"]:visible').fill("2");
        await sale1.page.locator('input[data-fieldname="quantity"]:visible').press("Tab");
        await sale1.page.locator('input[data-fieldname="warehouse_user"]:visible').fill("kho1@example.com");
        await sale1.page.locator('input[data-fieldname="warehouse_user"]:visible').press("Tab");
        await save(sale1.page);
        const order = await sale1.page.evaluate(() => ({ name: cur_frm.doc.name, total: cur_frm.doc.total }));
        assert.equal(order.total, 250000);
        assert.equal(await sale1.page.getByRole("button", { name: "Đã giao", exact: true }).count(), 0);
        assert.equal(await sale1.page.getByRole("button", { name: "Doanh thu theo ngày", exact: true }).count(), 0);
        await sale1.page.screenshot({ path: path.join(shots, "06-sale-order.png"), fullPage: true });

        const second = await create(sale2, "Simple Order", {
            customer_name: "Khách Sale 2", item: code, quantity: 1, unit_price: 125000, warehouse_user: "kho2@example.com",
        });
        for (const [actor, visible, hidden] of [
            [sale1, order, second], [sale2, second, order], [kho1, order, second], [kho2, second, order],
        ]) {
            const list = await actor.context.request.get(docURL("Simple Order"), { params: { limit_page_length: "1000" } });
            assert.equal(list.status(), 200);
            const names = (await list.json()).data.map(row => row.name);
            assert.ok(names.includes(visible.name));
            assert.ok(!names.includes(hidden.name));
            await denied(actor, "get", docURL("Simple Order", hidden.name));
            await denied(actor, "get", "/api/method/frappe.desk.query_report.run?report_name=Daily%20Revenue");
        }
        await denied(sale1, "put", docURL("Simple Order", order.name), { status: "Đã giao" });
        await denied(kho2, "put", docURL("Simple Order", order.name), { warehouse_user: "kho2@example.com", status: "Đã giao" });
        await denied(kho1, "put", docURL("Simple Order", order.name), { unit_price: 1, status: "Đã giao" });
        await denied(sale1, "post", docURL("Stock Receipt"), { item: code, quantity: 100 });
        await denied(kho1, "post", docURL("Simple Order"), { customer_name: "No", item: code, quantity: 1, unit_price: 1 });
        await denied(sale1, "post", docURL("Stock Item"), { item_code: "FORBIDDEN", item_name: "No" });
        const changedReceipt = await kho1.request("put", docURL("Stock Receipt", receipt), { quantity: 999 });
        assert.equal(changedReceipt.status(), 417);
        const forgedBalance = await kho1.request("put", docURL("Stock Item", code), { stock_qty: 999 });
        assert.equal(forgedBalance.status(), 417);

        await kho1.page.goto(`/app/simple-order/${order.name}`);
        await kho1.page.getByRole("button", { name: "Đã giao", exact: true }).click();
        await kho1.page.getByRole("button", { name: "Yes", exact: true }).click();
        await kho1.page.waitForFunction(() => cur_frm.doc.status === "Đã giao" && !cur_frm.is_dirty());
        await kho1.page.locator(".modal:visible").waitFor({ state: "hidden" });
        await kho1.page.locator(".modal-backdrop:visible").waitFor({ state: "hidden" });
        assert.equal(await kho1.page.getByRole("button", { name: "Hủy", exact: true }).count(), 0);
        await kho1.page.screenshot({ path: path.join(shots, "07-warehouse-delivered.png"), fullPage: true });
        assert.equal((await read(kho1, "Stock Item", code)).stock_qty, 3);
        const duplicate = await kho1.request("put", docURL("Simple Order", order.name), { status: "Đã giao" });
        assert.equal(duplicate.status(), 417);
        assert.equal((await read(kho1, "Stock Item", code)).stock_qty, 3);

        const races = await Promise.all(["kho1@example.com", "kho2@example.com"].map(warehouse_user => create(sale1, "Simple Order", {
            customer_name: "Hai yêu cầu tranh tồn", item: code, quantity: 3, unit_price: 125000, warehouse_user,
        })));
        const results = await Promise.all([kho1, kho2].map((actor, i) => actor.request("put", docURL("Simple Order", races[i].name), { status: "Đã giao" })));
        assert.equal(results.filter(result => result.status() === 200).length, 1);
        assert.equal(results.filter(result => result.status() === 417).length, 1);
        assert.equal((await read(admin, "Stock Item", code)).stock_qty, 0);
        const statuses = await Promise.all(races.map(async row => (await read(sale1, "Simple Order", row.name)).status));
        assert.equal(statuses.filter(status => status === "Đã giao").length, 1);
        assert.equal(statuses.filter(status => status === "Mới").length, 1);
        await create(kho1, "Stock Receipt", { item: code, quantity: 1 });
        const repeated = await create(sale1, "Simple Order", {
            customer_name: "Cùng xác nhận một đơn", item: code, quantity: 1, unit_price: 125000,
            warehouse_user: "kho1@example.com",
        });
        const simultaneous = await Promise.all([1, 2].map(() => kho1.request("put", docURL("Simple Order", repeated.name), { status: "Đã giao" })));
        assert.equal(simultaneous.filter(result => result.status() === 200).length, 1);
        assert.equal(simultaneous.filter(result => [409, 417].includes(result.status())).length, 1);
        assert.equal((await read(admin, "Stock Item", code)).stock_qty, 0);
        await admin.page.goto("/app/stock-item");
        await admin.page.waitForFunction(() => window.cur_list?.data?.length > 0);
        await admin.page.screenshot({ path: path.join(shots, "08-stock-items.png"), fullPage: true });
        console.log(`PASS: catalog ${code}, receipt, Sale/Kho UI, scoped lists/URLs/API, report denial, immutable stock, concurrent last-stock and same-order delivery.`);
    } catch (error) {
        for (let i = 0; i < pages.length; i++) {
            await pages[i].screenshot({ path: path.join(__dirname, `../.cache/rbac-failure-${i}.png`), fullPage: true }).catch(() => {});
        }
        throw error;
    } finally {
        await browser.close();
    }
})().catch(error => { console.error(error); process.exitCode = 1; });
