#!/usr/bin/env python3
"""Instagram 4:5 (2160x2700) "scan & pay" post: phone with the bank QR + account details (+ optional Raast card or logo).
    python3 tools/posts/payment_post.py tools/posts/payment-<name>.json
JSON: name, qr (repo path to the bank QR image), title, acc, iban, branch, bank, app_title, raast (optional),
      logo (optional repo path, transparent), G/G2/GD (accent colours). The QR is cropped + scaled NEAREST
      (never resampled); always verify it still decodes after rendering."""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image
R = Path(__file__).resolve().parents[2]
F = lambda g: str(next(R.joinpath('fonts').rglob(g)))
c = json.load(open(sys.argv[1]))
d = R / "Video Edits/Export" / c["name"]; w = d / "work"; w.mkdir(parents=True, exist_ok=True)
im = Image.open(R / c["qr"]).convert("RGB"); a = np.array(im.convert("L")) < 110
ys = np.where(a.any(1))[0]; xs = np.where(a.any(0))[0]
side = xs.max() + 1 - xs.min()  # QR is square: ignore any caption text printed under it
q = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.min() + side)); k = max(1, 1400 // q.width)
q = q.resize((q.width * k, q.height * k), Image.NEAREST); qp = w / "qr.png"; q.save(qp)
fonts = [{"family": "Noori", "path": F("JameelNooriNastaleeq-400.ttf"), "weight": 400, "style": "normal"},
         {"family": "Aslam", "path": F("Aslam-400.ttf"), "weight": 400, "style": "normal"},
         {"family": "Montserrat", "path": F("Montserrat-900.ttf"), "weight": 900, "style": "normal"},
         {"family": "Montserrat", "path": F("Montserrat-500.ttf"), "weight": 500, "style": "normal"},
         {"family": "Poppins", "path": F("Poppins-600.ttf"), "weight": 600, "style": "normal"},
         {"family": "Poppins", "path": F("Poppins-700.ttf"), "weight": 700, "style": "normal"},
         {"family": "Poppins", "path": F("Poppins-800.ttf"), "weight": 800, "style": "normal"}]
G, G2, GD, INK = c.get("G", "#0B7A3B"), c.get("G2", "#14A350"), c.get("GD", "#075A2B"), "#1B1B1F"
css = f"""*{{margin:0;padding:0;box-sizing:border-box}}
#p{{position:absolute;inset:0;overflow:hidden;font-family:Poppins;color:{INK};background:radial-gradient(ellipse 75% 55% at 50% 45%,#FFFFFF 0%,#F3F4F3 55%,#E2E5E3 100%)}}
.sheen{{position:absolute;inset:0;background:linear-gradient(115deg,transparent 42%,rgba(255,255,255,.55) 50%,transparent 58%)}}
.top{{position:absolute;top:64px;left:0;right:0;text-align:center;font:500 20px Montserrat;letter-spacing:8px;color:#6f7570}}
.top b{{font-weight:900;color:{INK};letter-spacing:6px}} .top i{{font-style:normal;color:{G}}}
.h{{position:absolute;top:96px;left:0;right:0;text-align:center;direction:rtl;font:74px/1.5 Noori;color:#26282a}}
.h span{{font:104px Aslam;background:linear-gradient(180deg,{G2},{G} 60%,{GD});-webkit-background-clip:text;color:transparent}}
.ph{{position:absolute;left:64px;top:262px;width:452px;height:800px;border-radius:64px;background:linear-gradient(160deg,#2b2e31,#0d0f10);box-shadow:0 40px 60px rgba(0,0,0,.28),inset 0 0 0 3px #3a3e42}}
.scr{{position:absolute;inset:16px;border-radius:50px;background:#fff;overflow:hidden}}
.isl{{position:absolute;top:14px;left:50%;transform:translateX(-50%);width:120px;height:34px;border-radius:20px;background:#0d0f10}}
.app{{position:absolute;top:68px;left:0;right:0;text-align:center;font:700 21px Poppins;color:#fff;background:{G};padding:14px 10px 12px}}
.app small{{display:block;font:600 14px Poppins;letter-spacing:4px;opacity:.85}}
.qrw{{position:absolute;top:172px;left:50%;transform:translateX(-50%);width:352px;height:352px;background:#fff}}
.qrw img{{width:352px;height:352px;image-rendering:pixelated;display:block}}
.br{{position:absolute;width:56px;height:56px;border:7px solid {G2}}}
.b1{{left:-22px;top:-22px;border-right:none;border-bottom:none;border-radius:18px 0 0 0}} .b2{{right:-22px;top:-22px;border-left:none;border-bottom:none;border-radius:0 18px 0 0}}
.b3{{left:-22px;bottom:-22px;border-right:none;border-top:none;border-radius:0 0 0 18px}} .b4{{right:-22px;bottom:-22px;border-left:none;border-top:none;border-radius:0 0 18px 0}}
.nmq{{position:absolute;top:562px;left:0;right:0;text-align:center;font:700 18px Poppins;letter-spacing:1px;color:#33363a}}
.scan{{position:absolute;top:606px;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:10px;background:#EEF7F1;color:{G};font:700 20px Poppins;padding:12px 26px;border-radius:40px;white-space:nowrap}}
.scan:before{{content:"";width:12px;height:12px;border-radius:50%;background:{G2};box-shadow:0 0 0 6px rgba(20,163,80,.18)}}
.dt{{position:absolute;left:560px;right:56px;top:300px;display:flex;flex-direction:column;gap:18px}}
.row small{{display:block;font:600 15px Poppins;letter-spacing:3.5px;color:#8a8f8b}}
.row b{{display:block;font:800 30px/1.2 Poppins;color:{INK};word-break:break-all}} .row b.s{{font-size:23px}}
.ln{{height:2px;background:linear-gradient(90deg,rgba(11,122,59,.35),transparent)}}
.raast{{position:absolute;left:560px;right:56px;top:836px;border-radius:30px;padding:22px 26px 24px;color:#fff;background:linear-gradient(135deg,{G2},{G} 55%,{GD});box-shadow:0 22px 36px rgba(11,122,59,.32)}}
.rl{{position:absolute;right:20px;bottom:18px;background:#fff;border-radius:14px;padding:8px 12px;box-shadow:0 8px 18px rgba(0,0,0,.2)}} .rl img{{height:30px;display:block}}
.raast small{{display:block;font:600 15px Poppins;letter-spacing:4px;opacity:.85}} .raast b{{display:block;font:800 40px/1.15 Poppins;margin-top:4px}} .raast span{{display:block;font:600 16px Poppins;opacity:.85;margin-top:4px}}
.logo{{position:absolute;left:{c.get('logo_left',600)}px;top:{c.get('logo_top',790)}px;width:{c.get('logo_w',300)}px;filter:drop-shadow(0 22px 26px rgba(0,0,0,.28));transform:rotate({c.get('logo_rot',-3)}deg);border-radius:{c.get('logo_radius',0)}px}}
.bt{{position:absolute;bottom:92px;left:0;right:0;text-align:center;direction:rtl;font:44px/1.6 Noori;color:#3a3d40}}
.bt span{{font-family:Aslam;color:{G};font-size:1.12em}}
.ft{{position:absolute;bottom:52px;left:0;right:0;text-align:center;font:500 16px Montserrat;letter-spacing:7px;color:#8a8f8b}}"""
raast = (f'<div class="raast" style="top:{c.get("raast_top",836)}px"><small>{c.get("raast_label","RAAST ID")}</small><b>{c["raast"]}</b>{('<i class="rl"><img src="file://' + str(R / c["raast_logo"]) + '"></i>') if c.get("raast_logo") else ""}<span>{c.get("raast_sub","Instant transfer from any bank")}</span></div>' if c.get("raast") else "")
logo = f'<img class="logo" src="file://{R / c["logo"]}">' if c.get("logo") else ""
html = f"""<div id="p"><div class="sheen"></div>
<div class="top">{c['top']}</div>
<div class="h"><span>اسکین</span> کریں، پیمنٹ کریں</div>
<div class="ph"><div class="scr"><div class="isl"></div><div class="app"><small>SCAN TO PAY</small>{c['app_title']}</div>
 <div class="qrw"><img src="file://{qp}"><i class="br b1"></i><i class="br b2"></i><i class="br b3"></i><i class="br b4"></i></div>
 <div class="nmq">{c['qr_name']}</div><div class="scan">Any bank app · Scan &amp; Pay</div></div></div>
<div class="dt">{''.join(f'<div class="row"><small>{k}</small><b class="{s}">{v}</b></div><div class="ln"></div>' for k, v, s in c['rows'])}</div>
{raast}{logo}
<div class="bt">{c.get('bt','کسی بھی <span>بینک ایپ</span> سے اسکین کر کے فوراً پیمنٹ کریں')}</div>
<div class="ft">{c['ft']}</div></div>"""
out = d / f"{c['name']}.png"; job = d / "job.json"
job.write_text(json.dumps({"width": 1080, "height": 1350, "scale": 2, "css": css, "fonts": fonts, "states": [{"file": str(out), "html": html}]}))
subprocess.run(["node", str(R / "tools/htmlcaps/render.js"), str(job)], check=True, capture_output=True)
job.unlink(); (d / "page.html").unlink(missing_ok=True)
Image.open(out).convert("RGB").save(out); print(out)
