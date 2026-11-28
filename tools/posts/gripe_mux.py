import subprocess, sys
from pathlib import Path
R=Path('/home/user/video-editing-workflow'); sys.path.insert(0,str(R/'tools'))
from sfx import get
D=R/'Video Edits/Export/gripe-vo'; W=D/'work'
cuts=[2.26,4.6,5.68,8.16,9.8]
fx=[('impact',0.0,0.28),('pop',1.32,0.2)]+[('whoosh_fast',t-0.06,0.2) for t in cuts]+[('pop',2.5,0.14),('pop',2.75,0.14),('pop',3.0,0.14),('ching',4.75,0.16),('pop',5.73,0.2),('pop',7.26,0.2),('swish',8.3,0.18),('ding',8.5,0.14),('boom',9.8,0.24),('ching',11.9,0.14)]
fx=[f for f in fx if f[2]>0]
ins=['-framerate','30','-i',str(W/'frames/f%05d.jpg'),'-i',str(W/'voice-tight.wav')]
flt=['[1:a]volume=1.0,aresample=48000[a0]']
for k,(n,t,v) in enumerate(fx,start=2):
    ins+=['-i',str(get(n,'pro'))]; flt.append(f'[{k}:a]adelay={int(t*1000)}|{int(t*1000)},volume={v},aresample=48000[a{k-1}]')
n=len(fx)+1
flt.append(''.join(f'[a{i}]' for i in range(n))+f'amix=inputs={n}:normalize=0,loudnorm=I=-14:TP=-1.5[out]')
out=D/'gripe-vo.mp4'
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(flt),'-map','0:v','-map','[out]','-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-shortest',str(out)],check=True)
print(out)
