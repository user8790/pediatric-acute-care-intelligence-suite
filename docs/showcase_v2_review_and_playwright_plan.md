# Showcase v2 Review and Playwright Plan

## Review Summary

The showcase is now a credible v2 product surface, but the next quality step is to protect the public demo with browser-level regression tests and remove internal-only demo scaffolding from production navigation.

## Opportunities Identified

1. **Public surface clarity:** the Walkthrough tab is useful for internal rehearsal, but it reads as meta-demo content on the public product surface. Keep it local/internal and remove it from the production nav and hero.
2. **Regression coverage:** unit tests and Vite builds do not catch broken tab navigation, missing v2 JSON assets, blank chart canvases, or responsive overflow. Add Playwright tests against a production preview server.
3. **Visual risk areas:** ECharts-heavy pages should be checked in a browser because successful TypeScript compilation does not prove charts render.
4. **Responsive polish:** the public app is desktop-first, but tablet/mobile visitors should not see page-level horizontal overflow.
5. **Data contract guard:** the public showcase should keep serving `/data/v2/metadata.json` and the app should continue to identify itself as v2.

## Changes Implemented

- Added `@playwright/test` to the showcase dev toolchain.
- Added Playwright config with production preview web server.
- Added Chromium desktop and mobile projects.
- Added public-surface tests for nav rendering, v2 metadata, page navigation, chart canvases, and horizontal overflow.
- Gated the Walkthrough page behind local development or `VITE_SHOW_WALKTHROUGH=true`, removing it from the public production nav and hero.

## Future Showcase Opportunities

- Add screenshot comparison baselines for the six public pages.
- Add keyboard-navigation and focus-order tests.
- Add chart-specific assertions for tooltips and legends.
- Add lazy route splitting if bundle size becomes a measured load issue.
- Add a public demo script document outside the product surface rather than a visible Walkthrough tab.
