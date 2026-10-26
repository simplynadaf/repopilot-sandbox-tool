// ============================================================================
// record_demo_v2.js  —  drives the REAL integrated RepoPilot UI (not the old toggle)
// Shows: old v1 (reads it) -> new UI sneaky repo F-score -> NEW TOOL runs it ->
//        catches curl|bash -> safe repo clean -> old UI proof -> close on caught danger.
// Holds are timed to the Polly VO segments synthesized by make_video.sh.
// Run (via make_video.sh): NODE_PATH=~/repopilot-recording/node_modules node record_demo_v2.js
// ============================================================================
const { chromium } = require('playwright-core');

const CHROME  = '/home/ec2-user/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome';
const NEW_URL = 'http://127.0.0.1:8099/index.html';       // the real integrated UI (docs/index.html)
const OLD_URL = 'https://simplynadaf.github.io/repopilot-your-first-run-agent/';
const OUT_DIR = '/home/ec2-user/repopilot-sandbox-rec/demo';

const hold = (p, ms) => p.waitForTimeout(ms);
// click the sandbox run button, waiting for it to exist (it is rendered after inspect)
async function runSandbox(page) {
  await page.waitForSelector('#sbxRun', { timeout: 15000 });
  await page.click('#sbxRun');
}

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    recordVideo: { dir: OUT_DIR, size: { width: 1920, height: 1080 } },
  });
  const page = await context.newPage();

  // ---- HOOK (~17s): the OLD agent that only reads the repo ----
  await page.goto(OLD_URL, { waitUntil: 'domcontentloaded' }).catch(() => {});
  await hold(page, 5500);
  await page.evaluate(() => window.scrollBy({ top: 360, behavior: 'smooth' })).catch(() => {});
  await hold(page, 6000);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' })).catch(() => {});
  await hold(page, 5500);

  // ---- THE GAP (~24s): new UI, sneaky repo, static F scorecard (read-only verdict) ----
  await page.goto(NEW_URL, { waitUntil: 'load' });
  await hold(page, 2500);
  await page.click('.examples button[data-repo="evil/fake-agent-kit"]');
  await hold(page, 2600);                                   // scorecard animates in
  // scroll so the F score + critical issues are centered
  await page.evaluate(() => document.querySelector('#scorecard')?.scrollIntoView({ behavior: 'smooth', block: 'center' })).catch(() => {});
  await hold(page, 18000);                                  // gap VO reads over the static F verdict

  // ---- PAYOFF (~37s): scroll to the NEW TOOL panel and run it ----
  await page.evaluate(() => document.querySelector('#sandbox')?.scrollIntoView({ behavior: 'smooth', block: 'center' })).catch(() => {});
  await hold(page, 3000);                                   // let the NEW TOOL ribbon/panel land
  await runSandbox(page);                              // run the sandbox tool
  await hold(page, 6500);                                   // log types out line by line
  // keep the caught-danger card centered for the money shot
  await page.evaluate(() => document.querySelector('#sbxOut')?.scrollIntoView({ behavior: 'smooth', block: 'center' })).catch(() => {});
  await hold(page, 20000);                                  // long hold on caught curl|bash + contrast chip

  // ---- BALANCE (~20s): safe repo, run the tool, clean green verdict ----
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' })).catch(() => {});
  await hold(page, 1200);
  await page.click('.examples button[data-repo="pallets/flask"]');   // safe repo: A score + green sandbox replay
  await hold(page, 2600);                                   // scorecard animates (98 / A)
  await page.evaluate(() => document.querySelector('#sandbox')?.scrollIntoView({ behavior: 'smooth', block: 'center' })).catch(() => {});
  await hold(page, 1500);
  await runSandbox(page);
  await hold(page, 6500);
  await page.evaluate(() => document.querySelector('#sbxOut')?.scrollIntoView({ behavior: 'smooth', block: 'center' })).catch(() => {});
  await hold(page, 8000);                                   // green SUCCEEDED / no danger

  // ---- PROOF (~18s): back to the OLD UI briefly (the agent I already shipped) ----
  await page.goto(OLD_URL, { waitUntil: 'domcontentloaded' }).catch(() => {});
  await hold(page, 9000);
  await page.evaluate(() => window.scrollBy({ top: 400, behavior: 'smooth' })).catch(() => {});
  await hold(page, 8000);

  // ---- CLOSE (~15s): end on the new UI caught-danger frame ----
  await page.goto(NEW_URL, { waitUntil: 'load' });
  await page.click('.examples button[data-repo="evil/fake-agent-kit"]');
  await hold(page, 2600);
  await page.evaluate(() => document.querySelector('#sandbox')?.scrollIntoView({ behavior: 'smooth', block: 'center' })).catch(() => {});
  await runSandbox(page);
  await hold(page, 7000);
  await page.evaluate(() => document.querySelector('#sbxOut')?.scrollIntoView({ behavior: 'smooth', block: 'center' })).catch(() => {});
  await hold(page, 6000);                                   // end on caught danger

  await context.close();
  await browser.close();
  console.log('demo recording complete ->', OUT_DIR);
})().catch((e) => { console.error('ERR', e.message); process.exit(1); });
