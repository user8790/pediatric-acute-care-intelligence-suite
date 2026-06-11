import { expect, test } from "@playwright/test";

const publicPages = [
  { button: "System Posture", text: "Today’s Pediatric System Posture" },
  { button: "Inpatient", text: "Huddle view with source-readiness" },
  { button: "Ambulatory", text: "Backlog, template capacity" },
  { button: "Predictive Assets", text: "15 governed synthetic assets" },
  { button: "Scenarios", text: "Scenario comparison mode" },
  { button: "Gatekeeper", text: "AHA Gatekeeper Control Plane" },
  { button: "Memory", text: "Learning System Memory" },
  { button: "Wiring", text: "Future Real-Data Wiring" },
];

test("production public surface hides internal walkthrough", async ({ page }) => {
  const consoleErrors: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") {
      consoleErrors.push(message.text());
    }
  });

  await page.goto("/");

  await expect(page.getByRole("heading", { name: /Provincial Pediatric Acute Care Intelligence Operating Layer/i })).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Product areas" })).not.toContainText("Walkthrough");
  await expect(page.getByRole("button", { name: /10-minute walkthrough/i })).toHaveCount(0);
  await expect(page.locator(".status-stack").getByText("Synthetic demonstration data", { exact: true })).toBeVisible();
  expect(consoleErrors).toEqual([]);
});

test("v3 metadata and all public pages render", async ({ page, request }) => {
  const metadata = await request.get("/data/v3/metadata.json");
  await expect(metadata).toBeOK();
  expect((await metadata.json()).appVersion).toBe("v3.0");

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

  await nav.getByRole("button", { name: "Scenarios", exact: true }).click();
  await expect(page.locator("canvas").first()).toBeVisible();

  const hasPageOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
  expect(hasPageOverflow).toBe(false);
});

test("showcase learning memory captures local synthetic events", async ({ page }) => {
  await page.goto("/");
  const nav = page.getByRole("navigation", { name: "Product areas" });
  await nav.getByRole("button", { name: "Memory", exact: true }).click();

  await page.getByRole("button", { name: /Add synthetic acknowledgement/i }).click();
  await expect(page.getByText("Synthetic acknowledgement captured from the public showcase.")).toBeVisible();
});
