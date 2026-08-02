import { expect, test } from "@playwright/test";

test("landing page exposes the main research workflow", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Khám phá tri thức khoa học/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /Bắt đầu tìm paper/i })).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Điều hướng chính" })).toBeVisible();
});

test("registration form provides concrete client-side validation", async ({ page }) => {
  await page.goto("/register");
  await page.getByLabel("Email").fill("invalid");
  await page.getByLabel("Username").fill("a");
  await page.getByLabel("Mật khẩu", { exact: true }).fill("weak");
  await page.getByLabel("Nhập lại mật khẩu").fill("different");
  await page.getByRole("button", { name: "Đăng ký" }).click();

  await expect(page.getByText("Email không hợp lệ")).toBeVisible();
  await expect(page.getByText(/Tên đăng nhập cần ít nhất/i)).toBeVisible();
});

test("search page exposes filters without submitting to the API", async ({ page }) => {
  await page.goto("/search");
  await expect(page.getByRole("heading", { name: /Tìm kiếm bài báo/i })).toBeVisible();
  await expect(page.getByLabel(/Từ năm/i)).toBeVisible();
  await expect(page.getByLabel(/Đến năm/i)).toBeVisible();
  await expect(page.getByText(/Open Access/i)).toBeVisible();
});

test("pricing page explains mock and Stripe modes", async ({ page }) => {
  await page.goto("/pricing");
  await expect(page.getByRole("heading", { name: "Gói sử dụng" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Chọn Premium" })).toBeVisible();
  await expect(page.getByText(/mock billing/i)).toBeVisible();
});
