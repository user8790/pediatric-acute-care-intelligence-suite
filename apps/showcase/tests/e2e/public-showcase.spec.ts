import { expect, test } from "@playwright/test";

const publicPages = [
  { button: "Overview", text: "Pediatric operations intelligence" },
  { button: "Inpatient", text: "Executive Inpatient Mission Control" },
  { button: "Ambulatory", text: "Executive Ambulatory Access Mission Control" },
  { button: "Simulation", text: "Scenario Simulation Lab" },
  { button: "Methods", text: "Model Registry and Methods Explorer" },
  { button: "Governance", text: "Governance, Privacy, Safety" },
];

test("production public surface hides internal walkthrough", async ({ page }) => {
  const consoleErrors: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") {
      consoleErrors.push(message.text());
    }
  });

  await page.goto("/");

  await expect(page.getByRole("heading", { name: /Executive command centre/i })).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Product areas" })).not.toContainText("Walkthrough");
  await expect(page.getByRole("button", { name: /10-minute walkthrough/i })).toHaveCount(0);
  await expect(page.locator(".status-stack").getByText("Synthetic demonstration data", { exact: true })).toBeVisible();
  expect(consoleErrors).toEqual([]);
});

test("v2 metadata and all public pages render", async ({ page, request }) => {
  const metadata = await request.get("/data/v2/metadata.json");
  await expect(metadata).toBeOK();
  expect((await metadata.json()).appVersion).toBe("v2.0");

  await page.goto("/");
  const nav = page.getByRole("navigation", { name: "Product areas" });

  for (const publicPage of publicPages) {
    await nav.getByRole("button", { name: publicPage.button, exact: true }).click();
    await expect(page.getByText(publicPage.text).first()).toBeVisible();
  }
});

test("charts render and layout avoids page-level horizontal overflow", async ({ page }) => {
  await page.goto("/");
  const nav = page.getByRole("navigation", { name: "Product areas" });

  await nav.getByRole("button", { name: "Inpatient", exact: true }).click();
  await expect(page.locator("canvas").first()).toBeVisible();

  await nav.getByRole("button", { name: "Simulation", exact: true }).click();
  await expect(page.locator("canvas").first()).toBeVisible();

  const hasPageOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
  expect(hasPageOverflow).toBe(false);
});
