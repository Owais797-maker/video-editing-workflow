#!/usr/bin/env python3
"""Life Gripe Water promo (owner's AI voice-over, ~13 s, sharp cuts), light white post theme, Life Gripe Water blue/green.
Owner's farm clips (Video Edits/Raw/library-gripe-water, see SHOTS.md) as image sequences in rounded windows.
Key message on screen: MIX IN WATER (paani mein mila kar pilayen).

    python3 tools/posts/gripe_explainer.py [scale] | --html-only
"""
import json, subprocess, sys
from pathlib import Path

R = Path(__file__).resolve().parents[2]
P = "gripe-vo"
D = R / "Video Edits/Export" / P; W = D / "work"; Q = W / "seq"
F = lambda g: str(next(R.joinpath("fonts").rglob(g)))
fonts = [{"family": "Noori", "path": F("JameelNooriNastaleeq-400.ttf"), "weight": 400, "style": "normal"},
         {"family": "Aslam", "path": F("Aslam-400.ttf"), "weight": 400, "style": "normal"},
         {"family": "Montserrat", "path": F("Montserrat-900.ttf"), "weight": 900, "style": "normal"},
         {"family": "Montserrat", "path": F("Montserrat-500.ttf"), "weight": 500, "style": "normal"}]
DUR = 13.02
BLUE, NAVY, GRN, RED, INK = "#1F4AA8", "#0F2A6B", "#2E9B3A", "#D7232E", "#1B1B1F"
hd = R / "Video Edits/Raw/bacha-hairan/gripe-water-mockup-cutout-hd.png"
bottle = hd if hd.exists() else R / "Video Edits/Raw/bacha-hairan/gripe-water-mockup-cutout.png"
E = lambda c: R / "assets/emoji" / c
S = [(0.0, 2.26), (2.26, 4.6), (4.6, 5.68), (5.68, 8.16), (8.16, 9.8), (9.8, DUR)]

css = f"""*{{margin:0;padding:0;box-sizing:border-box}}
#v{{position:absolute;inset:0;overflow:hidden;font-family:Montserrat;color:{INK};
  background:radial-gradient(ellipse 85% 55% at 50% 42%,#FFFFFF 0%,#F1F5FA 55%,#DCE5F0 100%)}}
.sheen{{position:absolute;inset:0;background:linear-gradient(115deg,transparent 42%,rgba(255,255,255,.6) 50%,transparent 58%)}}
@keyframes fin{{from{{opacity:0}}to{{opacity:1}}}} @keyframes fout{{from{{opacity:1}}to{{opacity:0}}}}
@keyframes up{{from{{opacity:0;translate:0 60px}}to{{opacity:1;translate:0 0}}}}
@keyframes pop{{0%{{opacity:0;scale:.4}}70%{{opacity:1;scale:1.08}}100%{{opacity:1;scale:1}}}}
@keyframes bag{{0%{{opacity:0;translate:0 300px;scale:.8}}100%{{opacity:1;translate:0 0;scale:1}}}}
@keyframes float{{from{{translate:0 0}}to{{translate:0 -14px}}}}
@keyframes ripple{{0%{{opacity:.8;scale:.2}}100%{{opacity:0;scale:1.6}}}}
.sc{{position:absolute;inset:0;opacity:0}}
.top{{position:absolute;top:150px;left:0;right:0;text-align:center;font:500 24px Montserrat;letter-spacing:8px;color:#77777d}} .top b{{font-weight:900;color:{INK}}} .top i{{font-style:normal;color:{BLUE}}}
.ur{{position:absolute;left:40px;right:40px;direction:rtl;text-align:center;font-family:Noori;color:#2a2a2e;line-height:1.7}}
.ur b{{font-family:Aslam;font-weight:400;color:{BLUE}}} .ur r{{font-family:Aslam;color:{RED}}} .ur g{{font-family:Aslam;color:{GRN}}}
.en{{display:inline-block;direction:ltr;font:900 .42em Montserrat;color:#fff;background:{NAVY};border-radius:.3em;padding:.16em .45em;vertical-align:middle;letter-spacing:.05em;margin:0 .15em}}
.win{{position:absolute;border-radius:46px;overflow:hidden;border:8px solid #fff;box-shadow:0 30px 60px rgba(0,0,0,.18)}}
.win img{{width:100%;height:100%;object-fit:cover}}
.pill{{position:absolute;left:50%;translate:-50% 0;white-space:nowrap;background:{INK};color:#fff;border-radius:50px;padding:14px 32px;font:900 30px Montserrat;letter-spacing:2px;box-shadow:0 14px 30px rgba(0,0,0,.25)}}
.pill i{{font-style:normal;color:#8FD3FF}}
.chip{{display:flex;align-items:center;gap:18px;background:#fff;border-radius:60px;padding:14px 34px 14px 14px;box-shadow:0 16px 34px rgba(0,0,0,.14);font:900 34px Montserrat;color:{NAVY}}}
.chip img{{width:72px;height:72px}}
.btl{{position:absolute;filter:drop-shadow(0 30px 34px rgba(0,0,0,.25))}}
"""

def sc(k, inner):
    a, b = S[k]
    return f'<div class="sc" style="animation:fin .18s ease {a:.2f}s both,fout .16s ease {b - 0.16:.2f}s forwards">{inner}</div>'
def at(t, kind="up", d=0.4, extra=""):
    return f"animation:{kind} {d}s cubic-bezier(.2,.8,.2,1) {t:.2f}s both{extra}"
def clip(name, t0):
    n = len(list((Q / name).glob("*.jpg")))
    return f'<img data-seq="{Q / name}" data-start="{t0:.2f}" data-n="{n}" data-fps="30" src="file://{Q / name}/0001.jpg">'
en = lambda s: f'<span class="en">{s}</span>'
top = '<div class="top"><b>LIFE</b> <i>GRIPE WATER</i> &nbsp;·&nbsp; ORAL LIQUID</div>'
x = []
# 1 hook
a, b = S[0]
x.append(sc(0, top +
    f'<div class="ur" style="top:210px;font-size:84px;{at(.03,"pop",.4)}">جانور <r>چارہ چھوڑ</r> رہا ہے؟</div>'
    f'<div class="win" style="left:110px;right:110px;top:420px;height:780px;{at(.05)}">{clip("F", 0.0)}</div>'
    f'<div class="ur" style="top:1240px;font-size:96px;{at(1.32,"pop")}"><r>پیٹ پھولا</r> ہوا ہے؟</div>'))
# 2 fix digestion first
a, b = S[1]
flow = "".join(
    f'<div style="display:inline-block;vertical-align:middle;text-align:center;margin:0 14px;{at(a + .2 + i * .25, "pop", .35)}">'
    f'<img src="file://{E(c)}" style="width:120px;height:120px"><div class="ur" style="position:static;font-size:44px">{t}</div></div>'
    + (f'<span style="display:inline-block;vertical-align:middle;font:900 70px Montserrat;color:{BLUE};margin-top:-50px;{at(a + .32 + i * .25, "fin", .2)}">←</span>' if i < 2 else "")
    for i, (c, t) in enumerate([("1f33e.png", "خوراک"), ("1f9eb.png", "ہاضمہ"), ("1f4aa.png", "طاقت")]))
x.append(sc(1, top +
    f'<div class="win" style="left:150px;right:150px;top:230px;height:640px;{at(a+.03)}">{clip("B", a)}</div>'
    f'<div style="position:absolute;top:910px;left:80px;right:80px;background:#fff;border-radius:40px;padding:26px 10px 14px;text-align:center;direction:rtl;box-shadow:0 20px 50px rgba(0,0,0,.1);{at(a+.1)}">{flow}</div>'
    f'<div class="ur" style="top:1240px;font-size:90px;{at(a+.05,"pop")}">پہلے <b>ہاضمہ</b> ٹھیک کرو بھائی! {en("DIGESTION")}</div>'))
# 3 product: real bottle close-up + title
a, b = S[2]
x.append(sc(2, top +
    f'<div style="position:absolute;top:210px;left:0;right:0;text-align:center;font:900 100px Montserrat;letter-spacing:-3px;{at(a,"pop",.35)}">LIFE <span style="color:{BLUE}">GRIPE WATER</span></div>'
    f'<div class="win" style="left:150px;right:150px;top:380px;height:820px;{at(a+.02,"pop",.35)}">{clip("P", a)}</div>'
    f'<div class="pill" style="top:1250px;{at(a+.2,"pop")}">5 LITRES · <i>ORAL LIQUID</i></div>'))
# 4 benefits
a, b = S[3]
x.append(sc(3, top +
    f'<img class="btl" src="file://{bottle}" style="left:50%;top:250px;height:720px;margin-left:-205px;{at(a,"bag",.45)},float 2s ease-in-out {a+.45:.2f}s infinite alternate">'
    f'<div style="position:absolute;top:1010px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:22px">'
    f'<div class="chip" style="{at(a+.05,"pop")}"><img src="file://{E("1f4a8.png")}">GAS / BLOAT <span style="font-family:Noori;font-weight:400;font-size:40px;color:{INK}">(افارہ)</span></div>'
    f'<div class="chip" style="{at(7.26,"pop")}"><img src="file://{E("1f60b.png")}">APPETITE <span style="font-family:Noori;font-weight:400;font-size:40px;color:{INK}">(بھوک)</span></div></div>'
    f'<div class="ur" style="top:1290px;font-size:78px;{at(a+.2,"pop")}"><b>گیس اور افارے</b> میں آرام، <g>بھوک کھلے!</g></div>'))
# 5 mix in water (owner's real pouring shot)
a, b = S[4]
x.append(sc(4, top +
    f'<div class="ur" style="top:200px;font-size:92px;{at(a+.02,"pop",.35)}">بس <b>پانی میں ملا کر</b> پلائیں!</div>'
    f'<div class="win" style="left:110px;right:110px;top:430px;height:820px;{at(a+.03)}">{clip("M", a)}</div>'
    f'<div class="pill" style="top:1290px;background:{BLUE};font-size:40px;{at(a+.25,"pop")}">💧 MIX IN <i>WATER</i></div>'))
# 6 end card
a, b = S[5]
x.append(sc(5, top +
    f'<img class="btl" src="file://{bottle}" style="left:50%;top:300px;height:860px;margin-left:-245px;{at(a,"bag",.45)},float 2s ease-in-out {a+.45:.2f}s infinite alternate">'
    f'<div style="position:absolute;top:200px;left:0;right:0;text-align:center;font:900 100px Montserrat;letter-spacing:-3px;{at(a,"pop")}">LIFE <span style="color:{BLUE}">GRIPE WATER</span></div>'
    f'<div class="ur" style="top:1210px;font-size:96px;{at(10.94,"pop")}"><b>ہاضمہ درست،</b></div>'
    f'<div class="ur" style="top:1350px;font-size:96px;{at(11.8,"pop")}">جانور <g>تندرست!</g></div>'))

html = f'<div id="v"><div class="sheen"></div>{"".join(x)}</div>'
W.mkdir(parents=True, exist_ok=True)
job = W / "anim-job.json"
job.write_text(json.dumps({"width": 1080, "height": 1920, "css": css, "fonts": fonts, "states": [{"file": "", "html": html}]}))
if "--html-only" in sys.argv:
    sys.exit(0)
subprocess.run(["rm", "-rf", str(W / "frames")])
subprocess.run(["node", str(R / "tools/posts/anim_frames.js"), str(job), str(W / "frames"), "30", str(DUR), sys.argv[1] if len(sys.argv) > 1 else "2"], check=True)
print("frames ok")
