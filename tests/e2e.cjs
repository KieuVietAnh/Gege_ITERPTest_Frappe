const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

(async () => {
    const root = path.join(__dirname, "..");
    const password = process.env.FRAPPE_TEST_PASSWORD || "admin";
    const browser = await chromium.launch({ headless: true });
    try {
        const context = await browser.newContext({
            baseURL: process.env.FRAPPE_TEST_URL || "http://127.0.0.1:8080",
            viewport: { width: 1440, height: 1000 },
        });
        const login = await context.request.post("/api/method/login", {
            form: { usr: "Administrator", pwd: password },
        });
        assert.equal(login.status(), 200);
        const page = await context.newPage();
        const pageErrors = [];
        page.on("pageerror", error => pageErrors.push(error.message));
        const screenshots = path.join(root, "docs/screenshots");
        fs.mkdirSync(screenshots, { recursive: true });

        async function reportRows() {
            const response = await context.request.get("/api/method/frappe.desk.query_report.run", {
                params: { report_name: "Daily Revenue", ignore_prepared_report: "1" },
            });
            assert.equal(response.status(), 200, await response.text());
            return (await response.json()).message.result;
        }

        async function createOrder(customer, takeScreenshot = false) {
            await page.goto("/app/simple-order");
            await page.locator(".page-head .primary-action:visible").click();
            await page.locator('input[data-fieldname="customer_name"]:visible').fill(customer);
            await page.locator('input[data-fieldname="item"]:visible').fill("KB001");
            await page.locator('input[data-fieldname="item"]:visible').press("Tab");
            await page.waitForFunction(() => cur_frm.doc.item_name === "Bàn phím" && cur_frm.doc.unit_price === 150000);
            await page.locator('input[data-fieldname="quantity"]:visible').fill("2");
            await page.locator('input[data-fieldname="quantity"]:visible').press("Tab");
            await page.locator('input[data-fieldname="unit_price"]:visible').fill("150000");
            await page.locator('input[data-fieldname="unit_price"]:visible').press("Tab");
            await page.waitForFunction(() => cur_frm.doc.total === 300000);
            if (takeScreenshot) {
                await page.screenshot({ path: path.join(screenshots, "01-create-order.png"), fullPage: true });
            }
            await page.locator(".page-head .primary-action:visible").click();
            await page.waitForFunction(() => cur_frm && !cur_frm.is_new() && !cur_frm.is_dirty());
            return page.evaluate(() => ({ name: cur_frm.doc.name, creation: cur_frm.doc.creation }));
        }

        async function closeOrder(status, filename) {
            await page.getByRole("button", { name: status, exact: true }).click();
            await page.getByRole("button", { name: "Yes", exact: true }).click();
            await page.locator(".modal:visible").waitFor({ state: "hidden" });
            await page.locator(".modal-backdrop:visible").waitFor({ state: "hidden" });
            await page.waitForFunction(value => cur_frm.doc.status === value && !cur_frm.is_dirty(), status);
            await page.locator('.frappe-control[data-fieldname="quantity"] .control-value').waitFor({ state: "visible" });
            assert.equal(await page.locator(".page-head .primary-action:visible").count(), 0);
            assert.equal(await page.getByRole("button", { name: "Đã giao", exact: true }).count(), 0);
            assert.equal(await page.getByRole("button", { name: "Hủy", exact: true }).count(), 0);
            await page.screenshot({ path: path.join(screenshots, filename), fullPage: true });
        }

        const before = await reportRows();
        const delivered = await createOrder("Khách demo giao hàng", true);
        await closeOrder("Đã giao", "02-delivered-order.png");
        const csrf = await page.evaluate(() => frappe.csrf_token);
        for (const data of [{ quantity: 99 }, { status: "Mới" }]) {
            const response = await context.request.put(`/api/resource/Simple%20Order/${delivered.name}`, {
                headers: { "X-Frappe-CSRF-Token": csrf }, data,
            });
            assert.equal(response.status(), 417);
            assert.equal((await response.json()).exc_type, "ValidationError");
        }

        const cancelled = await createOrder("Khách demo hủy đơn");
        await closeOrder("Hủy", "03-cancelled-order.png");
        const after = await reportRows();
        const day = delivered.creation.slice(0, 10);
        const prior = before.find(row => row.order_date === day) || { order_count: 0, revenue: 0 };
        const current = after.find(row => row.order_date === day);
        assert.equal(current.order_count, prior.order_count + 1);
        assert.equal(current.revenue, prior.revenue + 300000);

        await page.getByRole("button", { name: "Doanh thu theo ngày", exact: true }).click();
        await page.locator(".datatable").waitFor({ state: "visible" });
        await page.getByText("Saved", { exact: true }).last().waitFor({ state: "hidden" });
        await page.screenshot({ path: path.join(screenshots, "04-daily-revenue.png"), fullPage: true });
        assert.deepEqual(pageErrors, []);
        console.log(`PASS: create ${delivered.name}, deliver, lock, API protection, cancel ${cancelled.name}, daily report and screenshots.`);
    } finally {
        await browser.close();
    }
})().catch(error => { console.error(error); process.exitCode = 1; });
