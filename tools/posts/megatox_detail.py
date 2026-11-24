#!/usr/bin/env python3
"""Detailed 9:16 info post for Mega-Tox (clay): benefits + formulation table, locked white series look."""
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
d=R/"Video Edits/Export/mega-tox-detail"; w=d/"work"; w.mkdir(parents=True,exist_ok=True)
im=Image.open(R/"Video Edits/Raw/mega-tox-clay/bag-crop-cutout.png").convert("RGBA")
im=im.resize((im.width*3,im.height*3),Image.LANCZOS).filter(ImageFilter.UnsharpMask(2,50,2)); bag=w/"bag.png"; im.save(bag)
O="#D4561E"; O2="#EE7A36"; OD="#A63C0F"; G="#2E7D32"; INK="#1B1B1F"
ben=[("فیڈ کے زہر <bdi style=\"font:600 22px Poppins;color:#8a8a90\">(Mycotoxins)</bdi> کو جذب کر کے بے اثر کرے","Binds aflatoxin & mycotoxins"),
     ("ساڑھو <bdi style=\"font:600 22px Poppins;color:#8a8a90\">(Mastitis)</bdi> کا خطرہ کم کرنے میں مددگار","Supports udder health"),
     ("کُھر کے مسائل <bdi style=\"font:600 22px Poppins;color:#8a8a90\">(Laminitis)</bdi> کم کرنے میں مددگار","Hoof health support"),
     ("جگر کی صحت اور خوراک کا بہتر استعمال","Liver & feed efficiency"),
     ("دودھ اور پیداوار میں بہتری","Better productivity")]
form=[("Bentonite","400 g"),("Clinoptilolite (Zeolite)","300 g"),("Sepiolite","150 g"),("Montmorillonite","100 g"),("Yeast Cell Wall","25 g"),("Niacin (Vitamin B3)","0.5 g"),("Calcium Carbonate","q.s.")]
chk=f'<svg width="22" height="22" viewBox="0 0 24 24"><path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
css=f"""*{{margin:0;padding:0;box-sizing:border-box}}
#p{{position:absolute;inset:0;overflow:hidden;font-family:Poppins;color:{INK};background:radial-gradient(ellipse 80% 50% at 50% 45%,#FFFFFF 0%,#F3F3F5 55%,#E2E3E7 100%)}}
.sheen{{position:absolute;inset:0;background:linear-gradient(115deg,transparent 42%,rgba(255,255,255,.55) 50%,transparent 58%)}}
.top{{position:absolute;top:110px;left:0;right:0;text-align:center;font:500 21px Montserrat;letter-spacing:8px;color:#77777d}}
.top b{{font-weight:900;color:{INK};letter-spacing:6px}} .top i{{font-style:normal;color:{O}}}
.l1{{position:absolute;top:166px;left:0;right:0;text-align:center;direction:rtl;font:56px/1.6 Noori;color:#2a2a2e}} .l1 span{{font-family:Aslam;color:{O};font-size:1.12em}}
.hero{{position:absolute;top:262px;left:0;right:0;text-align:center;direction:rtl;font:96px/1.3 Aslam;white-space:nowrap;background:linear-gradient(180deg,{O2},{O} 60%,{OD});-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 12px 16px rgba(212,86,30,.2))}}
.hero span{{display:inline-block;margin:0 .1em}}
.en{{position:absolute;top:448px;left:0;right:0;text-align:center;font:900 50px Montserrat;letter-spacing:-.5px}} .en i{{font-style:normal;color:{O}}}
.bag{{position:absolute;left:40px;top:560px;height:640px;filter:drop-shadow(0 24px 26px rgba(0,0,0,.26))}}
.disc{{position:absolute;left:30px;top:1170px;width:400px;height:60px;border-radius:50%;background:radial-gradient(ellipse at 50% 35%,#fff,#E6E6EA 60%,#CFCFD6);box-shadow:0 18px 28px rgba(0,0,0,.15)}}
.ben{{position:absolute;left:420px;right:44px;top:560px;display:flex;flex-direction:column;gap:14px}}
.bh{{font:900 24px Montserrat;letter-spacing:4px;color:{O};margin-bottom:2px;text-align:right}}
.b{{display:flex;align-items:flex-start;gap:12px;direction:rtl;background:#fff;border-radius:20px;padding:12px 16px 10px;box-shadow:0 8px 20px rgba(0,0,0,.07)}}
.b .c{{flex:none;width:36px;height:36px;border-radius:50%;background:{G};display:flex;align-items:center;justify-content:center;margin-top:6px}}
.b .t{{font:30px/1.45 Noori;color:#2a2a2e}} .b small{{display:block;direction:ltr;text-align:right;font:600 15px Poppins;letter-spacing:.5px;color:#8a8a90}}
.fm{{position:absolute;left:44px;right:44px;top:1262px;background:#fff;border-radius:30px;padding:22px 30px 20px;box-shadow:0 14px 34px rgba(0,0,0,.09)}}
.fm .h{{display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px solid {O};padding-bottom:10px;margin-bottom:8px}}
.fm .h b{{font:900 28px Montserrat;letter-spacing:1px}} .fm .h span{{direction:rtl;font:36px/1.3 Aslam;color:{O}}}
.r{{display:flex;justify-content:space-between;font:600 25px/1.75 Poppins;border-bottom:1px dashed #DADADF}} .r:last-child{{border-bottom:none}}
.r b{{font-weight:800;color:{O}}}
.use{{position:absolute;left:44px;right:44px;top:1702px;display:flex;gap:14px}}
.use div{{flex:1;background:{INK};color:#fff;border-radius:22px;padding:14px 18px;text-align:center}}
.use small{{display:block;font:600 15px Poppins;letter-spacing:3px;opacity:.7}} .use b{{display:block;font:800 26px Poppins;margin-top:2px}}
.price{{position:absolute;left:236px;top:975px;width:230px;height:230px;border-radius:50%;background:radial-gradient(circle at 35% 30%,{O2},{O} 55%,{OD});color:#fff;text-align:center;padding-top:58px;white-space:nowrap;box-shadow:0 18px 30px rgba(166,60,15,.4),inset 0 0 0 6px rgba(255,255,255,.35);transform:rotate(-8deg);z-index:3}}
.price small{{display:block;font:700 18px Poppins;letter-spacing:3px;opacity:.9}} .price b{{display:block;font:900 44px/1.1 Montserrat;letter-spacing:-1px}} .price i{{display:block;font:700 14px Poppins;font-style:normal;letter-spacing:2px;opacity:.9;margin-top:2px}}
.ft{{position:absolute;bottom:40px;left:0;right:0;text-align:center;font:500 17px Montserrat;letter-spacing:6px;color:#8a8a90}}"""
bens="".join(f'<div class="b"><div class="c">{chk}</div><div class="t">{u}<small>{e}</small></div></div>' for u,e in ben)
rows="".join(f'<div class="r"><span>{a}</span><b>{b}</b></div>' for a,b in form)
html=f"""<div id="p"><div class="sheen"></div>
<div class="top"><b>MEGA-<i>TOX</i></b> &nbsp;·&nbsp; CLAY-BASED TOXIN BINDER</div>
<div class="l1"><span>جیب</span> پر ہلکا، <span>جانور</span> پر پورا!</div>
<div class="hero"><span>ترکی</span><span>کا</span><span>ٹاکسن</span><span>بائنڈر</span></div>
<div class="en">STRONG <i>CLAY POWER</i></div>
<div class="disc"></div><img class="bag" src="file://{bag}">
<div class="price"><small>ONLY</small><b>Rs 8,000</b><i>PER 25 KG BAG</i></div><div class="ben"><div class="bh">KEY BENEFITS</div>{bens}</div>
<div class="fm"><div class="h"><b>COMPOSITION · PER 1 KG</b><span>فارمولا</span></div>{rows}</div>
<div class="use"><div><small>DOSAGE</small><b>0.5–1 KG / TON FEED</b></div><div><small>FOR</small><b>CATTLE · GOATS · POULTRY</b></div></div>
<div class="ft">25 KG KRAFT BAG · TURKEY · SOLINKON</div></div>"""
out=d/"mega-tox-detail.png"; job=d/"job.json"
job.write_text(json.dumps({"width":1080,"height":1920,"scale":2,"css":css,"fonts":fonts,"states":[{"file":str(out),"html":html}]}))
subprocess.run(["node",str(R/"tools/htmlcaps/render.js"),str(job)],check=True,capture_output=True)
job.unlink(); (d/"page.html").unlink(missing_ok=True)
Image.open(out).convert("RGB").save(d/"mega-tox-detail.jpg",quality=95); out.unlink(); print(d/"mega-tox-detail.jpg")
