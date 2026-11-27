#!/usr/bin/env python3
"""Heavy Gold qurbani explainer (owner's AI voice-over): animated Urdu scenes with animal photos, icons and simple
concept graphs, rendered frame by frame (tools/posts/anim_frames.js) at 4K and muxed with the tightened voice.

    python3 tools/posts/hgq_explainer.py            # frames + mux -> Export/hg-qurbani-vo/hg-qurbani-vo.mp4
"""
import json, subprocess, sys
from pathlib import Path

R = Path(__file__).resolve().parents[2]
P = "hg-qurbani-vo"
D = R / "Video Edits/Export" / P; W = D / "work"
F = lambda g: str(next(R.joinpath("fonts").rglob(g)))
fonts = [{"family": "Noori", "path": F("JameelNooriNastaleeq-400.ttf"), "weight": 400, "style": "normal"},
         {"family": "Aslam", "path": F("Aslam-400.ttf"), "weight": 400, "style": "normal"},
         {"family": "Montserrat", "path": F("Montserrat-900.ttf"), "weight": 900, "style": "normal"},
         {"family": "Montserrat", "path": F("Montserrat-500.ttf"), "weight": 500, "style": "normal"},
         {"family": "Mehr", "path": F("MehrNastaliq-400.ttf"), "weight": 400, "style": "normal"}]
DUR = 28.38
ST = R / "assets/stock"
def pick(cat, *names):
    for n in names:
        f = ST / cat / n
        if f.exists():
            return f
    fs = sorted((ST / cat).glob("*.jpg")) if (ST / cat).exists() else []
    return fs[0] if fs else None
goat1 = pick("goat", "boer-goat-49944899088.jpg", "boer-goat-50374051253.jpg") or R / "Video Edits/Raw/power-vimix/goat-kid.jpg"
goat2 = pick("goat", "beetal-ch-vre.jpg", "boer-goat-8742860752.jpg", "boer-goat-doe-clark-county.jpg") or goat1
goat3 = pick("goat", "boer-goat-8742860752.jpg", "boer-goat-doe-clark-county.jpg") or goat2
calf = pick("calf", "zebu-calf.jpg", "zebu-calf-33132314843.jpg") or pick("dairy-cow")
cow = pick("dairy-cow", "holstein-cow-and-calf.jpg", "a-dairy-cow-in-bemmel.jpg")
bull = pick("bull") or cow
hg = R / "Video Edits/Raw/heavy-gold/heavy-gold-bag-cutout.png"
NAVY, BLUE, GOLD = "#0E1F5E", "#1E3FA0", "#FFD400"

# scene timings (tightened voice)
S = [(0.0, 3.46), (3.46, 6.8), (6.8, 8.62), (8.62, 11.56), (11.56, 14.16), (14.16, 17.38), (17.38, 20.88),
     (20.88, 24.18), (24.18, 26.72), (26.72, DUR)]

css = f"""*{{margin:0;padding:0;box-sizing:border-box}}
#v{{position:absolute;inset:0;overflow:hidden;background:{NAVY};font-family:Montserrat}}
@keyframes fin{{from{{opacity:0}}to{{opacity:1}}}} @keyframes fout{{from{{opacity:1}}to{{opacity:0}}}}
@keyframes up{{from{{opacity:0;translate:0 60px}}to{{opacity:1;translate:0 0}}}}
@keyframes pop{{0%{{opacity:0;scale:.4}}70%{{opacity:1;scale:1.08}}100%{{opacity:1;scale:1}}}}
@keyframes kb{{from{{scale:1.08}}to{{scale:1.2}}}}
@keyframes grow{{from{{scale:1 0}}to{{scale:1 1}}}}
@keyframes draw{{from{{stroke-dashoffset:1600}}to{{stroke-dashoffset:0}}}}
@keyframes bag{{0%{{opacity:0;translate:0 300px;scale:.8}}100%{{opacity:1;translate:0 0;scale:1}}}}
@keyframes float{{from{{translate:0 0}}to{{translate:0 -16px}}}}
@keyframes shine{{from{{left:-40%}}to{{left:140%}}}}
.sc{{position:absolute;inset:0;opacity:0}}
.bg{{position:absolute;inset:-4%;width:108%;height:108%;object-fit:cover;filter:brightness(.62) saturate(1.15)}}
.grad{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(14,31,94,.55) 0%,rgba(14,31,94,.15) 35%,rgba(14,31,94,.2) 60%,rgba(14,31,94,.92) 100%)}}
.plain{{position:absolute;inset:0;background:radial-gradient(ellipse 90% 60% at 50% 40%,#2A55D6 0%,{BLUE} 45%,{NAVY} 100%)}}
.rays{{position:absolute;inset:0;background:repeating-linear-gradient(115deg,rgba(255,255,255,.04) 0 46px,transparent 46px 92px)}}
.ur{{direction:rtl;text-align:center;font-family:Noori;color:#fff;text-shadow:0 6px 20px rgba(0,0,0,.55)}}
.ur b{{font-family:Aslam;font-weight:400;color:{GOLD}}}
.en{{display:inline-block;direction:ltr;font:900 .5em Montserrat;color:{NAVY};background:{GOLD};border-radius:.3em;padding:.12em .42em;vertical-align:middle;letter-spacing:.04em;margin:0 .15em}}
.big{{position:absolute;left:50px;right:50px;font-size:96px;line-height:1.7}}
.mid{{position:absolute;left:60px;right:60px;font-size:70px;line-height:1.7}}
.card{{position:absolute;border-radius:44px;overflow:hidden;border:7px solid #fff;box-shadow:0 30px 60px rgba(0,0,0,.45)}}
.card img{{width:100%;height:100%;object-fit:cover}}
.chip{{position:absolute;display:flex;align-items:center;gap:16px;background:#fff;border-radius:60px;padding:14px 30px 14px 14px;box-shadow:0 16px 34px rgba(0,0,0,.35);font:900 34px Montserrat;color:{NAVY}}}
.chip i{{font-style:normal;width:72px;height:72px;border-radius:50%;background:{BLUE};display:flex;align-items:center;justify-content:center;font-size:40px}}
.hg{{position:absolute;filter:drop-shadow(0 30px 40px rgba(0,0,0,.5))}}
.panel{{position:absolute;left:70px;right:70px;background:rgba(255,255,255,.96);border-radius:40px;box-shadow:0 30px 60px rgba(0,0,0,.4);padding:40px}}
.panel h4{{direction:rtl;font:400 46px/1.6 Noori;color:{NAVY};text-align:right}} .panel h4 .en{{font-size:.6em}}
.axis{{stroke:#9aa3c7;stroke-width:4}} .lab{{font:500 26px Montserrat;fill:#6b7290}}
.credit{{position:absolute;left:50%;translate:-50% 0;display:flex;align-items:center;gap:18px;white-space:nowrap;background:linear-gradient(135deg,#FFFFFF,#F3F1EA);border:4px solid {GOLD};border-radius:60px;padding:4px 30px 10px;box-shadow:0 14px 30px rgba(0,0,0,.35);z-index:5}}
.credit .cu{{direction:rtl;font:400 50px/1.7 Mehr;color:{NAVY}}} .credit .ce{{font:900 20px Montserrat;letter-spacing:3px;color:#8a7a2a;margin-top:8px}}
.shine{{position:absolute;top:0;bottom:0;width:30%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.35),transparent);animation:shine 1.6s ease-in-out 1}}
"""

def sc(k, inner):
    a, b = S[k]
    return (f'<div class="sc" style="animation:fin .25s ease {a:.2f}s both,fout .2s ease {b - 0.2:.2f}s forwards">{inner}</div>')

def at(t, kind="up", d=0.45, extra=""):
    return f"animation:{kind} {d}s cubic-bezier(.2,.8,.2,1) {t:.2f}s both{extra}"

def bg(img, t0, t1):
    return f'<img class="bg" src="file://{img}" style="animation:kb {t1 - t0:.2f}s linear {t0:.2f}s both"><div class="grad"></div>'

en = lambda s: f'<span class="en">{s}</span>'
Q = W / "seq"
def seq(name, t0, extra=""):
    n = len(list((Q / name).glob("*.jpg")))
    return f'data-seq="{Q / name}" data-start="{t0:.2f}" data-n="{n}" data-fps="30" src="file://{Q / name}/0001.jpg" {extra}'
def clipcard(name, t0, x, y, w, h):
    return (f'<div class="card" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{at(t0 + .05, "pop", .45)}"><img {seq(name, t0)}></div>'
            + credit(t0 + .4, y + h - 34))
def clipbg(name, t0):
    return f'<img class="bg" {seq(name, t0)} style="filter:brightness(.5) saturate(1.15) blur(2px)"><div class="grad"></div>'
def credit(t, y):
    return (f'<div class="credit" style="top:{y}px;{at(t, "pop", .4)}"><span class="cu">محمد احمد کیٹل فارم</span>'
            f'<span class="ce">MUHAMMAD AHMED CATTLE FARM</span></div>')
scenes = []
# 1 hook
a, b = S[0]
scenes.append(sc(0, '<div class="plain"></div><div class="rays"></div>' + clipcard("A", 0.0, 150, 560, 780, 780) +
    f'<div class="ur big" style="top:170px;font-size:88px;{at(0.05,"pop",.5)}">منڈی میں سب سے پہلے<br><b>کون سا جانور</b> بکتا ہے؟</div>'
    f'<div class="ur big" style="top:1400px;font-size:100px;{at(2.5,"pop",.45)}"><b>جو بھرا ہوا ہو!</b></div>'))
# 2 eid countdown
a, b = S[1]
scenes.append(sc(1, '<div class="plain"></div><div class="rays"></div>' + clipcard("B", a, 90, 830, 900, 462) +
    f'<div class="chip" style="left:50%;top:300px;translate:-50% 0;{at(a+.05,"pop")}"><i>🌙</i>EID UL ADHA 2027</div>'
    f'<div class="ur mid" style="top:470px;font-size:84px;{at(a+.2)}">عید میں <b>چند مہینے</b> رہ گئے ہیں بھائی!</div>'
    f'<div style="position:absolute;left:120px;right:120px;top:740px;height:40px;border-radius:20px;background:rgba(255,255,255,.25);overflow:hidden;{at(a+.4,"fin",.3)}">'
    f'<div style="position:absolute;inset:0;background:linear-gradient(90deg,{GOLD},#FF9A3C);transform-origin:0 50%;animation:grow-x 2.2s ease-out {a+.5:.2f}s both"></div></div>'
    f'<div class="ur mid" style="top:1400px;font-size:92px;{at(5.64,"pop")}">ابھی سے <b>تیاری</b> کرو!</div>'))
css += "@keyframes grow-x{from{scale:0 1}to{scale:1 1}}"
# 3 heavy gold reveal
a, b = S[2]
icons = [("⚡", "BYPASS FAT"), ("🧫", "YEAST"), ("🦴", "DCP"), ("💊", "VITAMINS"), ("🧪", "MINERALS")]
ic = "".join(f'<div class="chip" style="left:{60 + (i % 2) * 480}px;top:{1180 + (i // 2) * 120}px;font-size:28px;{at(a + .55 + i * .14, "pop", .4)}"><i style="width:60px;height:60px;font-size:32px">{e}</i>{t}</div>' for i, (e, t) in enumerate(icons))
scenes.append(sc(2, '<div class="plain"></div><div class="rays"></div>'
    f'<img class="hg" src="file://{hg}" style="left:50%;top:260px;height:820px;margin-left:-275px;{at(a,"bag",.6)},float 2s ease-in-out {a+.6:.2f}s infinite alternate">'
    f'<div style="position:absolute;top:150px;left:0;right:0;text-align:center;font:900 92px Montserrat;color:#fff;letter-spacing:-2px;{at(a+.1,"pop")}">HEAVY <span style="color:{GOLD}">GOLD</span></div>'
    + ic + f'<div class="chip" style="right:60px;top:1420px;background:{GOLD};{at(a+.4,"pop")}"><i style="background:{NAVY};color:{GOLD};font-size:30px">5</i>5 IN 1</div>'))
# 4 C16 bypass fat: energy bars
a, b = S[3]
bars = "".join(f'<rect x="{80 + i * 130}" y="{360 - h}" width="90" height="{h}" rx="14" fill="{c}" style="transform-box:fill-box;transform-origin:50% 100%;animation:grow .7s cubic-bezier(.2,.8,.2,1) {a + .6 + i * .12:.2f}s both"/>'
               for i, (h, c) in enumerate([(110, "#c9cfe6"), (160, "#c9cfe6"), (230, GOLD), (300, GOLD)]))
scenes.append(sc(3, clipbg("D", a) + credit(a + .3, 1330) +
    f'<div class="ur mid" style="top:230px;font-size:80px;{at(a+.05,"pop")}"><b>سی سولہ بائی پاس فیٹ</b><br>{en("C16 BYPASS FAT")}</div>'
    f'<div class="panel" style="top:760px;height:560px;{at(a+.3)}"><h4>جانور میں <b style="color:{BLUE};font-family:Aslam;font-weight:400">طاقت</b> {en("ENERGY")} ⚡</h4>'
    f'<svg viewBox="0 0 640 400" style="width:100%;height:380px"><line class="axis" x1="50" y1="362" x2="620" y2="362"/>{bars}'
    f'<text class="lab" x="80" y="395">پہلے</text><text class="lab" x="470" y="395">ہیوی گولڈ کے ساتھ</text></svg></div>'))
# 5 yeast: flow diagram
a, b = S[4]
steps = [("🌾", "خوراک"), ("🧫", "ییسٹ"), ("💪", "جسم کو لگے")]
flow = "".join(f'<div style="position:absolute;top:0;left:{i * 330}px;width:280px;text-align:center;{at(a + .4 + i * .45, "pop", .4)}"><div style="font-size:120px">{e}</div>'
               f'<div class="ur" style="font-size:50px;color:{NAVY};text-shadow:none">{t}</div></div>' + (f'<div style="position:absolute;left:{i * 330 + 262}px;top:60px;font:900 70px Montserrat;color:{GOLD};{at(a + .6 + i * .45, "fin", .3)}">←</div>' if i < 2 else "")
               for i, (e, t) in enumerate(steps))
scenes.append(sc(4, bg(goat2, a, b) +
    f'<div class="ur mid" style="top:240px;font-size:84px;{at(a+.05,"pop")}"><b>ییسٹ</b> {en("YEAST")}</div>'
    f'<div class="panel" style="top:560px;height:470px;{at(a+.2)}"><div style="position:relative;direction:rtl;height:300px;margin:20px auto 0;width:920px">{flow}</div></div>'
    f'<div class="ur mid" style="top:1330px;font-size:90px;{at(12.5,"pop")}">جو کھائے، وہ <b>جسم کو لگے!</b></div>'))
# 6 DCP bones
a, b = S[5]
scenes.append(sc(5, '<div class="plain"></div><div class="rays"></div>' +
    clipcard("C", a, 90, 480, 900, 760) +
    f'<div class="ur mid" style="top:150px;font-size:84px;{at(a+.05,"pop")}"><b>ڈی سی پی</b> {en("DCP")}</div>'
    f'<div class="chip" style="left:50%;top:330px;translate:-50% 0;font-size:30px;{at(a+.5,"pop")}"><i>🦴</i>CALCIUM + PHOSPHORUS</div>'
    f'<div class="ur mid" style="top:1300px;font-size:78px;{at(14.92,"pop")}">مضبوط <b>ڈھانچہ</b>، تبھی تو چڑھے گا <b>گوشت!</b></div>'))
# 7 vitamins & minerals
a, b = S[6]
vm = ["VIT A", "VIT D3", "VIT E", "VIT B", "ZINC", "COPPER", "SELENIUM", "IODINE"]
grid = "".join(f'<div class="chip" style="left:{80 + (i % 2) * 480}px;top:{560 + (i // 2) * 120}px;font-size:30px;padding-right:26px;{at(a + .3 + i * .1, "pop", .35)}"><i style="width:56px;height:56px;font-size:28px;background:{BLUE if i < 4 else "#178A3B"}">{"💊" if i < 4 else "🧪"}</i>{t}</div>' for i, t in enumerate(vm))
scenes.append(sc(6, bg(goat1, a, b) +
    f'<div class="ur mid" style="top:220px;font-size:80px;{at(a+.05,"pop")}"><b>وٹامنز</b> اور <b>منرلز</b><br>{en("VITAMINS + MINERALS")}</div>'
    + grid + f'<div class="ur mid" style="top:1330px;font-size:86px;{at(18.68,"pop")}">کھال <b>چمکدار</b>، جانور <b>ہٹا کٹا!</b></div>'))
# 8 formula: fodder + grain + heavy gold
a, b = S[7]
eq = [("🌿", "چارہ", 21.5), ("+", "", 21.8), ("🌾", "دانہ", 21.96), ("+", "", 22.6)]
eqh = "".join(f'<div style="display:inline-block;vertical-align:middle;text-align:center;margin:0 10px;{at(t, "pop", .35)}"><div style="font-size:{130 if e != "+" else 90}px;color:{GOLD};font-weight:900">{e}</div>'
              f'<div class="ur" style="font-size:52px">{l}</div></div>' for e, l, t in eq)
scenes.append(sc(7, '<div class="plain"></div><div class="rays"></div>'
    f'<div class="ur mid" style="top:220px;font-size:84px;{at(a+.05,"pop")}">بس <b>چارہ دانہ</b> پورا دو</div>'
    f'<div style="position:absolute;top:560px;left:0;right:0;text-align:center;direction:rtl">{eqh}'
    f'<img src="file://{hg}" style="height:300px;vertical-align:middle;filter:drop-shadow(0 20px 30px rgba(0,0,0,.5));{at(23.26,"pop",.45)}"></div>'
    f'<div class="ur mid" style="top:1250px;font-size:90px;{at(22.74,"pop")}">اور ساتھ میں <b>ہیوی گولڈ!</b></div>'))
# 9 weight = rate graph
a, b = S[8]
scenes.append(sc(8, clipbg("E", a) + credit(a + .3, 1300) +
    f'<div class="ur mid" style="top:220px;font-size:100px;{at(a+.05,"pop")}"><b>وزن</b> ہے تو <b>ریٹ</b> ہے!</div>'
    f'<div class="panel" style="top:600px;height:640px;{at(a+.25)}"><h4>{en("WEIGHT")} وزن ↑ &nbsp; = &nbsp; ریٹ ↑ {en("PRICE")}</h4>'
    f'<svg viewBox="0 0 640 430" style="width:100%;height:440px"><line class="axis" x1="60" y1="380" x2="620" y2="380"/><line class="axis" x1="60" y1="20" x2="60" y2="380"/>'
    f'<path d="M60 360 C 220 340, 340 260, 600 60" fill="none" stroke="{GOLD}" stroke-width="16" stroke-linecap="round" stroke-dasharray="1600" style="animation:draw 1.6s ease-out {a+.6:.2f}s both"/>'
    f'<text class="lab" x="440" y="415">وزن (WEIGHT) →</text><text class="lab" x="70" y="40">ریٹ (PRICE)</text></svg></div>'))
# 10 end card
a, b = S[9]
scenes.append(sc(9, '<div class="plain"></div><div class="rays"></div>'
    f'<img class="hg" src="file://{hg}" style="left:50%;top:330px;height:860px;margin-left:-290px;{at(a,"bag",.5)}">'
    f'<div style="position:absolute;top:170px;left:0;right:0;text-align:center;font:900 96px Montserrat;color:#fff;letter-spacing:-2px;{at(a,"pop")}">HEAVY <span style="color:{GOLD}">GOLD</span></div>'
    f'<div class="ur big" style="top:1260px;font-size:112px;{at(a+.2,"pop")}">دودھ بھی، <b>گوشت بھی!</b></div>'))

html = f'<div id="v">{"".join(scenes)}</div>'
W.mkdir(parents=True, exist_ok=True)
job = W / "anim-job.json"
job.write_text(json.dumps({"width": 1080, "height": 1920, "css": css, "fonts": fonts, "states": [{"file": "", "html": html}]}))
if "--html-only" in sys.argv:
    sys.exit(0)
frames = W / "frames"
subprocess.run(["rm", "-rf", str(frames)])
subprocess.run(["node", str(R / "tools/posts/anim_frames.js"), str(job), str(frames), "30", str(DUR), sys.argv[1] if len(sys.argv) > 1 and sys.argv[1][0].isdigit() else "2"], check=True)
print("frames ok")
