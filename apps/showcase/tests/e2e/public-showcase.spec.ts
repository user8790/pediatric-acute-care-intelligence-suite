import { expect, test } from "@playwright/test";

const publicPages = [
  { button: "System Posture", text: "Pediatric command centre" },
  { button: "Inpatient", text: "Inpatient progression hub" },
  { button: "Ambulatory", text: "Ambulatory access command centre" },
  { button: "Predictive Assets", text: "Predictive asset layer" },
  { button: "Scenarios", text: "Interactive scenario lab" },
  { button: "Readiness", text: "Data & Model Readiness" },
  { button: "AI Signals", text: "AI Signal Simulations" },
  { button: "Gatekeeper", text: "Gatekeeper Control Plane" },
  { button: "Memory", text: "Learning System Memory" },
  { button: "Wiring", text: "Future Real-Data Wiring" },
];

function control(page: import("@playwright/test").Page, index: number) {
  return page.locator(".control-band select").nth(index);
}

test("production public surface hides internal walkthrough", async ({ page }) => {
  const consoleErrors: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") {
      consoleErrors.push(message.text());
    }
  });

  await page.goto("/");

  await expect(page.getByRole("heading", { name: /Pediatric Command Centre/i })).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Product areas" })).not.toContainText("Walkthrough");
  await expect(page.getByRole("button", { name: /walkthrough/i })).toHaveCount(0);
  await expect(page.locator(".status-stack").getByText("Synthetic demonstration data", { exact: true })).toBeVisible();
  expect(consoleErrors).toEqual([]);
});

test("v5 metadata and all public pages render", async ({ page, request }) => {
  const metadata = await request.get("/data/v5/metadata.json");
  await expect(metadata).toBeOK();
  expect((await metadata.json()).appVersion).toBe("v5.0");

  await page.goto("/");
  const nav = page.getByRole("navigation", { name: "Product areas" });

  for (const publicPage of publicPages) {
    await nav.getByRole("button", { name: publicPage.button, exact: true }).click();
    await expect(page.getByText(publicPage.text).first()).toBeVisible();
  }
});

test("global controls visibly change the active command-centre lens", async ({ page }) => {
  await page.goto("/");

  await control(page, 1).selectOption("SITE_STOLLERY_INSPIRED");
  await expect(page.locator(".section-intro").first()).toContainText("Stollery-inspired");

  await control(page, 3).selectOption("respiratory");
  await expect(page.locator(".section-intro").first()).toContainText("Respiratory");

  await control(page, 2).selectOption("Next 24 hours");
  await expect(page.locator(".section-intro").first()).toContainText("Next 24 hours");

  await control(page, 6).selectOption("SCN-HR-FLOAT");
  await expect(page.locator(".section-intro").first()).toContainText("Deploy pediatric float-pool hours");

  await page.getByRole("navigation", { name: "Product areas" }).getByRole("button", { name: "Inpatient", exact: true }).click();
  const unitOptions = await control(page, 4).locator("option").evaluateAll((options) => options.map((option) => ({ value: (option as HTMLOptionElement).value, text: option.textContent ?? "" })));
  const respiratoryUnit = unitOptions.find((option) => option.value !== "All units" && /Respiratory/i.test(option.text));
  expect(respiratoryUnit).toBeTruthy();
  await control(page, 4).selectOption(respiratoryUnit!.value);
  await expect(page.locator(".section-intro").first()).toContainText(respiratoryUnit!.text.trim());

  await page.getByRole("navigation", { name: "Product areas" }).getByRole("button", { name: "Ambulatory", exact: true }).click();
  await control(page, 5).selectOption("respiratory");
  await expect(page.locator(".section-intro").first()).toContainText("Respiratory");
});

test("interactive workspace opens object, source, model, warning, and scenario drawers", async ({ page }) => {
  await page.goto("/");
  const nav = page.getByRole("navigation", { name: "Product areas" });

  await nav.getByRole("button", { name: "Inpatient", exact: true }).click();
  await page.locator(".object-card").first().click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByText("Capacity", { exact: true })).toBeVisible();
  await expect(page.getByText("Finance/resource proxy")).toBeVisible();
  await page.getByLabel("Close drawer").click();

  await nav.getByRole("button", { name: "Ambulatory", exact: true }).click();
  await page.locator(".object-card").first().click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByText("Referrals", { exact: true })).toBeVisible();
  await expect(page.getByText("Template capacity/gap")).toBeVisible();
  await page.getByLabel("Close drawer").click();

  await nav.getByRole("button", { name: "Predictive Assets", exact: true }).click();
  await page.locator(".model-card-button").first().click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByText("Source fields")).toBeVisible();
  await expect(page.getByText("Feature families")).toBeVisible();
  await expect(page.getByText("Threshold logic")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);

  await nav.getByRole("button", { name: "Gatekeeper", exact: true }).click();
  await page.locator(".source-readiness-table button").first().click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByText("Curated view")).toBeVisible();
  await expect(page.getByText("Fields")).toBeVisible();
  await page.keyboard.press("Escape");

  await nav.getByRole("button", { name: "System Posture", exact: true }).click();
  await page.locator(".warning-list button").first().click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByText("Recommended action")).toBeVisible();
  await page.keyboard.press("Escape");

  await nav.getByRole("button", { name: "Scenarios", exact: true }).click();
  await page.locator(".clickable-row").first().click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByRole("dialog").getByText("Trade-off", { exact: true })).toBeVisible();
});

test("scenario sliders, toggles, HR, and finance constraints recompute outputs", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("navigation", { name: "Product areas" }).getByRole("button", { name: "Scenarios", exact: true }).click();

  const before = await page.locator(".improvement-card strong").textContent();
  const firstSlider = page.locator(".slider-control input[type='range']").first();
  await firstSlider.evaluate((slider) => {
    const input = slider as HTMLInputElement;
    const setValue = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
    setValue?.call(input, input.max);
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
  });
  await expect.poll(async () => page.locator(".improvement-card strong").textContent()).not.toBe(before);

  await page.getByRole("button", { name: /AQHI\/smoke context/i }).click();
  await expect(page.locator(".comparison-board")).toContainText("HR constraint");
  await expect(page.getByText("Available HR hours", { exact: true })).toBeVisible();
  await expect(page.getByText("Finance cap", { exact: true })).toBeVisible();
});

test("readiness and AI signal simulation pages expose implementation transparency", async ({ page }) => {
  await page.goto("/");
  const nav = page.getByRole("navigation", { name: "Product areas" });

  await nav.getByRole("button", { name: "Readiness", exact: true }).click();
  await expect(page.getByText("Implementation transparency for feeds")).toBeVisible();
  await expect(page.getByText("Blocked / not connected")).toBeVisible();
  await page.getByRole("button", { name: /Pending Model/i }).click();
  await expect(page.getByRole("cell", { name: "Rare-disease case-finding simulation" }).first()).toBeVisible();

  await nav.getByRole("button", { name: "AI Signals", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Triage and LOS orchestration" })).toBeVisible();
  await page.getByRole("button", { name: "Rare-disease case finding", exact: true }).click();
  await expect(page.getByText("phenotype patterning")).toBeVisible();
  await page.getByRole("button", { name: "NEC recognition rehearsal", exact: true }).click();
  await expect(page.getByRole("heading", { name: "NEC recognition rehearsal" })).toBeVisible();
  await expect(page.getByText("Aggregate only")).toBeVisible();
  await page.getByRole("button", { name: /Capture signal review/i }).click();
  await nav.getByRole("button", { name: "Memory", exact: true }).click();
  await expect(page.getByText("reviewed as a synthetic implementation rehearsal")).toBeVisible();
});

test("at least twenty interactive charts exist across the public workspace and layout avoids horizontal overflow", async ({ page }) => {
  await page.goto("/");
  const nav = page.getByRole("navigation", { name: "Product areas" });
  const pages = ["System Posture", "Inpatient", "Ambulatory", "Predictive Assets", "Scenarios", "AI Signals"];
  let chartCount = 0;

  for (const pageName of pages) {
    await nav.getByRole("button", { name: pageName, exact: true }).click();
    await expect(page.locator("canvas").first()).toBeVisible();
    chartCount += await page.locator("canvas").count();
  }

  expect(chartCount).toBeGreaterThanOrEqual(20);
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
