#!/usr/bin/env python3
"""Buttery Milk promo (owner's AI voice-over, ~21 s): light white "product-posts" theme (Noori + Montserrat, white
cards, product colours), owner's own goat clips in rounded windows, 28% MILK FAT counter + gauge, 34% PROTEIN gauge,
1 kg = 10 litre animation, growth graph, end card. Frames via tools/posts/anim_frames.js, mux via hgq_mux-style mix.

    python3 tools/posts/buttery_explainer.py [scale]     # frames -> work/frames
    python3 tools/posts/buttery_explainer.py --html-only
"""
import json, subprocess, sys
from pathlib import Path

R = Path(__file__).resolve().parents[2]
P = "buttery-vo"
D = R / "Video Edits/Export" / P; W = D / "work"; Q = W / "seq"
F = lambda g: str(next(R.joinpath("fonts").rglob(g)))
fonts = [{"family": "Noori", "path": F("JameelNooriNastaleeq-400.ttf"), "weight": 400, "style": "normal"},
         {"family": "Aslam", "path": F("Aslam-400.ttf"), "weight": 400, "style": "normal"},
         {"family": "Mehr", "path": F("MehrNastaliq-400.ttf"), "weight": 400, "style": "normal"},
         {"family": "Montserrat", "path": F("Montserrat-900.ttf"), "weight": 900, "style": "normal"},
         {"family": "Montserrat", "path": F("Montserrat-500.ttf"), "weight": 500, "style": "normal"}]
DUR = 21.02
RED, GREEN, BUT, INK, BLUE = "#D7232E", "#1E8A3A", "#F5B800", "#1B1B1F", "#1E3FA0"
goatpng = R / "assets/emoji/1f410.png"
bag = R / "Video Edits/Raw/butter-milk/butter-milk-bag-cutout-noprice.png"
S = [(0.0, 4.38), (4.38, 5.56), (5.56, 9.58), (9.58, 12.96), (12.96, 15.2), (15.2, 17.74), (17.74, DUR)]

css = f"""*{{margin:0;padding:0;box-sizing:border-box}}
@property --n {{ syntax:'<integer>'; inherits:false; initial-value:0 }}
#v{{position:absolute;inset:0;overflow:hidden;font-family:Montserrat;color:{INK};
  background:radial-gradient(ellipse 85% 55% at 50% 42%,#FFFFFF 0%,#F4F6F3 55%,#E3E9E2 100%)}}
.sheen{{position:absolute;inset:0;background:linear-gradient(115deg,transparent 42%,rgba(255,255,255,.6) 50%,transparent 58%)}}
@keyframes fin{{from{{opacity:0}}to{{opacity:1}}}} @keyframes fout{{from{{opacity:1}}to{{opacity:0}}}}
@keyframes up{{from{{opacity:0;translate:0 60px}}to{{opacity:1;translate:0 0}}}}
@keyframes pop{{0%{{opacity:0;scale:.4}}70%{{opacity:1;scale:1.08}}100%{{opacity:1;scale:1}}}}
@keyframes bag{{0%{{opacity:0;translate:0 300px;scale:.8}}100%{{opacity:1;translate:0 0;scale:1}}}}
@keyframes float{{from{{translate:0 0}}to{{translate:0 -14px}}}}
@keyframes count{{from{{--n:0}}to{{--n:var(--to)}}}}
@keyframes ring{{from{{stroke-dashoffset:1131}}to{{stroke-dashoffset:var(--off)}}}}
@keyframes draw{{from{{stroke-dashoffset:1600}}to{{stroke-dashoffset:0}}}}
@keyframes grow{{from{{scale:0}}to{{scale:1}}}}
@keyframes drip{{0%{{translate:0 -40px;opacity:0}}30%{{opacity:1}}100%{{translate:0 60px;opacity:0}}}}
.sc{{position:absolute;inset:0;opacity:0}}
.top{{position:absolute;top:150px;left:0;right:0;text-align:center;font:500 24px Montserrat;letter-spacing:8px;color:#77777d}} .top b{{font-weight:900;color:{INK}}} .top i{{font-style:normal;color:{RED}}}
.ur{{direction:rtl;text-align:center;font-family:Noori;color:#2a2a2e}}
.ur b{{font-family:Aslam;font-weight:400;color:{RED}}} .ur g{{color:{GREEN};font-family:Aslam}}
.en{{display:inline-block;direction:ltr;font:900 .46em Montserrat;color:#fff;background:{GREEN};border-radius:.3em;padding:.14em .45em;vertical-align:middle;letter-spacing:.05em;margin:0 .15em}}
.win{{position:absolute;border-radius:46px;overflow:hidden;border:8px solid #fff;box-shadow:0 30px 60px rgba(0,0,0,.18)}}
.win img{{width:100%;height:100%;object-fit:cover}}
.pill{{position:absolute;left:50%;translate:-50% 0;white-space:nowrap;background:{INK};color:#fff;border-radius:50px;padding:14px 32px;font:900 28px Montserrat;letter-spacing:2px;box-shadow:0 14px 30px rgba(0,0,0,.25)}}
.pill i{{font-style:normal;color:{BUT}}}
.cardw{{position:absolute;left:80px;right:80px;background:#fff;border-radius:44px;box-shadow:0 24px 60px rgba(0,0,0,.10);border:2px solid #E3E9E2}}
.num{{font:900 300px/1 Montserrat;letter-spacing:-10px;counter-reset:n var(--n);animation-fill-mode:both}} .num::before{{content:counter(n)}}
.credit{{position:absolute;left:50%;translate:-50% 0;display:flex;align-items:center;gap:16px;white-space:nowrap;background:#fff;border:4px solid {BUT};border-radius:60px;padding:2px 28px 8px;box-shadow:0 14px 30px rgba(0,0,0,.18);z-index:5}}
.credit .cu{{direction:rtl;font:400 48px/1.7 Mehr;color:{INK}}} .credit .ce{{font:900 19px Montserrat;letter-spacing:3px;color:#9a7a00;margin-top:8px}}
.bag{{position:absolute;filter:drop-shadow(0 30px 34px rgba(0,0,0,.25))}}
"""

def sc(k, inner):
    a, b = S[k]
    return f'<div class="sc" style="animation:fin .22s ease {a:.2f}s both,fout .2s ease {b - 0.2:.2f}s forwards">{inner}</div>'
def at(t, kind="up", d=0.45, extra=""):
    return f"animation:{kind} {d}s cubic-bezier(.2,.8,.2,1) {t:.2f}s both{extra}"
def seq(name, t0):
    n = len(list((Q / name).glob("*.jpg")))
    return f'data-seq="{Q / name}" data-start="{t0:.2f}" data-n="{n}" data-fps="30" src="file://{Q / name}/0001.jpg"'
en = lambda s: f'<span class="en">{s}</span>'
def credit(t, y, ur, enl):
    return (f'<div class="credit" style="top:{y}px;{at(t, "pop", .4)}"><span class="cu">{ur}</span><span class="ce">{enl}</span></div>')
NAVEED = ("نوید گوٹ فارم", "NAVEED GOAT FARM")
MAC = ("محمد احمد کیٹل فارم", "UMAIR NASEEM · MUHAMMAD AHMED CATTLE")
top = '<div class="top"><b>BUTTERY</b> <i>MILK</i> &nbsp;·&nbsp; CALF MILK REPLACER</div>'
def gauge(pct, col, t, label):
    off = 1131 * (1 - pct / 100)
    return (f'<svg viewBox="0 0 400 400" style="width:520px;height:520px"><circle cx="200" cy="200" r="180" fill="none" stroke="#EEF1EC" stroke-width="34"/>'
            f'<circle cx="200" cy="200" r="180" fill="none" stroke="{col}" stroke-width="34" stroke-linecap="round" stroke-dasharray="1131" '
            f'transform="rotate(-90 200 200)" style="--off:{off:.0f};animation:ring 1.3s cubic-bezier(.2,.8,.2,1) {t:.2f}s both"/></svg>')

sc_ = []
# 1 hook with goats drinking (owner's footage)
a, b = S[0]
sc_.append(sc(0, top +
    f'<div class="ur" style="position:absolute;top:220px;left:40px;right:40px;font-size:86px;line-height:1.7;{at(.05,"pop",.5)}">بکرا ہو یا بچھڑا، <b>وزن چاہیے؟</b></div>'
    f'<div class="win" style="left:110px;right:110px;top:470px;height:860px;{at(.15)}"><img {seq("G1", 0.0)}></div>' + credit(.5, 1290, *NAVEED) +
    f'<div class="ur" style="position:absolute;top:1385px;left:40px;right:40px;font-size:82px;line-height:1.7;{at(2.56,"pop")}">تو دودھ بھی <b>تگڑا</b> چاہیے!</div>'))
# 2 product reveal
a, b = S[1]
sc_.append(sc(1, top +
    f'<img class="bag" src="file://{bag}" style="left:50%;top:360px;height:900px;margin-left:-323px;{at(a,"bag",.5)}">'
    f'<div style="position:absolute;top:230px;left:0;right:0;text-align:center;font:900 104px Montserrat;letter-spacing:-3px;{at(a+.05,"pop")}">BUTTERY <span style="color:{RED}">MILK</span></div>'
    f'<div class="pill" style="top:1300px;{at(a+.3,"pop")}">PREMIUM QUALITY <i>BUTTER FAT</i></div>'))
# 3 28% MILK FAT (hero)
a, b = S[2]
drops = "".join(f'<div style="position:absolute;left:{x}px;top:250px;width:26px;height:36px;border-radius:50% 50% 50% 50%/60% 60% 40% 40%;background:{BUT};animation:drip 1.1s ease-in {a + .4 + d:.2f}s 3 both"></div>' for x, d in ((260, 0), (520, .35), (780, .7)))
sc_.append(sc(2, top +
    f'<div class="cardw" style="top:260px;height:900px;{at(a,"up",.4)}">'
    f'<div style="position:absolute;left:0;right:0;top:40px;display:flex;justify-content:center">{gauge(28, BUT, a + .25, "")}</div>'
    f'<div style="position:absolute;left:0;right:0;top:40px;height:520px;display:flex;align-items:center;justify-content:center;color:{INK}"><span class="num" style="--to:28;font-size:150px;letter-spacing:-6px;animation:count 1.3s cubic-bezier(.2,.8,.2,1) {a + .25:.2f}s both"></span><span style="font:900 80px Montserrat;margin-top:30px">%</span></div>'
    f'<div style="position:absolute;left:0;right:0;top:590px;text-align:center;font:900 92px Montserrat;letter-spacing:4px;color:{BUT};{at(a+.6,"pop")}">MILK FAT</div>'
    f'<div class="ur" style="position:absolute;left:0;right:0;top:700px;font-size:64px;line-height:1.6;{at(a+.9,"pop")}"><b style="color:#C98A00">ملک فیٹ</b> یعنی مکھن والی چکنائی</div>'
    f'{drops}</div>'
    f'<div class="ur" style="position:absolute;top:1210px;left:40px;right:40px;font-size:82px;line-height:1.7;{at(7.28,"pop")}"><b>بھرپور طاقت،</b> بھرا بھرا جانور!</div>'))
# 4 34% PROTEIN with muscular bull (Muhammad Ahmed Cattle, Umair Naseem bhai)
a, b = S[3]
sc_.append(sc(3, top +
    f'<div style="position:absolute;top:220px;left:0;right:0;display:flex;align-items:center;justify-content:center;gap:26px;{at(a,"up",.4)}">'
    f'<div><span class="num" style="--to:34;font-size:200px;color:{GREEN};animation:count 1.2s cubic-bezier(.2,.8,.2,1) {a + .2:.2f}s both"></span><span style="font:900 110px Montserrat;color:{GREEN}">%</span></div>'
    f'<div style="text-align:left"><div style="font:900 84px/1 Montserrat;letter-spacing:3px">PROTEIN</div><div class="ur" style="text-align:left;font-size:50px;line-height:1.5"><g>پروٹین</g> یعنی گوشت بنانے والا</div></div></div>'
    f'<div class="win" style="left:70px;right:70px;top:520px;height:620px;{at(a+.25)}"><img {seq("M", a)}></div>' + credit(a + .6, 1100, *MAC) +
    f'<div class="ur" style="position:absolute;top:1230px;left:40px;right:40px;font-size:90px;line-height:1.7;{at(11.44,"pop")}"><b>گوشت</b> اور <b>پٹھے!</b> 💪</div>'))
# 5 1 kg = 10 litre
a, b = S[4]
bottles = "".join(f'<div style="display:inline-block;margin:6px;{at(14.04 + i * .07, "pop", .3)}"><img src="file://{R}/assets/emoji/1f95b.png" style="width:86px;height:86px"></div>' for i in range(10))
sc_.append(sc(4, top +
    f'<div style="position:absolute;top:250px;left:0;right:0;display:flex;align-items:center;justify-content:center;gap:30px">'
    f'<img src="file://{bag}" style="height:420px;filter:drop-shadow(0 20px 24px rgba(0,0,0,.22));{at(a,"pop",.4)}">'
    f'<div style="font:900 110px Montserrat;color:{RED};{at(a+.3,"pop")}">=</div>'
    f'<div style="text-align:center;{at(14.04,"pop")}"><div style="font:900 200px/1 Montserrat;color:{BLUE}">10</div><div style="font:900 54px Montserrat;letter-spacing:6px">LITRE</div></div></div>'
    f'<div style="position:absolute;top:760px;left:110px;right:110px;text-align:center;background:#fff;border-radius:40px;padding:26px;box-shadow:0 20px 50px rgba(0,0,0,.1)">{bottles}</div>'
    f'<div class="ur" style="position:absolute;top:1120px;left:40px;right:40px;font-size:96px;line-height:1.7;{at(a+.15,"pop")}"><b>ایک کلو</b> پاؤڈر، <b>دس لیٹر</b> دودھ!</div>'
    f'<div class="pill" style="top:1350px;background:{GREEN};{at(a+.5,"pop")}">1 KG = <i>10 LITRE</i></div>'))
# 6 drinks eagerly, grows fast
a, b = S[5]
sc_.append(sc(5, top +
    f'<div class="win" style="left:150px;right:150px;top:230px;height:760px;{at(a+.05)}"><img {seq("G2", a)}></div>' + credit(a + .4, 950, *NAVEED) +
    f'<div class="cardw" style="top:1050px;height:280px;{at(16.76,"up",.4)}"><svg viewBox="0 0 900 300" style="width:100%;height:100%">'
    f'<path d="M60 250 C 300 235, 560 170, 840 50" fill="none" stroke="{RED}" stroke-width="14" stroke-linecap="round" stroke-dasharray="1600" style="animation:draw 1.1s ease-out {16.9:.2f}s both"/>'
    f'<text x="60" y="290" font-size="28" fill="#888" font-family="Montserrat">WEIGHT ↑</text>'
    f'<image href="file://{goatpng}" x="790" y="-10" width="90" height="90" style="{at(17.6,"pop",.3)}"/><image href="file://{goatpng}" x="30" y="200" width="46" height="46"/></svg></div>'
    f'<div class="ur" style="position:absolute;top:1340px;left:40px;right:40px;font-size:78px;line-height:1.7;{at(a+.1,"pop")}">جانور <b>شوق سے</b> پیئے، <g>تیزی سے</g> بڑھے!</div>'))
# 7 end card
a, b = S[6]
sc_.append(sc(6, top +
    f'<img class="bag" src="file://{bag}" style="left:50%;top:330px;height:880px;margin-left:-316px;{at(a,"bag",.5)},float 2s ease-in-out {a+.5:.2f}s infinite alternate">'
    f'<div style="position:absolute;top:210px;left:0;right:0;text-align:center;font:900 104px Montserrat;letter-spacing:-3px;{at(a,"pop")}">BUTTERY <span style="color:{RED}">MILK</span></div>'
    f'<div style="position:absolute;top:1150px;left:0;right:0;display:flex;justify-content:center;gap:18px;{at(a+.3,"pop")}">'
    f'<div class="pill" style="position:static;translate:none;background:{BUT};color:{INK}">28% MILK FAT</div><div class="pill" style="position:static;translate:none;background:{GREEN}">34% PROTEIN</div></div>'
    f'<div class="ur" style="position:absolute;top:1280px;left:40px;right:40px;font-size:92px;line-height:1.7;{at(18.92,"pop")}">قربانی کا جانور <b>بھرپور!</b></div>'))

html = f'<div id="v"><div class="sheen"></div>{"".join(sc_)}</div>'
W.mkdir(parents=True, exist_ok=True)
job = W / "anim-job.json"
job.write_text(json.dumps({"width": 1080, "height": 1920, "css": css, "fonts": fonts, "states": [{"file": "", "html": html}]}))
if "--html-only" in sys.argv:
    sys.exit(0)
subprocess.run(["rm", "-rf", str(W / "frames")])
subprocess.run(["node", str(R / "tools/posts/anim_frames.js"), str(job), str(W / "frames"), "30", str(DUR), sys.argv[1] if len(sys.argv) > 1 else "2"], check=True)
print("frames ok")
