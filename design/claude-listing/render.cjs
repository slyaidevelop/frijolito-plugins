// Renders listing.html into the three images the plugin README shows.
// Run: node design/claude-listing/render.cjs (needs Playwright).
const { chromium } = require('playwright');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const OUT = path.join(__dirname, '..', '..', 'plugins', 'frijolito', 'assets', 'listing');

(async () => {
  const src = pathToFileURL(path.join(__dirname, 'listing.html')).href;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
  const scenes = ['ask', 'verify', 'receipt'];
  for (let n = 0; n < scenes.length; n += 1) {
    await page.goto(`${src}?s=${scenes[n]}`, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const loaded = await page.evaluate(() => ['Playfair Display', 'Inter', 'JetBrains Mono'].map((f) => document.fonts.check(`16px "${f}"`)));
    if (loaded.includes(false)) throw new Error(`A listing font did not load: ${loaded}`);
    await page.screenshot({ path: path.join(OUT, `${n + 1}-${scenes[n]}.png`) });
  }
  await browser.close();
})();
