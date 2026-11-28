#!/usr/bin/env python3
"""Milkolin Plus promo (owner's AI voice-over, ~26 s), light white post theme, Milkolin orange/brown palette.
Story: 10 kg cow drops to 2-3 kg after calving -> retained placenta (jer) -> Milkolin Plus (syrup) helps it out ->
back to HER OWN level (graph never goes above it) -> "not a milk-increasing syrup" card -> end card.
English words in brackets. Owner's photo library (assets/owner-library) with slow Ken Burns.

    python3 tools/posts/milkolin_explainer.py [scale] | --html-only
"""
import json, subprocess, sys
from pathlib import Path

R = Path(__file__).resolve().parents[2]
P = "milkolin-vo"
D = R / "Video Edits/Export" / P; W = D / "work"
L = R / "assets/owner-library"
F = lambda g: str(next(R.joinpath("fonts").rglob(g)))
fonts = [{"family": "Noori", "path": F("JameelNooriNastaleeq-400.ttf"), "weight": 400, "style": "normal"},
         {"family": "Aslam", "path": F("Aslam-400.ttf"), "weight": 400, "style": "normal"},
         {"family": "Montserrat", "path": F("Montserrat-900.ttf"), "weight": 900, "style": "normal"},
         {"family": "Montserrat", "path": F("Montserrat-500.ttf"), "weight": 500, "style": "normal"}]
DUR = 25.87
OR, BR, YE, INK, RED, GRN = "#E2780E", "#5A3A1E", "#F6C400", "#1B1B1F", "#D7232E", "#1E8A3A"
hd = R / "Video Edits/Raw/milkolin/milkolin-clean-cutout-hd.png"
bottle = hd if hd.exists() else R / "Video Edits/Raw/milkolin/milkolin-clean-cutout.png"
S = [(0.0, 4.18), (4.18, 7.98), (7.98, 9.24), (9.24, 13.46), (13.46, 16.32), (16.32, 22.88), (22.88, DUR)]

css = f"""*{{margin:0;padding:0;box-sizing:border-box}}
@property --n {{ syntax:'<integer>'; inherits:false; initial-value:0 }}
#v{{position:absolute;inset:0;overflow:hidden;font-family:Montserrat;color:{INK};
  background:radial-gradient(ellipse 85% 55% at 50% 42%,#FFFFFF 0%,#F7F3EE 55%,#EAE1D6 100%)}}
.sheen{{position:absolute;inset:0;background:linear-gradient(115deg,transparent 42%,rgba(255,255,255,.6) 50%,transparent 58%)}}
@keyframes fin{{from{{opacity:0}}to{{opacity:1}}}} @keyframes fout{{from{{opacity:1}}to{{opacity:0}}}}
@keyframes up{{from{{opacity:0;translate:0 60px}}to{{opacity:1;translate:0 0}}}}
@keyframes pop{{0%{{opacity:0;scale:.4}}70%{{opacity:1;scale:1.08}}100%{{opacity:1;scale:1}}}}
@keyframes bag{{0%{{opacity:0;translate:0 300px;scale:.8}}100%{{opacity:1;translate:0 0;scale:1}}}}
@keyframes float{{from{{translate:0 0}}to{{translate:0 -14px}}}}
@keyframes kb{{from{{scale:1.04}}to{{scale:1.16}}}}
@keyframes draw{{from{{stroke-dashoffset:2000}}to{{stroke-dashoffset:0}}}}
@keyframes drop{{0%{{opacity:0;translate:0 -30px}}100%{{opacity:1;translate:0 0}}}}
@keyframes strike{{from{{scale:0 1}}to{{scale:1 1}}}}
.sc{{position:absolute;inset:0;opacity:0}}
.top{{position:absolute;top:150px;left:0;right:0;text-align:center;font:500 24px Montserrat;letter-spacing:8px;color:#77777d}} .top b{{font-weight:900;color:{INK}}} .top i{{font-style:normal;color:{OR}}}
.ur{{position:absolute;left:40px;right:40px;direction:rtl;text-align:center;font-family:Noori;color:#2a2a2e;line-height:1.7}}
.ur b{{font-family:Aslam;font-weight:400;color:{OR}}} .ur r{{font-family:Aslam;color:{RED}}} .ur g{{font-family:Aslam;color:{GRN}}}
.en{{display:inline-block;direction:ltr;font:900 .42em Montserrat;color:#fff;background:{BR};border-radius:.3em;padding:.16em .45em;vertical-align:middle;letter-spacing:.05em;margin:0 .15em}}
.win{{position:absolute;border-radius:46px;overflow:hidden;border:8px solid #fff;box-shadow:0 30px 60px rgba(0,0,0,.18)}}
.win img{{width:100%;height:100%;object-fit:cover}}
.pill{{position:absolute;left:50%;translate:-50% 0;white-space:nowrap;background:{INK};color:#fff;border-radius:50px;padding:14px 32px;font:900 28px Montserrat;letter-spacing:2px;box-shadow:0 14px 30px rgba(0,0,0,.25)}}
.pill i{{font-style:normal;color:{YE}}}
.cardw{{position:absolute;left:80px;right:80px;background:#fff;border-radius:44px;box-shadow:0 24px 60px rgba(0,0,0,.10);border:2px solid #EAE1D6}}
.btl{{position:absolute;filter:drop-shadow(0 30px 34px rgba(0,0,0,.25))}}
"""

def sc(k, inner):
    a, b = S[k]
    return f'<div class="sc" style="animation:fin .22s ease {a:.2f}s both,fout .2s ease {b - 0.2:.2f}s forwards">{inner}</div>'
def at(t, kind="up", d=0.45, extra=""):
    return f"animation:{kind} {d}s cubic-bezier(.2,.8,.2,1) {t:.2f}s both{extra}"
def photo(f, a, b, pos="50% 50%"):
    return f'<img src="file://{L / f}" style="object-position:{pos};animation:kb {b - a:.2f}s linear {a:.2f}s both">'
en = lambda s: f'<span class="en">{s}</span>'
Q = W / "seq"
def clip(name, t0):
    n = len(list((Q / name).glob("*.jpg")))
    return f'<img data-seq="{Q / name}" data-start="{t0:.2f}" data-n="{n}" data-fps="30" src="file://{Q / name}/0001.jpg">'
top = '<div class="top"><b>MILKOLIN</b> <i>PLUS</i> &nbsp;·&nbsp; ORAL LIQUID</div>'

x = []
# 1 hook: 10 kg -> 2-3 kg
a, b = S[0]
x.append(sc(0, top +
    f'<div class="ur" style="top:210px;font-size:80px;{at(.05,"pop",.5)}">گائے <b>دس کلو</b> دودھ والی تھی</div>'
    f'<div class="win" style="left:110px;right:110px;top:420px;height:700px;{at(.1)}">{clip("K1", a)}</div>'
    f'<div style="position:absolute;top:1150px;left:0;right:0;display:flex;align-items:center;justify-content:center;gap:34px">'
    f'<div style="font:900 120px Montserrat;color:{GRN};{at(.5,"pop")}">10<span style="font-size:.45em"> KG</span></div>'
    f'<div style="font:900 110px Montserrat;color:{RED};{at(2.5,"drop",.4)}">→</div>'
    f'<div style="font:900 120px Montserrat;color:{RED};{at(2.66,"pop")}">2–3<span style="font-size:.45em"> KG</span></div></div>'
    f'<div class="ur" style="top:1320px;font-size:74px;{at(1.86,"pop")}">بیانے کے بعد <r>دو تین کلو</r> پر آ گئی؟</div>'))
# 2 problem: retained placenta
a, b = S[1]
x.append(sc(1, top +
    f'<div class="ur" style="top:230px;font-size:90px;{at(a+.05,"pop")}">مسئلہ <b>دودھ</b> کا نہیں بھائی!</div>'
    f'<div class="win" style="left:110px;right:110px;top:470px;height:640px;{at(a+.1)}">{photo("brahman-white-calves-1.jpg", a, b, "50% 30%")}</div>'
    f'<div class="ur" style="top:1150px;font-size:86px;{at(5.9,"pop")}">اندر رکا ہوا <r>جیر</r> {en("PLACENTA")}</div>'
    f'<div class="pill" style="top:1350px;background:{RED};{at(6.9,"pop")}">RETAINED <i>PLACENTA</i></div>'))
# 3 product reveal
a, b = S[2]
x.append(sc(2, top +
    f'<img class="btl" src="file://{bottle}" style="left:50%;top:330px;height:900px;margin-left:-140px;{at(a,"bag",.5)},float 2s ease-in-out {a+.5:.2f}s infinite alternate">'
    f'<div style="position:absolute;top:210px;left:0;right:0;text-align:center;font:900 104px Montserrat;letter-spacing:-3px;{at(a+.05,"pop")}">MILKOLIN <span style="color:{OR}">PLUS</span></div>'
    f'<div class="pill" style="top:1280px;{at(a+.3,"pop")}">POST-CALVING <i>SYRUP</i></div>'))
# 4 how: after calving, helps placenta out
a, b = S[3]
x.append(sc(3, top +
    f'<div class="win" style="left:110px;right:330px;top:260px;height:860px;{at(a+.05)}">{photo("brahman-white-calves-3.jpg", a, b, "50% 40%")}</div>'
    f'<img class="btl" src="file://{bottle}" style="right:70px;top:420px;height:700px;{at(a+.25,"bag",.5)}">'
    f'<div class="ur" style="top:1140px;font-size:74px;{at(a+.1,"pop")}"><b>تازہ بیائی ہوئی</b> گائے کو پلائیں<br>{en("AFTER CALVING")}</div>'
    f'<div class="ur" style="top:1360px;font-size:70px;{at(11.28,"pop")}"><r>جیر</r> باہر نکالنے میں <g>مدد</g> {en("PLACENTA")}</div>'))
# 5 back to her own level: graph never above the dashed "her level" line
a, b = S[4]
x.append(sc(4, top +
    f'<div class="win" style="left:110px;right:110px;top:240px;height:520px;{at(a+.05)}">{clip("K2", a)}</div>'
    f'<div class="cardw" style="top:800px;height:470px;{at(a+.15,"up",.4)}"><svg viewBox="0 0 920 470" style="width:100%;height:100%">'
    f'<line x1="70" y1="120" x2="880" y2="120" stroke="{GRN}" stroke-width="4" stroke-dasharray="16 12"/>'
    f'<text x="880" y="100" text-anchor="end" font-family="Montserrat" font-weight="900" font-size="26" fill="{GRN}">HER NORMAL MILK (اصل سطح)</text>'
    f'<path d="M70 140 C 160 140, 200 380, 300 380 C 420 380, 560 200, 860 122" fill="none" stroke="{OR}" stroke-width="14" stroke-linecap="round" stroke-dasharray="2000" style="animation:draw 1.8s ease-out {a + .5:.2f}s both"/>'
    f'<text x="300" y="430" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="26" fill="{RED}">AFTER CALVING 2–3 KG</text>'
    f'<text x="70" y="460" font-family="Montserrat" font-size="22" fill="#888">DAYS →</text></svg></div>'
    f'<div class="ur" style="top:1290px;font-size:76px;{at(13.84,"pop")}">واپس اپنی <g>اصل پیداوار</g> پر!<br>{en("ACTUAL MILK YIELD")}</div>'))
# 6 not a milk-increasing syrup
a, b = S[5]
row = lambda t, ok, txt, enl: (f'<div style="display:flex;align-items:center;gap:26px;direction:rtl;padding:26px 36px;{at(t, "pop", .45)}">'
    f'<div style="flex:none;width:92px;height:92px;border-radius:50%;background:{GRN if ok else RED};color:#fff;font:900 56px Montserrat;display:flex;align-items:center;justify-content:center">{"✓" if ok else "✕"}</div>'
    f'<div class="ur" style="position:static;text-align:right;font-size:70px;line-height:1.5">{txt}<br><span class="en" style="background:{GRN if ok else RED}">{enl}</span></div></div>')
x.append(sc(5, top +
    f'<div class="ur" style="top:220px;font-size:92px;{at(a+.05,"pop")}"><b>یاد رکھیں!</b></div>'
    f'<div class="cardw" style="top:470px;padding:30px 10px;{at(a+.2,"up",.4)}">'
    + row(16.9, False, "دودھ بڑھانے کا سیرپ", "NOT A MILK BOOSTER") +
    f'<div style="height:2px;background:#EAE1D6;margin:6px 40px"></div>'
    + row(18.84, True, "اپنے پورے دودھ پر واپسی میں مددگار", "BACK TO HER OWN LEVEL") +
    '</div>'
    f'<div class="win" style="left:200px;right:200px;top:1060px;height:300px;{at(19.3)}">{photo("cows-field.jpg", a, b, "55% 35%")}</div>'))
# 7 end card
a, b = S[6]
x.append(sc(6, top +
    f'<img class="btl" src="file://{bottle}" style="left:50%;top:320px;height:880px;margin-left:-137px;{at(a,"bag",.5)},float 2s ease-in-out {a+.5:.2f}s infinite alternate">'
    f'<div style="position:absolute;top:200px;left:0;right:0;text-align:center;font:900 104px Montserrat;letter-spacing:-3px;{at(a,"pop")}">MILKOLIN <span style="color:{OR}">PLUS</span></div>'
    f'<div style="position:absolute;top:1220px;left:0;right:0;display:flex;justify-content:center;gap:18px;{at(a+.25,"pop")}">'
    f'<div class="pill" style="position:static;translate:none;background:{OR}">ORAL LIQUID</div><div class="pill" style="position:static;translate:none;background:{BR}">1 LITRE</div></div>'
    f'<div class="ur" style="top:1330px;font-size:92px;{at(24.12,"pop")}">بیانے کے بعد کا <b>ساتھی!</b></div>'))

html = f'<div id="v"><div class="sheen"></div>{"".join(x)}</div>'
W.mkdir(parents=True, exist_ok=True)
job = W / "anim-job.json"
job.write_text(json.dumps({"width": 1080, "height": 1920, "css": css, "fonts": fonts, "states": [{"file": "", "html": html}]}))
if "--html-only" in sys.argv:
    sys.exit(0)
subprocess.run(["rm", "-rf", str(W / "frames")])
subprocess.run(["node", str(R / "tools/posts/anim_frames.js"), str(job), str(W / "frames"), "30", str(DUR), sys.argv[1] if len(sys.argv) > 1 else "2"], check=True)
print("frames ok")
