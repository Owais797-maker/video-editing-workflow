// node anim_frames.js job.json outdir fps seconds [scale]
// Renders an HTML post with CSS animations frame by frame (animations are paused and seeked, so timing is exact).
const fs = require("fs"), path = require("path");
const { chromium } = require("playwright");
(async () => {
  const [jobP, outDir, fpsS, durS, scS] = process.argv.slice(2);
  const job = JSON.parse(fs.readFileSync(jobP, "utf8")); const fps = +fpsS, dur = +durS;
  fs.mkdirSync(outDir, { recursive: true });
  const faces = job.fonts.map((f) => `@font-face{font-family:"${f.family}";src:url(data:font/ttf;base64,${fs.readFileSync(f.path).toString("base64")}) format("truetype");font-weight:${f.weight};font-style:${f.style};}`).join("\n");
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>${faces}
    html,body{margin:0;width:${job.width}px;height:${job.height}px;overflow:hidden;} ${job.css}</style></head>
    <body><div id="cap">${job.states[0].html}</div></body></html>`;
  const pagePath = path.join(path.dirname(path.resolve(jobP)), "anim.html"); fs.writeFileSync(pagePath, html);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: job.width, height: job.height }, deviceScaleFactor: +(scS || 1.5) });
  await p.goto("file://" + pagePath, { waitUntil: "load" });
  await p.evaluate(() => document.fonts.ready);
  await p.evaluate(() => Promise.all([...document.images].map((i) => i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; }))));
  await p.evaluate(() => document.getAnimations().forEach((a) => a.pause()));
  const n = Math.round(fps * dur);
  for (let i = 0; i < n; i++) {
    await p.evaluate((t) => document.getAnimations().forEach((a) => { a.currentTime = t; }), (i / fps) * 1000);
    await p.screenshot({ path: path.join(outDir, `f${String(i).padStart(5, "0")}.jpg`), type: "jpeg", quality: 93 });
  }
  await b.close(); console.log(`${n} frames`);
})().catch((e) => { console.error(e); process.exit(1); });
