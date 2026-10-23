// Record the NEW before/after toggle demo as a smooth 1080p WebM, driving the real toggles.
// Shows old (v1 reads it) vs new (v2 runs it) live, including the original RepoPilot UI.
// Run:
//   NODE_PATH=~/repopilot-recording/node_modules node docs/record_demo.js
const { chromium } = require('playwright-core');

const CHROME = '/home/ec2-user/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome';
const NEW_URL = 'http://127.0.0.1:8099/index.html';
const OLD_URL = 'https://simplynadaf.github.io/repopilot-your-first-run-agent/';
const OUT_DIR = '/home/ec2-user/repopilot-sandbox-rec/demo';

const hold = (p, ms) => p.waitForTimeout(ms);

// click a toggle by its data attribute, with a readable pause before + after
async function flip(page, sel, after = 2800) {
  await page.waitForSelector(sel, { timeout: 15000 });
  await hold(page, 600);
  await page.click(sel);
  await hold(page, after);
}

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    recordVideo: { dir: OUT_DIR, size: { width: 1920, height: 1080 } },
  });
  const page = await context.newPage();

  // --- NEW demo: the before/after story ---
  await page.goto(NEW_URL, { waitUntil: 'load' });
  await hold(page, 3400);                                  // header reads (hook VO)

  // Start: Before/v1 + Safe repo (default). Hold so "reads it" lands.
  await hold(page, 2600);

  // 0:28 switch repo to Sneaky, still v1 -> "Looks fine" (the gap)
  await flip(page, 'button[data-repo="bad"]', 3400);

  // 0:50 flip to After/v2, still Sneaky -> real log + caught curl|bash (payoff)
  await flip(page, 'button[data-ver="v2"]', 5200);         // long hold: this is the money shot

  // 1:25 switch repo to Safe, still v2 -> clean SUCCEEDED (balance)
  await flip(page, 'button[data-repo="good"]', 4200);

  // small settle
  await hold(page, 1600);

  // --- OLD RepoPilot UI (the agent I already built) ---
  await page.goto(OLD_URL, { waitUntil: 'domcontentloaded' }).catch(() => {});
  await hold(page, 5200);                                  // show the original reads-it UI
  // gentle scroll to show it is a real app
  await page.evaluate(() => window.scrollBy({ top: 420, behavior: 'smooth' })).catch(() => {});
  await hold(page, 3000);

  // --- back to the new demo for the close ---
  await page.goto(NEW_URL, { waitUntil: 'load' });
  await flip(page, 'button[data-ver="v2"]', 1200);
  await flip(page, 'button[data-repo="bad"]', 4200);       // end on the caught-danger frame
  await hold(page, 2000);

  await context.close();
  await browser.close();
  console.log('demo recording complete ->', OUT_DIR);
})().catch((e) => { console.error('ERR', e.message); process.exit(1); });
