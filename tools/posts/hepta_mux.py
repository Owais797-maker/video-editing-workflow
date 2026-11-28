import subprocess, sys
from pathlib import Path
R=Path('/home/user/video-editing-workflow'); sys.path.insert(0,str(R/'tools'))
from sfx import get
D=R/'Video Edits/Export/hepta-vo'; W=D/'work'
cuts=[2.9,5.94,7.78,9.66,11.92,14.08,18.54,21.26]
fx=[('impact',0.0,0.28),('pop',1.5,0.2)]+[('whoosh_fast',t-0.06,0.2) for t in cuts]+[('pop',3.3,0.12),('pop',3.48,0.12),('pop',3.66,0.12),('pop',3.84,0.12),('glitch',5.94,0.16),('impact',6.0,0.2),('ching',7.9,0.16),('pop',9.7,0.18),('pop',10.6,0.18),('pop',11.1,0.18),('ding',12.6,0.14),('pop',14.3,0.18),('ding',16.1,0.16),('swoosh_up',19.4,0.16),('boom',21.26,0.24),('pop',21.6,0.14),('pop',21.75,0.14),('pop',21.9,0.14)]
fx=[f for f in fx if f[2]>0]
ins=['-framerate','30','-i',str(W/'frames/f%05d.jpg'),'-i',str(W/'voice-tight.wav')]
flt=['[1:a]volume=1.0,aresample=48000[a0]']
for k,(n,t,v) in enumerate(fx,start=2):
    ins+=['-i',str(get(n,'pro'))]; flt.append(f'[{k}:a]adelay={int(t*1000)}|{int(t*1000)},volume={v},aresample=48000[a{k-1}]')
n=len(fx)+1
flt.append(''.join(f'[a{i}]' for i in range(n))+f'amix=inputs={n}:normalize=0,loudnorm=I=-14:TP=-1.5[out]')
out=D/'hepta-vo.mp4'
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(flt),'-map','0:v','-map','[out]','-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-shortest',str(out)],check=True)
print(out)
