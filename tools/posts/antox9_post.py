#!/usr/bin/env python3
"""Antox 9 (Stavbio, Russia) 9:16 info post: strains -> diseases, dosage. Locked white series look."""
import json,subprocess
from pathlib import Path
from PIL import Image, ImageFilter
R=Path(__file__).resolve().parents[2]
F=lambda g: str(next(R.joinpath('fonts').rglob(g)))
fonts=[{"family":"Noori","path":F("JameelNooriNastaleeq-400.ttf"),"weight":400,"style":"normal"},
 {"family":"Aslam","path":F("Aslam-400.ttf"),"weight":400,"style":"normal"},
 {"family":"Montserrat","path":F("Montserrat-900.ttf"),"weight":900,"style":"normal"},
 {"family":"Montserrat","path":F("Montserrat-500.ttf"),"weight":500,"style":"normal"},
 {"family":"Poppins","path":F("Poppins-600.ttf"),"weight":600,"style":"normal"},
 {"family":"Poppins","path":F("Poppins-700.ttf"),"weight":700,"style":"normal"},
 {"family":"Poppins","path":F("Poppins-800.ttf"),"weight":800,"style":"normal"}]
d=R/"Video Edits/Export/antox9-post"; w=d/"work"; w.mkdir(parents=True,exist_ok=True)
from PIL import ImageEnhance
im=Image.open(R/"Video Edits/Raw/antox9/box-crop-cutout.png").convert("RGBA")
a=im.split()[3]; rgb=im.convert("RGB")
rgb=ImageEnhance.Brightness(rgb).enhance(1.22); rgb=ImageEnhance.Contrast(rgb).enhance(1.08); rgb=ImageEnhance.Color(rgb).enhance(1.12)
import numpy as np
x=np.array(rgb).astype(float); x[...,2]=np.clip(x[...,2]*1.04,0,255); x[...,0]=np.clip(x[...,0]*0.98,0,255)
rgb=Image.fromarray(x.astype("uint8")).filter(ImageFilter.UnsharpMask(2,60,2)); rgb.putalpha(a); im=rgb
box=w/"box.png"; im.save(box)
B="#1E3A8C"; B2="#2F55C2"; BD="#122563"; RED="#D9232E"; INK="#1B1B1F"
rows=[("Cl. perfringens A","گیس گینگرین / آنتوں کی سوزش"),
      ("Cl. perfringens C (B)","خونی دست / انٹیروٹاکسیمیا"),
      ("Cl. perfringens D","انٹیروٹاکسیمیا (اچانک موت)"),
      ("Cl. novyi A","گیس گینگرین / سوجن"),
      ("Cl. novyi B","بلیک ڈیزیز (جگر)"),
      ("Cl. tetani","تشنج (ٹیٹنس)"),
      ("Cl. sordellii","سوجن / آنتوں کا انفیکشن"),
      ("Cl. septicum","مہلک سوجن <bdi style=\"font:600 17px Poppins;color:#8a8a90\">(Malignant Oedema)</bdi>"),
      ("Cl. chauvoei","لنگڑا بخار <bdi style=\"font:600 17px Poppins;color:#8a8a90\">(Black Quarter)</bdi>")]
css=f"""*{{margin:0;padding:0;box-sizing:border-box}}
#p{{position:absolute;inset:0;overflow:hidden;font-family:Poppins;color:{INK};background:radial-gradient(ellipse 80% 50% at 50% 45%,#FFFFFF 0%,#F2F4F8 55%,#E1E5EE 100%)}}
.sheen{{position:absolute;inset:0;background:linear-gradient(115deg,transparent 42%,rgba(255,255,255,.55) 50%,transparent 58%)}}
.top{{position:absolute;top:104px;left:0;right:0;text-align:center;font:500 21px Montserrat;letter-spacing:8px;color:#77777d}} .top b{{font-weight:900;color:{INK};letter-spacing:6px}} .top i{{font-style:normal;color:{RED}}}
.l1{{position:absolute;top:158px;left:0;right:0;text-align:center;direction:rtl;font:54px/1.6 Noori;color:#2a2a2e}} .l1 span{{font-family:Aslam;color:{RED};font-size:1.12em}}
.hero{{position:absolute;top:250px;left:0;right:0;text-align:center;font:900 132px/1 Montserrat;letter-spacing:-3px;background:linear-gradient(180deg,{B2},{B} 60%,{BD});-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 12px 16px rgba(30,58,140,.22))}}
.sub{{position:absolute;top:392px;left:0;right:0;text-align:center;direction:rtl;font:60px/1.4 Aslam;color:{RED}}}
.sub b{{font:800 30px Poppins;color:#fff;background:{B};border-radius:40px;padding:8px 22px 6px;margin-right:16px;vertical-align:10px;direction:ltr;display:inline-block;letter-spacing:2px}}
.box{{position:absolute;left:34px;top:560px;height:650px;filter:drop-shadow(0 24px 26px rgba(0,0,0,.25))}}
.disc{{position:absolute;left:20px;top:1180px;width:420px;height:60px;border-radius:50%;background:radial-gradient(ellipse at 50% 35%,#fff,#E6E8EE 60%,#CFD3DC);box-shadow:0 18px 28px rgba(0,0,0,.15)}}
.list{{position:absolute;left:450px;right:40px;top:548px;background:#fff;border-radius:28px;padding:18px 22px 12px;box-shadow:0 12px 30px rgba(0,0,0,.08)}}
.lh{{display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px solid {B};padding-bottom:8px;margin-bottom:4px}}
.lh b{{font:900 20px Montserrat;letter-spacing:2px;color:{B}}} .lh span{{direction:rtl;font:32px/1.3 Aslam;color:{RED}}}
.r{{display:flex;align-items:center;gap:10px;border-bottom:1px dashed #DADDE5;padding:5px 0 3px}} .r:last-child{{border-bottom:none}}
.n{{flex:none;width:30px;height:30px;border-radius:50%;background:{B};color:#fff;font:800 15px Poppins;display:flex;align-items:center;justify-content:center}}
.r .t{{flex:1;min-width:0}} .r .e{{font:700 17px/1.2 Poppins;color:{INK};white-space:nowrap}} .r .u{{direction:rtl;text-align:right;font:25px/1.35 Noori;color:#3a3a3e;white-space:nowrap}}
.note{{position:absolute;left:44px;right:44px;top:1290px;text-align:center;direction:rtl;font:44px/1.6 Noori;color:#2a2a2e}} .note span{{font-family:Aslam;color:{RED};font-size:1.08em}}
.chips{{position:absolute;left:44px;right:44px;top:1400px;display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.chips div{{background:#fff;border-radius:22px;padding:14px 18px 12px;text-align:center;box-shadow:0 10px 24px rgba(0,0,0,.07);border:2px solid #E3E7F0}}
.chips div.k{{background:{B};border-color:{B};color:#fff}}
.chips small{{display:block;font:600 15px Poppins;letter-spacing:3px;opacity:.7}} .chips b{{display:block;font:800 30px Poppins;margin-top:2px}} .chips i{{display:block;font-style:normal;font:600 17px Poppins;opacity:.75}}
.ft{{position:absolute;bottom:44px;left:0;right:0;text-align:center;font:500 17px Montserrat;letter-spacing:6px;color:#8a8a90}}"""
lst="".join(f'<div class="r"><div class="n">{i+1}</div><div class="t"><div class="e">{e}</div><div class="u">{u}</div></div></div>' for i,(e,u) in enumerate(rows))
html=f"""<div id="p"><div class="sheen"></div>
<div class="top"><b>STAVBIO</b> &nbsp;·&nbsp; MADE IN <i>RUSSIA</i></div>
<div class="l1"><span>رشیا</span> کی زبردست ویکسین</div>
<div class="hero">ANTOX 9</div>
<div class="sub"><b>9 IN 1</b>کلوسٹریڈیل بیماریوں سے بچاؤ</div>
<div class="disc"></div><img class="box" src="file://{box}">
<div class="list"><div class="lh"><b>COVERS 9 STRAINS</b><span>کن بیماریوں سے؟</span></div>{lst}</div>
<div class="note"><span>گائے</span>، بھینس، بھیڑ اور بکریوں کے لیے آزمودہ ویکسین</div>
<div class="chips">
 <div class="k"><small>CATTLE · گائے بھینس</small><b>4 ML</b><i>25 doses / 100 ml</i></div>
 <div class="k"><small>SHEEP &amp; GOAT</small><b>2 ML</b><i>50 doses / 100 ml</i></div>
 <div><small>WITHDRAWAL</small><b>ZERO DAYS</b><i>Subcutaneous · under the skin</i></div>
 <div><small>STORAGE</small><b>2–8 °C</b><i>Fridge, dark place</i></div></div>
<div class="ft">FOR VETERINARY USE ONLY · STAVROPOL BIOFACTORY · RUSSIA</div></div>"""
out=d/"antox9-post.png"; job=d/"job.json"
job.write_text(json.dumps({"width":1080,"height":1920,"scale":2,"css":css,"fonts":fonts,"states":[{"file":str(out),"html":html}]}))
subprocess.run(["node",str(R/"tools/htmlcaps/render.js"),str(job)],check=True,capture_output=True)
job.unlink(); (d/"page.html").unlink(missing_ok=True)
Image.open(out).convert("RGB").save(d/"antox9-post.jpg",quality=95); out.unlink(); print(d/"antox9-post.jpg")
