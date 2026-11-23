#!/usr/bin/env python3
"""Facebook cover (1640x624 @2x) for "Khyber Wala Owais" in the red/white series, products on a disc."""
import json,subprocess
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[2]
F=lambda g: str(next(R.joinpath('fonts').rglob(g)))
fonts=[{"family":"Montserrat","path":F("Montserrat-900.ttf"),"weight":900,"style":"normal"},{"family":"Montserrat","path":F("Montserrat-500.ttf"),"weight":500,"style":"normal"},
 {"family":"Poppins","path":F("Poppins-700.ttf"),"weight":700,"style":"normal"},{"family":"Poppins","path":F("Poppins-800.ttf"),"weight":800,"style":"normal"},
 {"family":"Noori","path":F("JameelNooriNastaleeq-400.ttf"),"weight":400,"style":"normal"},{"family":"Aslam","path":F("Aslam-400.ttf"),"weight":400,"style":"normal"}]
RED="#D9232E"; INK="#1B1B1F"; RV=R/"Video Edits/Raw"
prods=[RV/"heavy-gold/heavy-gold-bag-cutout.png",RV/"butter-milk/butter-milk-bag-cutout.png",RV/"three-products/hepta-sef-cutout.png",RV/"mega-vmix/mega-vmix-bag-cutout.png"]
css=f"""*{{margin:0;padding:0;box-sizing:border-box}}
#p{{position:absolute;inset:0;overflow:hidden;font-family:Poppins;color:{INK};background:radial-gradient(ellipse 70% 90% at 30% 50%,#FFFFFF 0%,#F4F4F5 55%,#E4E4E7 100%)}}
.sheen{{position:absolute;inset:0;background:linear-gradient(110deg,transparent 40%,rgba(255,255,255,.6) 50%,transparent 60%)}}
.bar{{position:absolute;left:0;top:0;bottom:0;width:12px;background:{RED}}}
.txt{{position:absolute;left:230px;top:112px}}
.kw{{font:900 38px Montserrat;letter-spacing:4px}} .kw i{{font-style:normal;color:{RED}}}
.nm{{font:800 118px/1.05 Poppins;letter-spacing:-4px;margin-left:-8px;background:linear-gradient(180deg,#F03A43,{RED} 55%,#B5161F);-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 12px 16px rgba(217,35,46,.22))}}
.pill{{display:inline-block;margin-top:14px;background:{RED};color:#fff;font:700 24px Poppins;letter-spacing:3px;padding:10px 28px;border-radius:50px;box-shadow:0 12px 24px rgba(217,35,46,.3)}}
.u{{margin-top:16px;direction:rtl;text-align:left;font:34px/1.5 Noori;color:#3a3a3e}} .u span{{font-family:Aslam;color:{RED};font-size:1.1em}}
.ph{{margin-top:6px;font:600 17px Montserrat;letter-spacing:5px;color:#6b6b72}}
.prods{{position:absolute;right:80px;bottom:70px;display:flex;align-items:flex-end;gap:4px}}
.prods img{{filter:drop-shadow(0 16px 16px rgba(0,0,0,.28))}}
.disc{{position:absolute;right:50px;bottom:42px;width:640px;height:60px;border-radius:50%;background:radial-gradient(ellipse at 50% 35%,#fff,#E6E6EA 60%,#CFCFD6);box-shadow:0 18px 28px rgba(0,0,0,.15)}}"""
ims="".join(f'<img src="file://{p}" style="height:{h}px">' for p,h in zip(prods,[250,262,200,250]))
html=f"""<div id="p"><div class="sheen"></div><div class="bar"></div>
<div class="txt"><div class="kw">KHYBER <i>WALA</i></div><div class="nm">“Owais”</div>
<div class="pill">WHOLESALE VET STORE</div><div class="u">جانوروں کی <span>صحت</span>، ہماری ذمہ داری</div>
<div class="ph">DENSO HALL · KARACHI</div></div>
<div class="disc"></div><div class="prods">{ims}</div></div>"""
d=R/"Video Edits/Export/social-setup"; d.mkdir(parents=True,exist_ok=True); out=d/"fb-cover.png"; job=d/"job.json"
job.write_text(json.dumps({"width":1640,"height":624,"scale":2,"css":css,"fonts":fonts,"states":[{"file":str(out),"html":html}]}))
subprocess.run(["node",str(R/"tools/htmlcaps/render.js"),str(job)],check=True,capture_output=True)
job.unlink(); (d/"page.html").unlink(missing_ok=True)
Image.open(out).convert("RGB").save(d/"fb-cover.jpg",quality=95); out.unlink(); print(d/"fb-cover.jpg")
