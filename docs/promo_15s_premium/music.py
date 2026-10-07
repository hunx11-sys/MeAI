import numpy as np, wave, sys
SR=44100; T=15.0; N=int(SR*T); BEAT=.5; rng=np.random.default_rng(3)
L=np.zeros(N); R=np.zeros(N)
def add(sig,t,g=1.0,pan=0.0):
    i=int(t*SR); j=min(N,i+len(sig))
    if i<N: L[i:j]+=g*(1-pan)*sig[:j-i]; R[i:j]+=g*(1+pan)*sig[:j-i]
def lp(x,a):
    y=np.zeros_like(x); a=np.broadcast_to(np.asarray(a,dtype=float),x.shape)
    for i in range(1,len(x)): y[i]=y[i-1]+a[i]*(x[i]-y[i-1])
    return y
def pad(freqs,dur,att=1.2,rel=1.5):
    n=int(dur*SR); t=np.arange(n)/SR; s=np.zeros(n)
    for f in freqs:
        for d in (-0.15,0.0,0.17): s+=2*((t*f*(1+d/100))%1)-1
    s=lp(s/(len(freqs)*3),0.035)
    e=np.minimum(1,t/att)*np.minimum(1,(dur-t)/rel); return s*np.clip(e,0,1)
def sub(f,dur):
    n=int(dur*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*f*t)*np.exp(-t*4)*np.minimum(1,t*80)
def kick():
    n=int(.5*SR); t=np.arange(n)/SR; f=42+70*np.exp(-t*22); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*6)
def tick():
    n=int(.03*SR); t=np.arange(n)/SR; return np.diff(np.concatenate([[0],rng.standard_normal(n)]))*np.exp(-t*160)*.5
def hit():
    n=int(2.0*SR); t=np.arange(n)/SR
    boom=np.sin(2*np.pi*(36+30*np.exp(-t*4))*t)*np.exp(-t*1.6)
    air=lp(rng.standard_normal(n),0.05)*np.exp(-t*2.5)*.6
    return boom+air
def swell(dur):
    n=int(dur*SR); t=np.arange(n)/SR; nz=lp(rng.standard_normal(n),0.02+0.2*(t/dur)**2)
    return nz*(t/dur)**2.5*1.2
def bell(f,dur=2.5):
    n=int(dur*SR); t=np.arange(n)/SR; return (np.sin(2*np.pi*f*t)+.4*np.sin(2*np.pi*f*2.01*t))*np.exp(-t*2.2)*.35
A1,B1,C1=2.5,3.5,12.5
# 화성 : Am9 → Fmaj7 → C → G (낮은 패드)
CH=[[110,130.81,164.81,196,246.94],[87.31,110,130.81,164.81],[130.81,164.81,196,246.94],[98,123.47,146.83,196]]
add(pad(CH[0],A1+.6,att=1.5),0,.55)
add(swell(A1),0,.5)
for k in range(9):                                   # 도구 구간 : 3박씩 화음 바뀜
    t=B1+k*1.0
    if t<C1: add(pad(CH[(k//1)%4],1.4,att=.25,rel=.5),t,.45)
for b in range(int(T/BEAT)):
    t=b*BEAT
    if t<A1:
        if b%2==0: add(tick(),t,.6,.3)
        continue
    if t>=C1+1.0: continue
    add(kick(),t,.9)
    add(sub(55 if (b//2)%2==0 else 43.65, .45),t,.5)
    add(tick(),t+.25,.5,-.4)
add(hit(),A1,1.0); add(hit(),B1,.8)
for i in range(1,6): add(hit(),B1+i*1.5,.45)
add(hit(),C1,1.1)
add(pad([110,164.81,220,261.63,329.63],T-C1,att=.8,rel=1.2),C1,.6)
for k,f in enumerate([880,1318.5,1760]): add(bell(f),C1+.15+k*.18,.6,(-.5,0,.5)[k])
mix=np.stack([L,R],1); mix=np.tanh(mix*1.1); mix/=np.max(np.abs(mix))*1.08
fade=int(.5*SR); mix[-fade:]*=np.linspace(1,0,fade)[:,None]
with wave.open(sys.argv[1] if len(sys.argv)>1 else 'music.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype('<i2').tobytes())
print('ok')
