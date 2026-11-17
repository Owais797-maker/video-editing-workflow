// Renders caption states to transparent full-frame PNGs with headless Chromium.
// Input: node render.js job.json
// job = {width, height, css, fonts:[{family, path, weight, style}], states:[{file, html}]}
const fs = require("fs");
const { chromium } = require("playwright");

(async () => {
  const job = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
  const faces = job.fonts.map((f) =>
    `@font-face{font-family:"${f.family}";src:url(data:font/ttf;base64,${fs.readFileSync(f.path).toString("base64")}) format("truetype");font-weight:${f.weight};font-style:${f.style};}`).join("\n");
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
    ${faces}
    html,body{margin:0;width:${job.width}px;height:${job.height}px;background:transparent;overflow:hidden;}
    ${job.css}
  </style></head><body><div id="cap"></div></body></html>`;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: job.width, height: job.height }, deviceScaleFactor: job.scale || 1 });
  // load from a file next to the job so file:// images (product cutouts) are allowed
  const path = require("path");
  const pagePath = path.join(path.dirname(path.resolve(process.argv[2])), "page.html");
  fs.writeFileSync(pagePath, html);
  await page.goto("file://" + pagePath, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  for (const st of job.states) {
    await page.evaluate((h) => { document.getElementById("cap").innerHTML = h; }, st.html);
    await page.evaluate(() => Promise.all([...document.images].map((i) => i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; }))));
    await page.screenshot({ path: st.file, omitBackground: true });
  }
  await browser.close();
  console.log(`rendered ${job.states.length} caption frames`);
})().catch((e) => { console.error(e); process.exit(1); });
