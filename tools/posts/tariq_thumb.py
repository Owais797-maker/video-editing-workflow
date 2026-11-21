#!/usr/bin/env python3
"""Customer-feedback thumbnail (9:16, 4K) in the locked product-post look: Tariq Shirazi sahab + Hepta Sef + Gripe Water."""
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
d=R/"Video Edits/Export/tariq-thumbnail"; w=d/"work"; w.mkdir(parents=True,exist_ok=True)
def up(src,name,k):
    im=Image.open(R/src).convert("RGBA"); im=im.resize((im.width*k,im.height*k),Image.LANCZOS).filter(ImageFilter.UnsharpMask(2,50,2)); p=w/name; im.save(p); return p
hs=up("Video Edits/Raw/three-products/hepta-sef-cutout.png","hs.png",3)
gw=up("Video Edits/Raw/bacha-hairan/gripe-water-mockup-cutout.png","gw.png",3)
tq=up("Video Edits/Raw/tariq-feedback/tariq-crop-cutout.png","tq.png",2)
RED="#D9232E"; INK="#1B1B1F"; P="#6B2C91"; B="#1F56C9"
css=f"""
*{{margin:0;padding:0;box-sizing:border-box}}
#p{{position:absolute;inset:0;overflow:hidden;font-family:Poppins;color:{INK};background:radial-gradient(ellipse 80% 45% at 50% 62%,#FFFFFF 0%,#F2F2F4 50%,#DFE0E5 100%)}}
.sheen{{position:absolute;inset:0;background:linear-gradient(115deg,transparent 42%,rgba(255,255,255,.55) 50%,transparent 58%)}}
.glow{{position:absolute;left:50%;top:1060px;width:1100px;height:900px;transform:translate(-50%,-50%);border-radius:50%;
 background:radial-gradient(circle,rgba(217,35,46,.16) 0%,rgba(217,35,46,.06) 40%,transparent 66%)}}
.cs{{position:absolute;top:236px;left:50%;transform:translateX(-50%);display:flex;white-space:nowrap;border-radius:60px;overflow:hidden;box-shadow:0 12px 26px rgba(217,35,46,.25)}}
.cs b{{background:linear-gradient(135deg,#F03A43,{RED});color:#fff;font:800 24px Poppins;letter-spacing:5px;padding:13px 26px 11px 30px;display:flex;align-items:center;gap:12px}}
.cs b:before{{content:"";width:14px;height:14px;border-radius:50%;background:#fff;box-shadow:0 0 0 5px rgba(255,255,255,.3)}}
.cs span{{background:#fff;color:{RED};font:42px/1 Noori;padding:8px 28px 12px 24px;direction:rtl}}
.l1{{position:absolute;top:318px;left:0;right:0;text-align:center;direction:rtl;font:64px/1.55 Noori;color:#2a2a2e}}
.l1 span{{font-family:Aslam;color:{INK};font-size:1.15em}}
.hero{{position:absolute;top:420px;left:0;right:0;text-align:center;direction:rtl;font:128px/1.3 Aslam;white-space:nowrap;
 background:linear-gradient(180deg,#F03A43,{RED} 55%,#B5161F);-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 16px 20px rgba(217,35,46,.25))}}
.en{{position:absolute;top:640px;left:0;right:0;text-align:center;font:900 54px/1 Montserrat;letter-spacing:-.5px;white-space:nowrap}}
.en i{{font-style:normal;color:{P}}} .en u{{text-decoration:none;color:{B}}} .en em{{font-style:normal;color:#9a9aa0;margin:0 14px}}
.tq{{position:absolute;left:50%;top:720px;width:900px;transform:translateX(-50%);-webkit-mask-image:linear-gradient(to top,transparent 0%,#000 18%),linear-gradient(to right,transparent 0%,#000 12%,#000 88%,transparent 100%);-webkit-mask-composite:source-in;
 filter:drop-shadow(0 24px 30px rgba(0,0,0,.25))}}
.disc{{position:absolute;width:300px;height:56px;border-radius:50%;background:radial-gradient(ellipse at 50% 35%,#fff,#E6E6EA 60%,#CFCFD6);box-shadow:0 20px 30px rgba(0,0,0,.18)}}
.btl{{position:absolute;filter:drop-shadow(0 22px 24px rgba(0,0,0,.3))}}
.nm{{position:absolute;top:1360px;left:50%;transform:translateX(-50%);white-space:nowrap;background:#fff;border-radius:60px;padding:14px 40px 12px;
 box-shadow:0 20px 40px rgba(0,0,0,.18);text-align:center;border:3px solid {RED}}}
.nm b{{display:block;font:800 40px Poppins;letter-spacing:-.3px}}
.nm small{{display:block;font:600 17px Poppins;letter-spacing:5px;color:{RED};margin-top:-2px}}
.ft{{position:absolute;top:1520px;left:0;right:0;text-align:center;direction:rtl;font:46px/1.6 Noori;color:#3a3d40}}
.ft span{{font-family:Aslam;color:{RED};font-size:1.1em}}
"""
html=f"""<div id="p"><div class="sheen"></div><div class="glow"></div>
<div class="cs"><b>COMING SOON</b><span>جلد ویڈیو آ رہی ہے</span></div>
<div class="l1"><span>طارق شیرازی</span> صاحب کا</div>
<div class="hero">زبردست فیڈ بیک!</div>
<div class="en"><i>HEPTA SEF</i><em>+</em><u>GRIPE WATER</u></div>
<img class="tq" src="file://{tq}">
<div class="disc" style="left:20px;top:1320px"></div><img class="btl" src="file://{hs}" style="left:52px;top:960px;height:400px">
<div class="disc" style="right:20px;top:1320px"></div><img class="btl" src="file://{gw}" style="right:56px;top:960px;height:400px">
<div class="nm"><b>Tariq Shirazi Sahab</b><small>REAL CUSTOMER · REAL FEEDBACK</small></div>
<div class="ft">پوری ویڈیو دیکھیں، <span>کسٹمر</span> کی اپنی زبانی</div>
</div>"""
out=d/"tariq-thumbnail.png"; job=d/"job.json"
job.write_text(json.dumps({"width":1080,"height":1920,"scale":2,"css":css,"fonts":fonts,"states":[{"file":str(out),"html":html}]}))
subprocess.run(["node",str(R/"tools/htmlcaps/render.js"),str(job)],check=True,capture_output=True)
job.unlink(); (d/"page.html").unlink(missing_ok=True)
im=Image.open(out).convert("RGB"); im.save(d/"tariq-thumbnail.jpg",quality=95); out.unlink(); print(d/"tariq-thumbnail.jpg")
