// Record intro + outro GSAP cards to WebM.
//   NODE_PATH=~/repopilot-recording/node_modules node docs/record_cards.js
const { chromium } = require('playwright-core');
const CHROME = '/home/ec2-user/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome';

async function recordCard(url, outDir, holdMs) {
  const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1,
    recordVideo: { dir: outDir, size: { width: 1920, height: 1080 } },
  });
  const page = await context.newPage();
  await page.goto(url, { waitUntil: 'load' });
  await page.waitForTimeout(holdMs);
  await context.close(); await browser.close();
  console.log('card done ->', outDir);
}
(async () => {
  await recordCard('http://127.0.0.1:8099/card-intro.html', '/home/ec2-user/repopilot-sandbox-rec/cards/intro', 6500);
  await recordCard('http://127.0.0.1:8099/card-outro.html', '/home/ec2-user/repopilot-sandbox-rec/cards/outro', 9000);
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
