#!/usr/bin/env python3
"""Tolomec Plus (Fatro, Italy) 9:16 info post: ivermectin + clorsulon, what it covers, label facts. Locked white series."""
import json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
R=Path(__file__).resolve().parents[2]
F=lambda g: str(next(R.joinpath('fonts').rglob(g)))
fonts=[{"family":"Noori","path":F("JameelNooriNastaleeq-400.ttf"),"weight":400,"style":"normal"},
 {"family":"Aslam","path":F("Aslam-400.ttf"),"weight":400,"style":"normal"},
 {"family":"Montserrat","path":F("Montserrat-900.ttf"),"weight":900,"style":"normal"},
 {"family":"Montserrat","path":F("Montserrat-500.ttf"),"weight":500,"style":"normal"},
 {"family":"Poppins","path":F("Poppins-600.ttf"),"weight":600,"style":"normal"},
 {"family":"Poppins","path":F("Poppins-700.ttf"),"weight":700,"style":"normal"},
 {"family":"Poppins","path":F("Poppins-800.ttf"),"weight":800,"style":"normal"}]
d=R/"Video Edits/Export/tolomec-post"; w=d/"work"; w.mkdir(parents=True,exist_ok=True)
hero=R/"Video Edits/Raw/tolomec/box-hero.png"
im=Image.open(R/"Video Edits/Raw/tolomec/box-grounded.png").convert("RGBA"); a=im.split()[3]
x=np.asarray(im.convert("RGB")).astype(np.float32)/255
lo=np.percentile(x[np.asarray(a)>128],1.5,axis=0); hi=np.percentile(x[np.asarray(a)>128],98.5,axis=0)
x=np.clip((x-lo)/(hi-lo),0,1)                       # auto levels per channel (removes the grey/yellow cast)
x=np.clip(x**0.95,0,1)                              # lift mid-tones
x=0.5+(x-0.5)*1.04                                  # contrast
rgb=Image.fromarray((np.clip(x,0,1)*255).astype("uint8"))
rgb=ImageEnhance.Color(rgb).enhance(1.15).filter(ImageFilter.UnsharpMask(2,70,2))
rgb.putalpha(a); box=w/"box.png"; rgb.save(box)
T="#1C8C8C"; T2="#2BB3B0"; TD="#12605F"; RED="#C8202B"; INK="#1B1B1F"
chk='<svg width="22" height="22" viewBox="0 0 24 24"><path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
cards=[("IVERMECTIN 10 MG/ML","اسکن انجیکشن","Skin parasites · ticks, lice & mange"),
       ("CLORSULON 100 MG/ML","جگر کے کیڑوں کے لیے","Liver fluke · Fasciola")]
css=f"""*{{margin:0;padding:0;box-sizing:border-box}}
#p{{position:absolute;inset:0;overflow:hidden;font-family:Poppins;color:{INK};background:radial-gradient(ellipse 80% 50% at 50% 45%,#FFFFFF 0%,#F1F6F6 55%,#DDE7E7 100%)}}
.sheen{{position:absolute;inset:0;background:linear-gradient(115deg,transparent 42%,rgba(255,255,255,.55) 50%,transparent 58%)}}
.top{{position:absolute;top:104px;left:0;right:0;text-align:center;font:500 21px Montserrat;letter-spacing:8px;color:#77777d}} .top b{{font-weight:900;color:{INK};letter-spacing:6px}} .top i{{font-style:normal;color:{RED}}}
.l1{{position:absolute;top:158px;left:30px;right:30px;text-align:center;direction:rtl;font:50px/1.6 Noori;white-space:nowrap;color:#2a2a2e}} .l1 span{{font-family:Aslam;color:{RED};font-size:1.12em}}
.hero{{position:absolute;top:252px;left:0;right:0;text-align:center;font:900 112px/1 Montserrat;letter-spacing:-3px;color:{RED};filter:drop-shadow(0 12px 16px rgba(200,32,43,.2))}}
.hero i{{font-style:normal;color:{T}}}
.sub{{position:absolute;top:382px;left:0;right:0;text-align:center;direction:rtl;font:62px/1.4 Aslam;color:{TD}}}
.sub b{{color:{RED};font-weight:400}}
.box{{position:absolute;left:50px;top:530px;height:862px;z-index:2;}}
.cs{{position:absolute;left:110px;top:1262px;width:420px;height:44px;border-radius:50%;background:radial-gradient(ellipse at 55% 50%,rgba(0,0,0,.7),rgba(0,0,0,.35) 45%,transparent 72%);filter:blur(4px);z-index:1}}
.disc{{position:absolute;left:40px;top:1238px;width:560px;height:100px;border-radius:50%;background:radial-gradient(ellipse at 50% 35%,#fff,#E3EBEB 60%,#C9D6D6);box-shadow:0 18px 28px rgba(0,0,0,.15)}}
.cards{{position:absolute;left:630px;right:40px;top:560px;display:flex;flex-direction:column;gap:18px}}
.c{{background:#fff;border-radius:26px;padding:18px 22px 16px;box-shadow:0 12px 28px rgba(0,0,0,.08);border-top:8px solid {T}}}
.c:nth-child(2){{border-top-color:{RED}}}
.c .e{{font:900 22px Montserrat;letter-spacing:1px;color:{INK}}}
.c .u{{direction:rtl;text-align:right;font:40px/1.5 Aslam;color:{T};margin-top:4px}} .c:nth-child(2) .u{{color:{RED}}}
.c .s{{font:600 18px Poppins;color:#7a7a80;margin-top:2px}}
.two{{background:{INK};color:#fff;border-radius:26px;padding:18px 22px;text-align:center}}
.two .u{{direction:rtl;font:32px/1.5 Noori;white-space:nowrap}} .two b{{font-family:Aslam;font-weight:400;color:#FFD400}}
.note{{position:absolute;left:44px;right:44px;top:1375px;text-align:center;direction:rtl;font:46px/1.6 Noori;color:#2a2a2e}} .note span{{font-family:Aslam;color:{RED};font-size:1.08em}}
.chips{{position:absolute;left:44px;right:44px;top:1480px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}}
.chips div{{background:#fff;border-radius:22px;padding:14px 10px 12px;text-align:center;box-shadow:0 10px 24px rgba(0,0,0,.07);border:2px solid #DDE7E7}}
.chips div.k{{background:{T};border-color:{T};color:#fff}} .chips div.w{{background:#FFF3F3;border-color:#F3C9CC}}
.chips small{{display:block;font:600 14px Poppins;letter-spacing:2.5px;opacity:.75}} .chips b{{display:block;font:800 26px/1.2 Poppins;margin-top:4px}} .chips i{{display:block;font-style:normal;font:600 15px Poppins;opacity:.75}}
.warn{{position:absolute;left:44px;right:44px;top:1650px;display:flex;align-items:center;gap:14px;justify-content:center;direction:rtl;font:38px/1.5 Noori;color:{RED}}}
.warn em{{font-style:normal;font:800 26px Poppins;background:{RED};color:#fff;border-radius:50%;width:44px;height:44px;display:flex;align-items:center;justify-content:center}}
.ft{{position:absolute;bottom:44px;left:0;right:0;text-align:center;font:500 17px Montserrat;letter-spacing:6px;color:#8a8a90}}"""
cs="".join(f'<div class="c"><div class="e">{e}</div><div class="u">{u}</div><div class="s">{s}</div></div>' for e,u,s in cards)
html=f"""<div id="p"><div class="sheen"></div>
<div class="top"><b>FATRO</b> &nbsp;·&nbsp; MADE IN <i>ITALY</i></div>
<div class="l1"><span>اٹلی</span> والا <span>جگر</span> اور <span>چمڑے</span> کا زبردست انجیکشن</div>
<div class="hero">TOLOMEC <i>PLUS</i></div>
<div class="sub"><b>جگر کے کیڑے</b> + اسکن، ایک ساتھ</div>
<img class="box" src="file://{box}">
<div class="cards">{cs}<div class="two"><div class="u"><bdi style="font:900 34px Montserrat;color:#FFD400;letter-spacing:1px">2 IN 1</bdi> &nbsp;ایک ہی انجیکشن میں دونوں کام</div></div></div>
<div class="note"><span>گائے</span> اور بھینس کے لیے</div>
<div class="chips">
 <div class="k"><small>PACK</small><b>500 ML</b><i>Injectable</i></div>
 <div><small>ROUTE</small><b>UNDER SKIN</b><i>Subcutaneous</i></div>
 <div class="w"><small>MEAT WITHDRAWAL</small><b>66 DAYS</b><i>before slaughter</i></div></div>
<div class="warn"><em>!</em>دودھ دینے والے جانوروں میں استعمال نہ کریں</div>
<div class="ft">FOR VETERINARY USE ONLY · FATRO S.p.A. · ITALY</div></div>"""
out=d/"tolomec-post.png"; job=d/"job.json"
job.write_text(json.dumps({"width":1080,"height":1920,"scale":2,"css":css,"fonts":fonts,"states":[{"file":str(out),"html":html}]}))
subprocess.run(["node",str(R/"tools/htmlcaps/render.js"),str(job)],check=True,capture_output=True)
job.unlink(); (d/"page.html").unlink(missing_ok=True)
Image.open(out).convert("RGB").save(d/"tolomec-post.jpg",quality=95); out.unlink(); print(d/"tolomec-post.jpg")
