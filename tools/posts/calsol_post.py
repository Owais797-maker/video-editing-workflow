#!/usr/bin/env python3
"""Calsol-D (Vetsol) calcium + vitamins liquid, 9:16 info post for milking / female animals, label facts only. Urdu in Noori + Mehr (owner: less Aslam). Locked white series."""
import json,os,re,subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
R=Path(__file__).resolve().parents[2]
F=lambda g: str(next(R.joinpath('fonts').rglob(g)))
fonts=[{"family":"Noori","path":F("JameelNooriNastaleeq-400.ttf"),"weight":400,"style":"normal"},
 {"family":"Aslam","path":F("Aslam-400.ttf"),"weight":400,"style":"normal"},
 {"family":"Mehr","path":F("MehrNastaliq-400.ttf"),"weight":400,"style":"normal"},
 {"family":"Montserrat","path":F("Montserrat-900.ttf"),"weight":900,"style":"normal"},
 {"family":"Montserrat","path":F("Montserrat-500.ttf"),"weight":500,"style":"normal"},
 {"family":"Poppins","path":F("Poppins-600.ttf"),"weight":600,"style":"normal"},
 {"family":"Poppins","path":F("Poppins-700.ttf"),"weight":700,"style":"normal"},
 {"family":"Poppins","path":F("Poppins-800.ttf"),"weight":800,"style":"normal"}]
d=R/"Video Edits/Export/calsol-post"; w=d/"work"; w.mkdir(parents=True,exist_ok=True)
im=Image.open(R/"Video Edits/Raw/calsol-d/bottle-grounded.png").convert("RGBA"); a=im.split()[3]
x=np.asarray(im.convert("RGB")).astype(np.float32)/255
lo=np.percentile(x[np.asarray(a)>128],1.5,axis=0); hi=np.percentile(x[np.asarray(a)>128],98.5,axis=0)
x=np.clip((x-lo)/(hi-lo),0,1)                       # auto levels per channel (removes the grey/yellow cast)
x=np.clip(x**0.95,0,1)                              # lift mid-tones
x=0.5+(x-0.5)*1.04                                  # contrast
rgb=Image.fromarray((np.clip(x,0,1)*255).astype("uint8"))
rgb=ImageEnhance.Color(rgb).enhance(1.15).filter(ImageFilter.UnsharpMask(2,70,2))
rgb.putalpha(a); box=w/"box.png"; rgb.save(box)
T="#8E1F6E"; T2="#B23A8E"; TD="#4A1240"; RED="#D4203A"; INK="#1B1B1F"
chk='<svg width="22" height="22" viewBox="0 0 24 24"><path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
cards=[("TRICALCIUM 9000 MG","ملک فیور سے بچاؤ میں مددگار","Rapid calcium &amp; energy · per 100 ml"),
       ("VITAMIN A · D3 · E · B1 · B3","دودھ اور گابھن ہونے میں مددگار","Milk yield · conception ratio")]
css=f"""*{{margin:0;padding:0;box-sizing:border-box}}
#p{{position:absolute;inset:0;overflow:hidden;font-family:Poppins;color:{INK};background:radial-gradient(ellipse 80% 50% at 50% 45%,#FFFFFF 0%,#F7F3F6 55%,#EBE1E8 100%)}}
.sheen{{position:absolute;inset:0;background:linear-gradient(115deg,transparent 42%,rgba(255,255,255,.55) 50%,transparent 58%)}}
.top{{position:absolute;top:104px;left:0;right:0;text-align:center;font:500 21px Montserrat;letter-spacing:8px;color:#77777d}} .top b{{font-weight:900;color:{INK};letter-spacing:6px}} .top i{{font-style:normal;color:{RED}}}
.l1{{position:absolute;top:158px;left:30px;right:30px;text-align:center;direction:rtl;font:50px/1.6 Noori;white-space:nowrap;color:#2a2a2e}} .l1 span{{color:{T};font-size:1.12em;text-shadow:0 0 .5px {T}}}
.hero{{position:absolute;top:252px;left:0;right:0;text-align:center;font:900 112px/1 Montserrat;letter-spacing:-3px;color:{RED};filter:drop-shadow(0 12px 16px rgba(200,32,43,.2))}}
.hero i{{font-style:normal;color:{T}}}
.sub{{position:absolute;top:372px;left:0;right:0;text-align:center;direction:rtl;font:74px/1.6 Mehr;color:{TD}}}
.sub b{{color:{RED};font-weight:400}}
.box{{position:absolute;left:135px;top:500px;height:920px;z-index:2;}}
.cs{{position:absolute;left:110px;top:1262px;width:420px;height:44px;border-radius:50%;background:radial-gradient(ellipse at 55% 50%,rgba(0,0,0,.7),rgba(0,0,0,.35) 45%,transparent 72%);filter:blur(4px);z-index:1}}
.disc{{position:absolute;left:40px;top:1238px;width:560px;height:100px;border-radius:50%;background:radial-gradient(ellipse at 50% 35%,#fff,#EFE6EC 60%,#DCCAD6);box-shadow:0 18px 28px rgba(0,0,0,.15)}}
.cards{{position:absolute;left:630px;right:40px;top:560px;display:flex;flex-direction:column;gap:18px}}
.c{{background:#fff;border-radius:26px;padding:18px 22px 16px;box-shadow:0 12px 28px rgba(0,0,0,.08);border-top:8px solid {T}}}
.c:nth-child(2){{border-top-color:{RED}}}
.c .e{{font:900 22px Montserrat;letter-spacing:1px;color:{INK}}}
.c .u{{direction:rtl;text-align:right;font:38px/1.6 Noori;color:{T};margin-top:4px}} .c:nth-child(2) .u{{color:{RED}}}
.c .s{{font:600 18px Poppins;color:#7a7a80;margin-top:2px}}
.two{{background:{INK};color:#fff;border-radius:26px;padding:18px 22px;text-align:center}}
.two .u{{direction:rtl;font:32px/1.5 Noori;white-space:nowrap}} .two b{{font-weight:400;color:#FFD400}}
.note{{position:absolute;left:44px;right:44px;top:1400px;text-align:center;direction:rtl;font:46px/1.6 Noori;color:#2a2a2e}} .note span{{color:{T};font-size:1.1em}}
.chips{{position:absolute;left:44px;right:44px;top:1500px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}}
.chips div{{background:#fff;border-radius:22px;padding:14px 10px 12px;text-align:center;box-shadow:0 10px 24px rgba(0,0,0,.07);border:2px solid #EBE1E8}}
.chips div.k{{background:{T};border-color:{T};color:#fff}} .chips div.w{{background:{TD};border-color:{TD};color:#fff}}
.chips small{{display:block;font:600 14px Poppins;letter-spacing:2.5px;opacity:.75}} .chips b{{display:block;font:800 26px/1.2 Poppins;margin-top:4px}} .chips i{{display:block;font-style:normal;font:600 15px Poppins;opacity:.75}}
.warn{{position:absolute;left:44px;right:44px;top:1640px;display:flex;align-items:center;gap:14px;justify-content:center;direction:rtl;font:38px/1.5 Noori;color:{RED}}}
.warn em{{font-style:normal;font:800 26px Poppins;background:{RED};color:#fff;border-radius:50%;width:44px;height:44px;display:flex;align-items:center;justify-content:center}}
.trust{{position:absolute;left:630px;right:40px;top:1030px;display:flex;flex-direction:column;gap:14px}}
.t{{display:flex;align-items:center;gap:14px;background:#fff;border-radius:22px;padding:14px 16px;box-shadow:0 10px 24px rgba(0,0,0,.07);border:2px solid #EBE1E8}}
.t .ic{{flex:none;width:58px;height:58px;border-radius:50%;display:flex;align-items:center;justify-content:center;font:900 30px Montserrat;background:{T};color:#fff}}
.t.b .ic{{background:{RED};font-size:22px}}
.t .tx{{flex:1;text-align:right}} .t .tx b{{display:block;font:900 17px Montserrat;letter-spacing:1px;color:{INK}}}
.t .tx span{{display:block;direction:rtl;font:30px/1.55 Noori;color:#2a2a2e}} .t .tx span em{{font-style:normal;color:{T}}} .t.b .tx span em{{color:{RED}}}
.kt{{position:absolute;left:44px;right:44px;top:1742px;height:118px;border-radius:60px;background:#1B1B1F;display:flex;align-items:center;padding:0 26px 0 22px;gap:20px;box-shadow:0 14px 30px rgba(0,0,0,.18)}}
.kt img{{height:74px;margin-left:20px}} .kt .ph{{margin-left:auto}}
.kt .nm{{flex:1;color:#fff}} .kt .nm b{{display:block;font:900 30px Montserrat;letter-spacing:1px}} .kt .nm i{{display:block;font-style:normal;font:600 15px Montserrat;letter-spacing:4px;color:#FFD400}}
.kt .ph{{display:flex;align-items:center;gap:10px;background:#FFD400;color:#1B1B1F;border-radius:40px;padding:14px 24px;font:900 32px Montserrat;letter-spacing:.5px}}
.ft{{position:absolute;bottom:22px;left:0;right:0;text-align:center;font:500 14px Montserrat;letter-spacing:5px;color:#8a8a90}}"""
cs="".join(f'<div class="c"><div class="e">{e}</div><div class="u">{u}</div><div class="s">{s}</div></div>' for e,u,s in cards)
html=f"""<div id="p"><div class="sheen"></div>
<div class="top"><b>VETSOL</b> &nbsp;·&nbsp; CALCIUM + <i>VITAMINS</i></div>
<div class="l1">دودھ دینے والی <span>گائے، بھینس اور بکری</span> کے لیے</div>
<div class="hero">CALSOL<i>-D</i></div>
<div class="sub"><b>دودھ بھی</b>، طاقت بھی!</div>
<img class="box" src="file://{box}">
<div class="cards">{cs}<div class="two"><div class="u">بیانے کے بعد <b>جیر گرانے</b> میں مددگار</div></div></div>
<div class="trust">
 <div class="t"><div class="ic">✓</div><div class="tx"><b>COMMERCIAL STOCK</b><span><em>کمپنی</em> والا اصلی مال</span></div></div>
 <div class="t b"><div class="ic">D3</div><div class="tx"><b>TRANSITION PERIOD</b><span><em>بیانے سے پہلے</em> اور بعد</span></div></div></div>
<div class="note">روزانہ ایک بار، <span>منہ کے ذریعے</span> پلائیں</div>
<div class="chips">
 <div class="k"><small>COW · BUFFALO</small><b>60–100 ML</b><i>once a day</i></div>
 <div class="k"><small>SHEEP · GOAT</small><b>10–20 ML</b><i>once a day</i></div>
 <div class="w"><small>CALF · HEIFER</small><b>40–60 ML</b><i>once a day</i></div></div>
<div class="warn"><em>!</em>ٹھنڈی سوکھی جگہ، دھوپ سے بچا کر رکھیں</div>
<div class="kt"><img src="file://{R}/assets/logos/khyber-traders-wordmark-white-red.png"><div class="ph"><svg width="30" height="30" viewBox="0 0 24 24"><path fill="#1B1B1F" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .1-3.3-.8-2.8-1.1-4.5-4-4.7-4.2-.1-.2-1.1-1.5-1.1-2.9s.7-2 1-2.3c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.3 0 .5l-.4.5-.3.4c-.1.1-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.3 2.4 1.5.3.1.5.1.6-.1l.9-1c.2-.3.4-.2.6-.1l1.9.9c.3.1.5.2.5.3.1.2.1.7-.1 1.2z"/></svg>0310-2999262</div></div>
<div class="ft">1 LITRE · FOR VETERINARY USE ONLY · VETSOL PHARMACEUTICAL</div></div>"""
NOKT=bool(os.environ.get("NO_KT"))   # reseller version: no Khyber Traders bar
if NOKT:
    html=re.sub(r'<div class="kt">.*?</div></div>\n','',html,flags=re.S).replace('top:1640px','top:1700px')
    css=css.replace('top:1640px','top:1700px')
name="calsol-post-nokt" if NOKT else "calsol-post"
out=d/f"{name}.png"; job=d/"job.json"
job.write_text(json.dumps({"width":1080,"height":1920,"scale":2,"css":css,"fonts":fonts,"states":[{"file":str(out),"html":html}]}))
subprocess.run(["node",str(R/"tools/htmlcaps/render.js"),str(job)],check=True,capture_output=True)
job.unlink(); (d/"page.html").unlink(missing_ok=True)
Image.open(out).convert("RGB").save(d/f"{name}.jpg",quality=95); out.unlink(); print(d/f"{name}.jpg")
