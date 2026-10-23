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

  // --- NEW demo: the before/after story (holds timed to the Polly VO segments) ---
  await page.goto(NEW_URL, { waitUntil: 'load' });
  await hold(page, 3200);                                  // header while intro card tail + hook VO opens

  // Start: Before/v1 + Safe repo (default). hook VO (~11s) plays over header+this.
  await hold(page, 8200);

  // v1 sneaky -> "Looks fine" (gap VO ~9.7s)
  await flip(page, 'button[data-repo="bad"]', 9800);

  // v2 sneaky -> real log + caught curl|bash (payoff VO ~13s). money shot: long hold.
  await flip(page, 'button[data-ver="v2"]', 13200);

  // v2 safe -> clean SUCCEEDED (safe VO ~8.5s)
  await flip(page, 'button[data-repo="good"]', 8800);

  await hold(page, 1400);

  // --- OLD RepoPilot UI (close VO ~28s spans this + the return) ---
  await page.goto(OLD_URL, { waitUntil: 'domcontentloaded' }).catch(() => {});
  await hold(page, 7000);                                  // show the original reads-it UI
  await page.evaluate(() => window.scrollBy({ top: 420, behavior: 'smooth' })).catch(() => {});
  await hold(page, 5000);

  // --- back to the new demo for the close; end on caught danger ---
  await page.goto(NEW_URL, { waitUntil: 'load' });
  await flip(page, 'button[data-ver="v2"]', 1000);
  await flip(page, 'button[data-repo="bad"]', 9000);       // end on the caught-danger frame
  await hold(page, 2500);

  await context.close();
  await browser.close();
  console.log('demo recording complete ->', OUT_DIR);
})().catch((e) => { console.error('ERR', e.message); process.exit(1); });
