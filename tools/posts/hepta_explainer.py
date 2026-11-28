#!/usr/bin/env python3
"""Hepta Sef promo (owner's AI voice-over, ~24 s, sharp cuts), "khata bohat, lagta nahi" scolding style.
Light white post theme in Hepta Sef purple + yellow. Benefits only (APPETITE / DIGESTION / LIVER / WEIGHT GAIN),
"kitna khaya X / kitna laga OK" card, mandi ending, dose cards (goat / calf / milking cow-buffalo with approx weights).
Clips: owner's Pinterest picks (Video Edits/Raw/hepta-vo/pin) as image sequences.

    python3 tools/posts/hepta_explainer.py [scale] | --html-only
"""
import json, subprocess, sys
from pathlib import Path

R = Path(__file__).resolve().parents[2]
P = "hepta-vo"
D = R / "Video Edits/Export" / P; W = D / "work"; Q = W / "seq"
F = lambda g: str(next(R.joinpath("fonts").rglob(g)))
fonts = [{"family": "Noori", "path": F("JameelNooriNastaleeq-400.ttf"), "weight": 400, "style": "normal"},
         {"family": "Aslam", "path": F("Aslam-400.ttf"), "weight": 400, "style": "normal"},
         {"family": "Montserrat", "path": F("Montserrat-900.ttf"), "weight": 900, "style": "normal"},
         {"family": "Montserrat", "path": F("Montserrat-500.ttf"), "weight": 500, "style": "normal"}]
DUR = 23.76
PUR, PUD, YEL, RED, GRN, INK = "#7B2C8F", "#4A1458", "#F2C400", "#D7232E", "#1E8A3A", "#1B1B1F"
hd = R / "Video Edits/Raw/three-products/hepta-sef-cutout-hd.png"
bottle = hd if hd.exists() else R / "Video Edits/Raw/three-products/hepta-sef-cutout.png"
E = lambda c: R / "assets/emoji" / c
S = [(0.0, 2.9), (2.9, 5.94), (5.94, 7.78), (7.78, 9.66), (9.66, 11.92), (11.92, 14.08), (14.08, 16.04),
     (16.04, 18.54), (18.54, 21.26), (21.26, DUR)]

css = f"""*{{margin:0;padding:0;box-sizing:border-box}}
#v{{position:absolute;inset:0;overflow:hidden;font-family:Montserrat;color:{INK};
  background:radial-gradient(ellipse 85% 55% at 50% 42%,#FFFFFF 0%,#F6F1F8 55%,#E7DCEC 100%)}}
.sheen{{position:absolute;inset:0;background:linear-gradient(115deg,transparent 42%,rgba(255,255,255,.6) 50%,transparent 58%)}}
@keyframes fin{{from{{opacity:0}}to{{opacity:1}}}} @keyframes fout{{from{{opacity:1}}to{{opacity:0}}}}
@keyframes up{{from{{opacity:0;translate:0 60px}}to{{opacity:1;translate:0 0}}}}
@keyframes pop{{0%{{opacity:0;scale:.4}}70%{{opacity:1;scale:1.08}}100%{{opacity:1;scale:1}}}}
@keyframes bag{{0%{{opacity:0;translate:0 300px;scale:.8}}100%{{opacity:1;translate:0 0;scale:1}}}}
@keyframes float{{from{{translate:0 0}}to{{translate:0 -14px}}}}
@keyframes shake{{0%,100%{{rotate:0deg}}25%{{rotate:-4deg}}75%{{rotate:4deg}}}}
@keyframes pile{{from{{scale:1 .2}}to{{scale:1 1}}}}
.sc{{position:absolute;inset:0;opacity:0}}
.top{{position:absolute;top:150px;left:0;right:0;text-align:center;font:500 24px Montserrat;letter-spacing:8px;color:#77777d}} .top b{{font-weight:900;color:{INK}}} .top i{{font-style:normal;color:{PUR}}}
.ur{{position:absolute;left:40px;right:40px;direction:rtl;text-align:center;font-family:Noori;color:#2a2a2e;line-height:1.7}}
.ur b{{font-family:Aslam;font-weight:400;color:{PUR}}} .ur r{{font-family:Aslam;color:{RED}}} .ur g{{font-family:Aslam;color:{GRN}}}
.en{{display:inline-block;direction:ltr;font:900 .42em Montserrat;color:{INK};background:{YEL};border-radius:.3em;padding:.16em .45em;vertical-align:middle;letter-spacing:.05em;margin:0 .15em}}
.win{{position:absolute;border-radius:46px;overflow:hidden;border:8px solid #fff;box-shadow:0 30px 60px rgba(0,0,0,.18)}}
.win img{{width:100%;height:100%;object-fit:cover}}
.pill{{position:absolute;left:50%;translate:-50% 0;white-space:nowrap;background:{PUR};color:#fff;border-radius:50px;padding:14px 32px;font:900 30px Montserrat;letter-spacing:2px;box-shadow:0 14px 30px rgba(0,0,0,.25)}}
.pill i{{font-style:normal;color:{YEL}}}
.chip{{display:flex;align-items:center;gap:18px;background:#fff;border-radius:60px;padding:12px 32px 12px 12px;box-shadow:0 16px 34px rgba(0,0,0,.14);font:900 34px Montserrat;color:{PUD}}}
.chip img{{width:68px;height:68px}}
.cardw{{position:absolute;left:80px;right:80px;background:#fff;border-radius:44px;box-shadow:0 24px 60px rgba(0,0,0,.10);border:2px solid #E7DCEC}}
.btl{{position:absolute;filter:drop-shadow(0 30px 34px rgba(0,0,0,.25))}}
.dose{{flex:1;background:#fff;border-radius:30px;padding:16px 8px 14px;text-align:center;box-shadow:0 14px 30px rgba(0,0,0,.10);border-top:8px solid {PUR}}}
.dose img{{width:84px;height:84px}} .dose b{{display:block;font:900 48px Montserrat;color:{PUR};margin-top:4px}}
.dose small{{display:block;font:900 17px Montserrat;letter-spacing:1px;color:#6b6b72}} .dose span{{display:block;direction:rtl;font:40px/1.6 Noori;color:{INK}}}
"""

def sc(k, inner):
    a, b = S[k]
    return f'<div class="sc" style="animation:fin .16s ease {a:.2f}s both,fout .14s ease {b - 0.14:.2f}s forwards">{inner}</div>'
def at(t, kind="up", d=0.38, extra=""):
    return f"animation:{kind} {d}s cubic-bezier(.2,.8,.2,1) {t:.2f}s both{extra}"
def clip(name, t0):
    n = len(list((Q / name).glob("*.jpg")))
    return f'<img data-seq="{Q / name}" data-start="{t0:.2f}" data-n="{n}" data-fps="30" src="file://{Q / name}/0001.jpg">'
en = lambda s: f'<span class="en">{s}</span>'
top = '<div class="top"><b>LIFE</b> <i>HEPTA SEF</i> &nbsp;·&nbsp; ORAL LIQUID</div>'
x = []
# 1 hook: eats a lot, doesn't show
a, b = S[0]
x.append(sc(0, top +
    f'<div class="ur" style="top:200px;font-size:96px;{at(.02,"pop",.35)}">جانور <b>کھاتا بہت</b> ہے،</div>'
    f'<div class="win" style="left:110px;right:110px;top:450px;height:760px;{at(.04)}">{clip("E1", 0.0)}</div>'
    f'<div class="ur" style="top:1240px;font-size:104px;{at(1.5,"pop")}">پر <r>لگتا نہیں؟</r></div>'))
# 2 and you keep feeding more
a, b = S[1]
x.append(sc(1, top +
    f'<div class="win" style="left:110px;right:110px;top:230px;height:760px;{at(a+.03)}">{clip("E2", a)}</div>'
    f'<div style="position:absolute;top:1010px;left:0;right:0;display:flex;justify-content:center;gap:24px;{at(a+.4,"pop")}">'
    + "".join(f'<img src="file://{E("1f33e.png")}" style="width:{90 + i * 18}px;height:{90 + i * 18}px;transform-origin:50% 100%;animation:pile .3s ease-out {a + .4 + i * .18:.2f}s both">' for i in range(4)) +
    f'</div><div class="ur" style="top:1180px;font-size:78px;{at(a+.05,"pop")}">اور آپ ہو کہ اسے<br><r>اور زیادہ</r> کھلانے پر تلے ہوئے ہو!</div>'))
# 3 won't work
a, b = S[2]
x.append(sc(2, top +
    f'<div style="position:absolute;top:420px;left:50%;margin-left:-210px;width:420px;height:420px;border-radius:50%;background:{RED};color:#fff;font:900 300px/420px Montserrat;text-align:center;box-shadow:0 30px 60px rgba(215,35,46,.35);{at(a,"pop",.35)},shake .4s ease {a+.35:.2f}s 2">✕</div>'
    f'<div class="ur" style="top:960px;font-size:100px;{at(a+.1,"pop")}">ایسے <r>کام نہیں</r> چلے گا بھائی!</div>'))
# 4 Hepta Sef
a, b = S[3]
x.append(sc(3, top +
    f'<img class="btl" src="file://{bottle}" style="left:50%;top:330px;height:860px;margin-left:-240px;{at(a,"bag",.4)},float 2s ease-in-out {a+.4:.2f}s infinite alternate">'
    f'<div style="position:absolute;top:200px;left:0;right:0;text-align:center;font:900 110px Montserrat;letter-spacing:-3px;{at(a,"pop")}">HEPTA <span style="color:{PUR}">SEF</span></div>'
    f'<div class="ur" style="top:1220px;font-size:88px;{at(a+.15,"pop")}"><b>ہیپٹا سیف</b> پلانا پڑے گا!</div>'))
# 5 appetite + digestion (+ liver)
a, b = S[4]
chips = [("1f60b.png", "APPETITE", "بھوک", a + .05), ("1f9eb.png", "DIGESTION", "ہاضمہ", 10.6), ("1fac1.png", "LIVER", "جگر", 11.1)]
x.append(sc(4, top +
    f'<img class="btl" src="file://{bottle}" style="left:50%;top:240px;height:560px;margin-left:-156px;{at(a,"bag",.35)}">'
    f'<div style="position:absolute;top:850px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:20px">'
    + "".join(f'<div class="chip" style="{at(t, "pop")}"><img src="file://{E(c)}">{e} <span style="font-family:Noori;font-weight:400;font-size:40px;color:{INK}">({u})</span></div>' for c, e, u, t in chips) +
    f'</div><div class="ur" style="top:1290px;font-size:74px;{at(a+.1,"pop")}"><g>بھوک</g> بھی کھلے گی، <b>ہاضمہ</b> بھی اچھا!</div>'))
# 6 what it eats will show
a, b = S[5]
flow = "".join(
    f'<div style="display:inline-block;vertical-align:middle;text-align:center;margin:0 10px;{at(a + .1 + i * .25, "pop", .3)}">'
    f'<img src="file://{E(c)}" style="width:116px;height:116px"><div style="font:900 24px Montserrat;color:{PUD}">{t}</div></div>'
    + (f'<span style="display:inline-block;vertical-align:middle;font:900 64px Montserrat;color:{PUR};margin-top:-36px;{at(a + .2 + i * .25, "fin", .2)}">→</span>' if i < 2 else "")
    for i, (c, t) in enumerate([("1f33e.png", "FEED"), ("1f9eb.png", "DIGESTION"), ("1f4aa.png", "WEIGHT")]))
x.append(sc(5, top +
    f'<div class="win" style="left:150px;right:150px;top:230px;height:720px;{at(a+.03)}">{clip("BR", a)}</div>'
    f'<div style="position:absolute;top:990px;left:80px;right:80px;background:#fff;border-radius:40px;padding:22px 10px 14px;text-align:center;box-shadow:0 20px 50px rgba(0,0,0,.1);{at(a+.05)}">{flow}</div>'
    f'<div class="ur" style="top:1250px;font-size:84px;{at(a+.1,"pop")}">جو کھائے گا، وہ <g>لگے گا بھی!</g></div>'))
# 7+8 the real kamal: X kitna khaya / OK kitna laga
a, b = S[6]
a2, b2 = S[7]
row = lambda t, ok, txt, enl: (f'<div style="display:flex;align-items:center;gap:26px;direction:rtl;padding:24px 36px;{at(t, "pop", .38)}">'
    f'<div style="flex:none;width:96px;height:96px;border-radius:50%;background:{GRN if ok else RED};color:#fff;font:900 58px Montserrat;display:flex;align-items:center;justify-content:center">{"✓" if ok else "✕"}</div>'
    f'<div class="ur" style="position:static;text-align:right;font-size:78px;line-height:1.4">{txt}<br><span class="en" style="background:{GRN if ok else RED};color:#fff">{enl}</span></div></div>')
x.append(f'<div class="sc" style="animation:fin .16s ease {a:.2f}s both,fout .14s ease {b2 - 0.14:.2f}s forwards">' + top +
    f'<div class="ur" style="top:210px;font-size:96px;{at(a+.02,"pop")}"><b>اصل کمال</b> کیا ہے؟</div>'
    f'<div class="cardw" style="top:460px;padding:26px 10px;{at(a+.1,"up",.35)}">' + row(a + .2, False, "کتنا کھا رہا ہے", "HOW MUCH IT EATS") +
    '<div style="height:2px;background:#E7DCEC;margin:6px 40px"></div>' + row(a2 + .05, True, "کتنا لگ رہا ہے!", "HOW MUCH IT GAINS") + '</div>'
    f'<div class="win" style="left:200px;right:200px;top:1060px;height:330px;{at(a2+.1)}">{clip("BR", a2 - 2.0)}</div></div>')
# 9 mandi: won't sell
a, b = S[8]
x.append(sc(8, top +
    f'<div class="ur" style="top:200px;font-size:88px;{at(a+.02,"pop")}">جانور <r>بنے گا نہیں،</r></div>'
    f'<div class="win" style="left:110px;right:110px;top:420px;height:780px;{at(a+.03)}">{clip("MK", a)}</div>'
    f'<div class="ur" style="top:1240px;font-size:104px;{at(19.9,"pop")}">تو <b>بکے گا کیسے؟</b></div>'))
# 10 end card + dose cards
a, b = S[9]
dose = [("1f410.png", "GOAT", "بکرا", "10–12 ML", "APPROX 40 KG"), ("1f402.png", "CALF", "بچھڑا", "35–40 ML", "APPROX 350–400 KG"),
        ("1f404.png", "MILKING COW / BUFFALO", "دودھ والی گائے بھینس", "60–70 ML", "APPROX 600 KG")]
x.append(sc(9, top +
    f'<img class="btl" src="file://{bottle}" style="left:50%;top:230px;height:620px;margin-left:-173px;{at(a,"bag",.4)}">'
    f'<div class="ur" style="top:860px;font-size:84px;{at(a+.05,"pop")}"><b>ہیپٹا سیف،</b> وزن بڑھانے کا ساتھی!</div>'
    f'<div style="position:absolute;top:1030px;left:50px;right:50px;display:flex;gap:14px">'
    + "".join(f'<div class="dose" style="{at(a + .3 + i * .15, "pop")}"><img src="file://{E(c)}"><small>{wt}<br>LIVE WEIGHT</small><b>{ml}</b><span>{u}</span></div>' for i, (c, e, u, ml, wt) in enumerate(dose)) +
    '</div>'))

html = f'<div id="v"><div class="sheen"></div>{"".join(x)}</div>'
W.mkdir(parents=True, exist_ok=True)
job = W / "anim-job.json"
job.write_text(json.dumps({"width": 1080, "height": 1920, "css": css, "fonts": fonts, "states": [{"file": "", "html": html}]}))
if "--html-only" in sys.argv:
    sys.exit(0)
subprocess.run(["rm", "-rf", str(W / "frames")])
subprocess.run(["node", str(R / "tools/posts/anim_frames.js"), str(job), str(W / "frames"), "30", str(DUR), sys.argv[1] if len(sys.argv) > 1 else "2"], check=True)
print("frames ok")
