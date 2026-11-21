#!/usr/bin/env python3
"""Khyber Traders WhatsApp contact post (locked product-post look, WhatsApp green). Needs the cleaned QR at
Video Edits/Export/whatsapp-post/work/waqr.png (crop of the owner's WhatsApp QR screenshot, binarised, 3x NEAREST).
Verify the QR still decodes after every change."""
import json,subprocess
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[2]
F=lambda g: str(next(R.joinpath('fonts').rglob(g)))
fonts=[{"family":"Noori","path":F("JameelNooriNastaleeq-400.ttf"),"weight":400,"style":"normal"},
 {"family":"Aslam","path":F("Aslam-400.ttf"),"weight":400,"style":"normal"},
 {"family":"Montserrat","path":F("Montserrat-900.ttf"),"weight":900,"style":"normal"},
 {"family":"Montserrat","path":F("Montserrat-500.ttf"),"weight":500,"style":"normal"},
 {"family":"Poppins","path":F("Poppins-600.ttf"),"weight":600,"style":"normal"},
 {"family":"Poppins","path":F("Poppins-700.ttf"),"weight":700,"style":"normal"},
 {"family":"Poppins","path":F("Poppins-800.ttf"),"weight":800,"style":"normal"}]
d=R/"Video Edits/Export/whatsapp-post"; QR=d/"work"/"waqr.png"
G="#14A94F"; G2="#25D366"; GD="#0B6E4F"; INK="#1B1B1F"
wa='<svg width="34" height="34" viewBox="0 0 24 24"><path fill="#fff" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2c-1.5 0-3-.4-4.3-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5c-.2 0-.4.1-.6.3-.2.2-.8.8-.8 2s.8 2.3.9 2.5c.1.2 1.7 2.6 4.2 3.6 1.5.7 2.1.7 2.9.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.2-.2-.5-.3z"/></svg>'
E=lambda t,s="inherit",c=G,w=800: f'<bdi style="font:{w} {s} Poppins;color:{c};letter-spacing:0;margin:0 .22em">{t}</bdi>'
css=f"""
*{{margin:0;padding:0;box-sizing:border-box}}
#p{{position:absolute;inset:0;overflow:hidden;font-family:Poppins;color:{INK};background:radial-gradient(ellipse 75% 50% at 50% 48%,#FFFFFF 0%,#F3F4F3 55%,#E1E5E2 100%)}}
.sheen{{position:absolute;inset:0;background:linear-gradient(115deg,transparent 42%,rgba(255,255,255,.55) 50%,transparent 58%)}}
.gn{{position:absolute;top:104px;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:0;white-space:nowrap;border-radius:60px;overflow:hidden;
 box-shadow:0 12px 26px rgba(20,169,79,.22)}}
.gn b{{background:linear-gradient(135deg,{G2},{G});color:#fff;font:800 24px Poppins;letter-spacing:5px;padding:12px 26px 10px 30px}}
.gn span{{background:#fff;color:{G};font:44px/1 Aslam;padding:6px 28px 12px 24px;direction:rtl}}
.l1{{position:absolute;top:196px;left:0;right:0;text-align:center;direction:rtl;font:54px/1.6 Noori;color:#2a2a2e}}
.hero{{position:absolute;top:302px;left:0;right:0;display:flex;justify-content:center;align-items:center;gap:30px;direction:rtl;white-space:nowrap;
 filter:drop-shadow(0 14px 18px rgba(20,169,79,.2))}}
.hero .n{{font:900 104px/1 Montserrat;letter-spacing:-2px;background:linear-gradient(180deg,{G2},{G} 55%,{GD});-webkit-background-clip:text;color:transparent;direction:ltr}}
.hero .u{{font:112px/1.35 Aslam;background:linear-gradient(180deg,{G2},{G} 55%,{GD});-webkit-background-clip:text;color:transparent}}
.en{{position:absolute;top:556px;left:0;right:0;text-align:center;font:500 19px Montserrat;letter-spacing:5px;color:#5f6460}}
.en b{{font-weight:900;color:{INK};letter-spacing:5px}} .en i{{font-style:normal;color:{G};font-weight:900}}
.card{{position:absolute;left:50%;top:640px;transform:translateX(-50%);width:600px;background:#fff;border-radius:46px;padding:40px 0 34px;text-align:center;
 box-shadow:0 34px 60px rgba(0,0,0,.14),0 2px 0 rgba(0,0,0,.03)}}
.card .hd{{display:flex;align-items:center;justify-content:center;gap:14px;font:800 30px Poppins}}
.card .hd em{{width:58px;height:58px;border-radius:50%;background:{G2};display:flex;align-items:center;justify-content:center}}
.card small{{display:block;font:600 17px Poppins;letter-spacing:3px;color:#8a8f8b;margin-top:6px}}
.qw{{position:relative;width:420px;height:420px;margin:34px auto 0}}
.qw img{{width:420px;height:420px;image-rendering:pixelated;display:block}}
.br{{position:absolute;width:60px;height:60px;border:8px solid {G2}}}
.b1{{left:-26px;top:-26px;border-right:none;border-bottom:none;border-radius:20px 0 0 0}}
.b2{{right:-26px;top:-26px;border-left:none;border-bottom:none;border-radius:0 20px 0 0}}
.b3{{left:-26px;bottom:-26px;border-right:none;border-top:none;border-radius:0 0 0 20px}}
.b4{{right:-26px;bottom:-26px;border-left:none;border-top:none;border-radius:0 0 20px 0}}
.card .sc{{font:700 22px Poppins;color:{G};margin-top:40px;letter-spacing:.5px}}
.num{{position:absolute;top:1350px;left:50%;transform:translateX(-50%);white-space:nowrap;display:flex;align-items:center;gap:16px;
 background:linear-gradient(135deg,{G2},{G} 55%,{GD});color:#fff;font:800 52px Poppins;letter-spacing:.5px;padding:18px 46px 16px 24px;border-radius:80px;
 box-shadow:0 20px 36px rgba(20,169,79,.35)}}
.num em{{width:66px;height:66px;border-radius:50%;background:rgba(255,255,255,.2);display:flex;align-items:center;justify-content:center}}
.l4{{position:absolute;top:1498px;left:70px;right:70px;text-align:center;direction:rtl;font:50px/1.75 Noori;color:#2f3133}}
.l5{{position:absolute;top:1720px;left:0;right:0;text-align:center;font:600 28px Poppins;color:#55595c}}
.l5 b{{color:{INK};font-weight:800}} .l5 i{{font-style:normal;color:{G};font-weight:700}}
.ft{{position:absolute;bottom:46px;left:0;right:0;text-align:center;font:500 17px Montserrat;letter-spacing:7px;color:#8a8f8b}}
"""
html=f"""<div id="p"><div class="sheen"></div>
<div class="gn"><b>GOOD NEWS</b><span>خوشخبری</span></div>
<div class="l1">آپ کی سہولت کے لیے ہماری {E('Team','42px')} اب {E('WhatsApp','42px')} پر</div>
<div class="hero"><div class="n">18 HOURS</div><div class="u">دستیاب</div></div>
<div class="en"><b>KHYBER <i>TRADERS</i></b> &nbsp;·&nbsp; ONLINE ORDERS SALES TEAM</div>
<div class="card"><div class="hd"><em>{wa}</em>Khyber Traders</div><small>WHATSAPP BUSINESS</small>
 <div class="qw"><img src="file://{QR}"><i class="br b1"></i><i class="br b2"></i><i class="br b3"></i><i class="br b4"></i></div>
 <div class="sc">Scan to start a WhatsApp chat</div></div>
<div class="num"><em>{wa}</em>0310-2999262</div>
<div class="l4">{E('QR Code','42px')} اسکین کریں یا اس نمبر پر رابطہ کریں،<br>ہر چیز کی {E('Details','42px')} وہیں مل جائیں گی</div>
<div class="l5"><b>Khyber Traders</b> · <i>Online Orders Sales Team</i></div>
<div class="ft">WHATSAPP · ONLINE ORDERS · 18 HOURS A DAY</div></div>"""
out=d/"whatsapp-post.png"; job=d/"job.json"
job.write_text(json.dumps({"width":1080,"height":1920,"scale":2,"css":css,"fonts":fonts,"states":[{"file":str(out),"html":html}]}))
subprocess.run(["node",str(R/"tools/htmlcaps/render.js"),str(job)],check=True,capture_output=True)
job.unlink(); (d/"page.html").unlink(missing_ok=True)
Image.open(out).convert("RGB").save(out); print(out)
