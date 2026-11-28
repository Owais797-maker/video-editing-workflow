import subprocess, sys
from pathlib import Path
R=Path('/home/user/video-editing-workflow'); sys.path.insert(0,str(R/'tools'))
from sfx import get
D=R/'Video Edits/Export/milkolin-vo'; W=D/'work'
cuts=[4.18,7.98,9.24,13.46,16.32,22.88]
fx=[('impact',0.0,0.28),('pop',0.55,0.18),('glitch',2.55,0.14),('pop',2.7,0.2)]+[('whoosh_fast',t-0.06,0.2) for t in cuts]+[('ding',6.95,0.14),('ching',8.3,0.16),('pop',9.55,0.2),('swish',11.3,0.16),('swoosh_up',14.0,0.18),('pop',16.95,0.2),('ding',18.9,0.16),('boom',22.88,0.26),('ching',24.2,0.14)]
fx=[f for f in fx if f[2]>0]
ins=['-framerate','30','-i',str(W/'frames/f%05d.jpg'),'-i',str(W/'voice-tight.wav')]
flt=['[1:a]volume=1.0,aresample=48000[a0]']
for k,(n,t,v) in enumerate(fx,start=2):
    ins+=['-i',str(get(n,'pro'))]; flt.append(f'[{k}:a]adelay={int(t*1000)}|{int(t*1000)},volume={v},aresample=48000[a{k-1}]')
n=len(fx)+1
flt.append(''.join(f'[a{i}]' for i in range(n))+f'amix=inputs={n}:normalize=0,loudnorm=I=-14:TP=-1.5[out]')
out=D/'milkolin-vo.mp4'
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(flt),'-map','0:v','-map','[out]','-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-shortest',str(out)],check=True)
print(out)
