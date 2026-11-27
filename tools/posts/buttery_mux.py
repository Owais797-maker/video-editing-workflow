import subprocess, sys
from pathlib import Path
R=Path('/home/user/video-editing-workflow'); sys.path.insert(0,str(R/'tools'))
from sfx import get
D=R/'Video Edits/Export/buttery-vo'; W=D/'work'
cuts=[4.38,5.56,9.58,12.96,15.2,17.74]
fx=[('impact',0.0,0.3),('swish',2.56,0.18)]+[('whoosh_fast',t-0.06,0.2) for t in cuts]+[('pop',4.45,0.22),('ching',4.9,0.14),('riser',5.0,0.12),('ding',6.0,0.16),('pop',6.2,0.2),('swish',7.28,0.16),('ding',10.0,0.16),('pop',11.44,0.2),('pop',13.0,0.2),('ching',14.1,0.16),('pop',14.3,0.14),('pop',14.6,0.14),('swoosh_up',16.8,0.18),('boom',17.74,0.28),('ching',18.95,0.14)]
fx=[f for f in fx if f[2]>0]
ins=['-framerate','30','-i',str(W/'frames/f%05d.jpg'),'-i',str(W/'voice-tight.wav')]
flt=['[1:a]volume=1.0,aresample=48000[a0]']
for k,(n,t,v) in enumerate(fx,start=2):
    ins+=['-i',str(get(n,'pro'))]; flt.append(f'[{k}:a]adelay={int(t*1000)}|{int(t*1000)},volume={v},aresample=48000[a{k-1}]')
n=len(fx)+1
flt.append(''.join(f'[a{i}]' for i in range(n))+f'amix=inputs={n}:normalize=0,loudnorm=I=-14:TP=-1.5[out]')
out=D/'buttery-vo.mp4'
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(flt),'-map','0:v','-map','[out]','-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-shortest',str(out)],check=True)
print(out)
