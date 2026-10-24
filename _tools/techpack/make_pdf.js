// Turns _tools/techpack/print.html into downloads/tech-pack-template.pdf. Run make_techpack.py first.
const path = require('path');
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(__dirname, 'print.html'));
  await page.pdf({ path: path.join(__dirname, '..', '..', 'downloads', 'tech-pack-template.pdf'), format: 'A4', landscape: true, printBackground: true, preferCSSPageSize: true });
  await browser.close();
  console.log('Wrote downloads/tech-pack-template.pdf');
})();
