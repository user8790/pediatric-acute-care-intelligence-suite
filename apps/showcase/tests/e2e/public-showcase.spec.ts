import { expect, test } from "@playwright/test";

const publicPages = [
  { button: "System Posture", text: "Today’s Pediatric System Posture" },
  { button: "Inpatient", text: "Huddle view with source-readiness" },
  { button: "Ambulatory", text: "Backlog, template capacity" },
  { button: "Predictive Assets", text: "15 governed synthetic assets" },
  { button: "Scenarios", text: "Move sliders, apply constraints" },
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

test("interactive workspace opens drilldowns and responds to scenario controls", async ({ page }) => {
  await page.goto("/");
  const nav = page.getByRole("navigation", { name: "Product areas" });

  await nav.getByRole("button", { name: "Inpatient", exact: true }).click();
  await page.locator(".drilldown-card").first().click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByText("Unit Drilldown", { exact: true })).toBeVisible();
  await expect(page.getByText("Synthetic aggregate unit drilldown.")).toBeVisible();
  await page.getByLabel("Close drawer").click();

  await nav.getByRole("button", { name: "Ambulatory", exact: true }).click();
  await page.locator(".drilldown-card").first().click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByText("Program Drilldown", { exact: true })).toBeVisible();
  await expect(page.getByText("Synthetic aggregate program drilldown.")).toBeVisible();
  await page.getByLabel("Close drawer").click();

  await nav.getByRole("button", { name: "Predictive Assets", exact: true }).click();
  await page.locator(".model-card-button").first().click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByText("Model Card", { exact: true })).toBeVisible();
  await expect(page.getByText("Warning logic")).toBeVisible();
  await expect(page.getByText("Coefficients")).toBeVisible();
  await expect(page.getByLabel("Close drawer")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);

  await nav.getByRole("button", { name: "System Posture", exact: true }).click();
  await page.locator(".source-chip").first().click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByText("Source Readiness", { exact: true })).toBeVisible();
  await expect(page.getByText("Curated view")).toBeVisible();
  await expect(page.getByText("Fields")).toBeVisible();
  await expect(page.getByLabel("Close drawer")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);

  await nav.getByRole("button", { name: "Scenarios", exact: true }).click();
  const firstSlider = page.locator(".slider-control input[type='range']").first();
  await firstSlider.evaluate((slider) => {
    const setValue = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
    setValue?.call(slider, String(Number(slider.max)));
    slider.dispatchEvent(new Event("input", { bubbles: true }));
    slider.dispatchEvent(new Event("change", { bubbles: true }));
  });
  await page.getByRole("button", { name: /Weekend clinic capacity/i }).click();
  await expect(page.getByText("14 beds")).toBeVisible();
  await expect(page.getByText("Available HR shifts", { exact: true })).toBeVisible();
  await expect(page.getByText("Finance cap", { exact: true })).toBeVisible();
  await expect(page.locator(".comparison-board")).toContainText("Baseline");
  await expect(page.locator(".comparison-board")).toContainText("Scenario");
});

test("showcase learning memory captures local synthetic events", async ({ page }) => {
  await page.goto("/");
  const nav = page.getByRole("navigation", { name: "Product areas" });
  await nav.getByRole("button", { name: "Memory", exact: true }).click();

  await page.getByRole("button", { name: /Add synthetic acknowledgement/i }).click();
  await expect(page.getByText("Synthetic acknowledgement captured from the public showcase.")).toBeVisible();
});
