#!/usr/bin/env python3
"""Thumbnails for clip-nov26b (North Nazimabad delivery): TikTok cover 9:16 and Facebook 16:9, Heavy Gold blue + gold."""
import json, subprocess
from pathlib import Path
from PIL import Image
R = Path(__file__).resolve().parents[2]
D = R / "Video Edits/Export/clip-nov26b/thumbs"; W = D / "work"
F = lambda g: str(next(R.joinpath("fonts").rglob(g)))
fonts = [{"family": "Montserrat", "path": F("Montserrat-900.ttf"), "weight": 900, "style": "normal"},
         {"family": "Montserrat", "path": F("Montserrat-500.ttf"), "weight": 500, "style": "normal"},
         {"family": "Aslam", "path": F("Aslam-400.ttf"), "weight": 400, "style": "normal"},
         {"family": "Noori", "path": F("JameelNooriNastaleeq-400.ttf"), "weight": 400, "style": "normal"}]
B, G, N = "#1E3FA0", "#FFD400", "#0E1F5E"
vac, mah = W / "f4.0.jpg", W / "f6.6.jpg"
hg = R / "Video Edits/Raw/heavy-gold/heavy-gold-bag-cutout.png"
box = R / "Video Edits/Raw/aftodoll-dispatch/box-cutout.png"
logo = R / "assets/logos/khyber-traders-wordmark-white-red.png"
moto = R / "assets/emoji/1f3cd.png"
base = f"""*{{margin:0;padding:0;box-sizing:border-box}}
.plate{{direction:rtl;display:inline-block;font-family:Aslam;color:#fff;background:linear-gradient(135deg,#2A55D6,{B} 55%,{N});border:6px solid {G};
 border-radius:.22em;padding:.02em .4em .14em;box-shadow:0 14px 34px rgba(0,0,0,.45);text-shadow:0 5px 14px rgba(0,0,0,.45);line-height:1.45}}
.plate i{{font-style:normal;color:{G}}}
.trip{{display:inline-flex;align-items:center;gap:16px;background:rgba(10,14,40,.78);border:2px solid rgba(255,255,255,.35);border-radius:60px;
 padding:14px 30px;font:900 30px Montserrat;color:#fff;letter-spacing:1px;box-shadow:0 10px 26px rgba(0,0,0,.35)}}
.trip .ln{{width:120px;height:5px;background:{G};border-radius:3px}} .trip img{{height:46px}}
.kt{{display:inline-flex;align-items:center;gap:18px;background:#111;border-radius:50px;padding:12px 26px 12px 22px;box-shadow:0 10px 26px rgba(0,0,0,.35)}}
.kt img{{height:50px}} .kt b{{background:{G};color:#111;border-radius:30px;padding:8px 18px;font:900 26px Montserrat}}"""
trip = f'<div class="trip">DENSO HALL <span class="ln"></span><img src="file://{moto}"> NORTH NAZIMABAD</div>'
kt = f'<div class="kt"><img src="file://{logo}"><b>0310-2999262</b></div>'

tt_css = base + f"""
#p{{position:absolute;inset:0;overflow:hidden;background:#000}}
.bg{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:saturate(1.1)}}
.shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,0) 34%,rgba(0,0,0,0) 62%,rgba(0,0,0,.7) 100%)}}
.h{{position:absolute;top:230px;left:0;right:0;text-align:center;display:flex;flex-direction:column;align-items:center;gap:14px}}
.h .a{{font-size:70px}} .h .b{{font-size:128px}} .h .c{{font-size:110px}}
.hg{{position:absolute;right:40px;bottom:500px;height:560px;filter:drop-shadow(0 24px 30px rgba(0,0,0,.5));transform:rotate(6deg)}}
.vb{{position:absolute;left:60px;bottom:520px;height:430px;filter:drop-shadow(0 24px 30px rgba(0,0,0,.5));transform:rotate(-6deg)}}
.tr{{position:absolute;bottom:330px;left:0;right:0;text-align:center}}
.ktw{{position:absolute;bottom:200px;left:0;right:0;text-align:center}}"""
tt = f"""<div id="p"><img class="bg" src="file://{vac}"><div class="shade"></div>
<div class="h"><div class="plate a">نارتھ ناظم آباد</div><div class="plate b"><i>پرانے پیسے والوں</i></div><div class="plate c">کی پسند!</div></div>
<img class="vb" src="file://{box}"><img class="hg" src="file://{hg}">
<div class="tr">{trip}</div><div class="ktw">{kt}</div></div>"""

fb_css = base + f"""
#p{{position:absolute;inset:0;overflow:hidden;background:radial-gradient(ellipse 70% 90% at 30% 50%,#2A55D6 0%,{B} 45%,{N} 100%)}}
.rays{{position:absolute;inset:0;background:repeating-linear-gradient(115deg,rgba(255,255,255,.035) 0 40px,transparent 40px 80px)}}
.card{{position:absolute;top:70px;height:940px;width:560px;object-fit:cover;border-radius:34px;border:7px solid #fff;box-shadow:0 26px 50px rgba(0,0,0,.5)}}
.c2{{right:340px;transform:rotate(-5deg)}} .c1{{right:40px;top:110px;transform:rotate(5deg);object-position:60% 0%;z-index:2}}
.h{{position:absolute;left:70px;top:90px;width:1040px;display:flex;flex-direction:column;align-items:center;gap:12px;text-align:center}}
.h .a{{font-size:66px}} .h .b{{font-size:118px}} .h .c{{font-size:100px}}
.prod{{position:absolute;left:150px;bottom:150px;display:flex;align-items:flex-end;gap:10px}}
.prod .hg{{height:400px;filter:drop-shadow(0 22px 26px rgba(0,0,0,.5))}} .prod .vb{{height:300px;filter:drop-shadow(0 22px 26px rgba(0,0,0,.5))}}
.plus{{position:absolute;left:520px;bottom:300px;font:900 90px Montserrat;color:{G};text-shadow:0 6px 16px rgba(0,0,0,.5)}}
.tr{{position:absolute;left:650px;bottom:300px}} .tr .trip{{font-size:24px;padding:12px 22px}} .tr .ln{{width:70px}}
.ktw{{position:absolute;left:650px;bottom:170px}}"""
fb = f"""<div id="p"><div class="rays"></div>
<img class="card c1" src="file://{mah}"><img class="card c2" src="file://{vac}">
<div class="h"><div class="plate a">نارتھ ناظم آباد</div><div class="plate b"><i>پرانے پیسے والوں</i></div><div class="plate c">کی پسند!</div></div>
<div class="prod"><img class="hg" src="file://{hg}"><img class="vb" src="file://{box}"></div>
<div class="tr">{trip}</div><div class="ktw">{kt}</div></div>"""

nk = lambda x: x.replace('<div class="ktw">' + kt + '</div>', '')
for name, w, h, css, html in [("tiktok-cover", 1080, 1920, tt_css, tt), ("facebook-thumbnail", 1920, 1080, fb_css, fb),
                              ("tiktok-cover-nokt", 1080, 1920, tt_css, nk(tt)), ("facebook-thumbnail-nokt", 1920, 1080, fb_css, nk(fb))]:
    job = W / f"{name}.json"; png = W / f"{name}.png"
    job.write_text(json.dumps({"width": w, "height": h, "scale": 2, "css": css, "fonts": fonts, "states": [{"file": str(png), "html": html}]}))
    subprocess.run(["node", str(R / "tools/htmlcaps/render.js"), str(job)], check=True, capture_output=True)
    Image.open(png).convert("RGB").save(D / f"{name}.jpg", quality=95); print(D / f"{name}.jpg")
