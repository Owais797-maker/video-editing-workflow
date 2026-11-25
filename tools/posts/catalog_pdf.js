// node tools/posts/catalog_pdf.js  -> one catalogue PDF (post + Urdu caption per page) + one PDF per product
const fs = require("fs"), path = require("path");
const { chromium } = require("playwright");
const R = path.resolve(__dirname, "../..");
const D = path.join(R, "Video Edits/Export/posts-3x4");
const OUT = path.join(D, "pdf"); fs.mkdirSync(OUT, { recursive: true });
const caps = JSON.parse(fs.readFileSync(path.join(__dirname, "captions_ur.json"), "utf8"));
const find = (g) => { const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => e.isDirectory() ? walk(path.join(d, e.name)) : [path.join(d, e.name)]); return walk(path.join(R, "fonts")).find((f) => path.basename(f) === g); };
const font = (fam, file, w) => `@font-face{font-family:${fam};src:url("${encodeURI("file://" + find(file))}");font-weight:${w}}`;
const css = `${font("Naskh", "NotoNaskhArabic-400.ttf", 400)}${font("Naskh", "NotoNaskhArabic-700.ttf", 700)}
@page{size:180mm 300mm;margin:0} *{margin:0;padding:0;box-sizing:border-box}
body{font-family:Naskh;background:#fff}
.pg{width:180mm;height:300mm;page-break-after:always;display:flex;flex-direction:column;padding:6mm 6mm 5mm}
.pg img{width:168mm;height:224mm;border-radius:4mm;display:block}
.cap{flex:1;direction:rtl;text-align:right;padding:4mm 3mm 0;color:#1B1B1F}
.cap h2{font:700 19pt/1.6 Naskh;color:#D7232E} .cap p{font:400 13.5pt/1.75 Naskh}
.cap .kt{margin-top:1.5mm;font:400 12pt/1.6 Naskh;color:#555} .cap .kt b{font-family:Montserrat,Arial;font-weight:800;direction:ltr;unicode-bidi:isolate}`;
const page = ([f, t, ls]) => `<div class="pg"><img src="file://${path.join(D, f + ".jpg")}"><div class="cap"><h2>${t}</h2>${ls.map((l) => `<p>${l}</p>`).join("")}<p class="kt">خیبر ٹریڈرز، ڈینسو ہال کراچی — <b>0310-2999262</b></p></div></div>`;
const doc = (ps) => `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>${ps.map(page).join("")}</body></html>`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  const go = async (ps, out) => { const h = path.join(OUT, "_tmp.html"); fs.writeFileSync(h, doc(ps)); await p.goto("file://" + h, { waitUntil: "load" }); await p.evaluate(() => document.fonts.ready); await p.pdf({ path: out, width: "180mm", height: "300mm", printBackground: true }); fs.unlinkSync(h); };
  await go(caps, path.join(D, "khyber-traders-catalogue.pdf"));
  let i = 1; for (const c of caps) { await go([c], path.join(OUT, `${String(i++).padStart(2, "0")}-${c[0].replace(/-post(-v\d)?$/, "").replace("novasil-post-colour","novasil-colour")}.pdf`)); }
  await b.close(); console.log("done");
})().catch((e) => { console.error(e); process.exit(1); });
