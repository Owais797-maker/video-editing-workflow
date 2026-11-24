#!/usr/bin/env python3
"""LOCKED product-post series (owner loved it, 2026-11-21): 9:16 4K reseller posts.

    python3 tools/posts/product_post.py tools/posts/<product>.json   ->  Video Edits/Export/<name>/<name>.jpg

See styles/product-posts/style.md for the look and the rules. JSON keys: name, src (cutout in the repo), up
(upscale 2-3 for small cutouts), P/P2/PD (product colour light->dark), A/AT (2nd badge colour + its text),
top, l1, hero, en, c1/c2 ([small, big] badge text), c1x/c1y/c2x/c2y, l4, l5, ft, sizes/tops (optional).
"""
import json,subprocess,sys
from pathlib import Path
from PIL import Image
R=Path('/home/user/video-editing-workflow')
F=lambda g: str(next(R.joinpath('fonts').rglob(g)))
fonts=[{"family":"Noori","path":F("JameelNooriNastaleeq-400.ttf"),"weight":400,"style":"normal"},
 {"family":"Aslam","path":F("Aslam-400.ttf"),"weight":400,"style":"normal"},
 {"family":"Montserrat","path":F("Montserrat-900.ttf"),"weight":900,"style":"normal"},
 {"family":"Montserrat","path":F("Montserrat-500.ttf"),"weight":500,"style":"normal"},
 {"family":"Poppins","path":F("Poppins-600.ttf"),"weight":600,"style":"normal"},
 {"family":"Poppins","path":F("Poppins-700.ttf"),"weight":700,"style":"normal"},
 {"family":"Poppins","path":F("Poppins-800.ttf"),"weight":800,"style":"normal"}]
c=json.load(open(sys.argv[1]))
if c.get("src"):
    from PIL import ImageFilter
    w=R/"Video Edits/Export"/c["name"]/"work"; w.mkdir(parents=True,exist_ok=True)
    im=Image.open(R/c["src"]).convert("RGBA"); u=int(c.get("up",2))
    im=im.resize((im.width*u,im.height*u),Image.LANCZOS).filter(ImageFilter.UnsharpMask(2,50,2))
    c["img"]=str(w/"product-up.png"); im.save(c["img"])
P,P2,PD,A,AT=c["P"],c["P2"],c["PD"],c["A"],c["AT"]; INK="#1B1B1F"
chk=lambda col:f'<svg width="26" height="26" viewBox="0 0 24 24"><path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="{col}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
css=f"""
*{{margin:0;padding:0;box-sizing:border-box}}
#p{{position:absolute;inset:0;overflow:hidden;font-family:Poppins;color:{INK};
 background:radial-gradient(ellipse 70% 45% at 52% 62%,#FFFFFF 0%,#F4F4F6 45%,#E2E3E8 100%)}}
.sheen{{position:absolute;inset:0;background:linear-gradient(115deg,transparent 42%,rgba(255,255,255,.55) 50%,transparent 58%)}}
.top{{position:absolute;top:118px;left:0;right:0;text-align:center;font:500 22px Montserrat;letter-spacing:8px;color:#77777d}}
.top b{{font-weight:900;color:{INK};letter-spacing:6px}} .top i{{font-style:normal;color:{P}}}
.l1{{position:absolute;top:{c.get("l1_top",196)}px;left:0;right:0;text-align:center;direction:rtl;font:{c.get("l1_size",66)}px/1.55 Noori;color:#2a2a2e}}
.l1 span{{font-family:Aslam;color:{P};font-size:1.12em}}
.hero{{position:absolute;top:{c.get("hero_top",322)}px;left:0;right:0;text-align:center;direction:rtl;font:{c.get('hero_size',150)}px/1.3 Aslam;
 background:linear-gradient(180deg,{P2} 0%,{P} 60%,{PD} 100%);-webkit-background-clip:text;color:transparent;
 filter:drop-shadow(0 14px 18px rgba(0,0,0,.14))}}
.tonic{{position:absolute;top:{c.get("en_top",548)}px;left:0;right:0;text-align:center}}
.tonic b{{display:inline-block;font:900 {c.get('en_size',92)}px/1 Montserrat;letter-spacing:-1px;color:{INK}}}
.tonic b i{{font-style:normal;color:{P}}}
.disc{{position:absolute;left:50%;top:{c.get("disc_top",1482)}px;width:600px;height:90px;transform:translateX(-50%);border-radius:50%;
 background:radial-gradient(ellipse at 50% 35%,#FFFFFF 0%,#ECECEF 60%,#D6D6DC 100%);box-shadow:0 26px 40px rgba(0,0,0,.16)}}
.bag{{position:absolute;left:50%;top:{c.get('bag_top',730)}px;height:{c.get('bag_h',800)}px;transform:translateX(-50%);filter:drop-shadow(0 26px 30px rgba(0,0,0,.26))}}
.chip{{position:absolute;display:flex;align-items:center;gap:14px;padding:14px 30px 14px 16px;border-radius:50px;
 font:800 27px/1.05 Poppins;letter-spacing:.5px;box-shadow:0 16px 30px rgba(0,0,0,.22);z-index:2}}
.chip .ic{{width:46px;height:46px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex:none}}
.chip small{{display:block;font:600 17px Poppins;letter-spacing:2px;opacity:.85}}
.c1{{left:{c.get('c1x',120)}px;top:{c.get('c1y',1040)}px;background:linear-gradient(135deg,{P2},{P});color:#fff;transform:rotate(-4deg)}}
.c1 .ic{{background:#fff}}
.c2{{right:{c.get('c2x',120)}px;top:{c.get('c2y',1262)}px;background:{A};color:{AT};transform:rotate(3deg)}}
.c2 .ic{{background:{P}}}
.l4{{position:absolute;top:{c.get('l4_top',1620)}px;left:0;right:0;text-align:center;font:600 46px Poppins;letter-spacing:-.5px}}
.l4 i{{font-style:normal;color:{P};font-weight:700}}
.l5{{position:absolute;top:{c.get('l5_top',1694)}px;left:0;right:0;text-align:center;direction:rtl;font:50px/1.6 Noori;color:#3a3a3e}}
.l5 span{{font-family:Aslam;color:{P};font-size:1.15em}}
.ft{{position:absolute;bottom:46px;left:0;right:0;text-align:center;font:500 18px Montserrat;letter-spacing:6px;color:#8a8a90}}
"""
html=f"""<div id="p"><div class="sheen"></div>
<div class="top">{c['top']}</div><div class="l1">{c['l1']}</div><div class="hero">{c['hero']}</div>
<div class="tonic"><b>{c['en']}</b></div>
<div class="disc"></div><img class="bag" src="file://{c['img']}">
<div class="chip c1"><div class="ic">{chk(P)}</div><div><small>{c['c1'][0]}</small>{c['c1'][1]}</div></div>
<div class="chip c2"><div class="ic">{chk('#fff')}</div><div><small>{c['c2'][0]}</small>{c['c2'][1]}</div></div>
<div class="l4">{c['l4']}</div><div class="l5">{c['l5']}</div><div class="ft">{c['ft']}</div></div>"""
d=R/"Video Edits/Export"/c["name"]; d.mkdir(exist_ok=True); out=d/(c["name"]+".png"); job=d/"job.json"
job.write_text(json.dumps({"width":1080,"height":1920,"scale":2,"css":css,"fonts":fonts,"states":[{"file":str(out),"html":html}]}))
subprocess.run(["node",str(R/"tools/htmlcaps/render.js"),str(job)],check=True,capture_output=True)
job.unlink(); (d/"page.html").unlink(missing_ok=True)
im=Image.open(out).convert("RGB"); im.save(d/(c["name"]+".jpg"),quality=95); out.unlink(); print(d/(c["name"]+".jpg"))
