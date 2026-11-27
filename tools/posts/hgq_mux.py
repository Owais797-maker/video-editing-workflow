import subprocess, sys
from pathlib import Path
R=Path('/home/user/video-editing-workflow'); sys.path.insert(0,str(R/'tools'))
from sfx import get
D=R/'Video Edits/Export/hg-qurbani-vo'; W=D/'work'
cuts=[3.46,6.8,8.62,11.56,14.16,17.38,20.88,24.18,26.72]
fx=[('impact',0.0,0.32),('pop',2.5,0.22)]+[('whoosh_fast',t-0.06,0.2) for t in cuts]+[('pop',6.9,0.2),('ching',7.2,0.14),('riser',8.0,0.0),('ding',11.0,0.12),('pop',14.9,0.18),('keys',17.6,0.22),('pop',21.5,0.18),('pop',21.96,0.18),('pop',23.26,0.22),('swoosh_up',24.7,0.18),('boom',26.72,0.28),('ching',27.6,0.14)]
fx=[f for f in fx if f[2]>0]
ins=['-framerate','30','-i',str(W/'frames/f%05d.jpg'),'-i',str(W/'voice-tight.wav')]
flt=['[1:a]volume=1.0,aresample=48000[a0]']
for k,(n,t,v) in enumerate(fx,start=2):
    ins+=['-i',str(get(n,'pro'))]; flt.append(f'[{k}:a]adelay={int(t*1000)}|{int(t*1000)},volume={v},aresample=48000[a{k-1}]')
n=len(fx)+1
flt.append(''.join(f'[a{i}]' for i in range(n))+f'amix=inputs={n}:normalize=0,loudnorm=I=-14:TP=-1.5[out]')
out=D/'hg-qurbani-vo.mp4'
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(flt),'-map','0:v','-map','[out]','-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-shortest',str(out)],check=True)
print(out)
