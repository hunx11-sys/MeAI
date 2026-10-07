# 30초 극화 패러디 광고 배경음 — 전부 합성(저작권 없음)
import numpy as np, wave, sys
from scipy.signal import lfilter
SR=44100; T=30.0; N=int(SR*T); rng=np.random.default_rng(7)
L=np.zeros(N); R=np.zeros(N)
def add(sig,t,g=1.0,pan=0.0):
    i=int(t*SR); j=min(N,i+len(sig))
    if i<N: L[i:j]+=g*(1-pan)*sig[:j-i]; R[i:j]+=g*(1+pan)*sig[:j-i]
def lp(x,a): return lfilter([a],[1,a-1],x)
def tt(d): return np.arange(int(d*SR))/SR
def drone(f,d,g=1):
    t=tt(d); s=sum(np.sin(2*np.pi*f*m*t+np.sin(2*np.pi*.3*t)*m)/m for m in (1,2,3,5))
    s+=.3*lp(rng.standard_normal(len(t)),.01)
    return s*np.minimum(1,t/1.5)*np.minimum(1,(d-t)/1.0)*g
def beat():                       # 심장 박동 (쿵-쿵)
    t=tt(.5); b=np.sin(2*np.pi*(40+30*np.exp(-t*30))*t)*np.exp(-t*10)
    s=np.zeros(int(.8*SR)); s[:len(b)]+=b; k=int(.22*SR); s[k:k+len(b)]+=.7*b; return s
def hit(d=2.5):                   # 묵직한 충격음
    t=tt(d); boom=np.sin(2*np.pi*(32+60*np.exp(-t*6))*t)*np.exp(-t*1.4)
    crack=rng.standard_normal(len(t))*np.exp(-t*25)*.8
    air=lp(rng.standard_normal(len(t)),.04)*np.exp(-t*2)*.8
    return boom*1.2+crack+air
def whoosh(d=.5,up=True):
    t=tt(d); x=t/d; env=(x if up else 1-x)**2*np.sin(np.pi*x)
    return lp(rng.standard_normal(len(t)),.05)*env*3
def tick(f=2200):
    t=tt(.05); return np.sin(2*np.pi*f*t)*np.exp(-t*120)*.6
def ding(f,d=1.2):
    t=tt(d); return (np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*f*3*t))*np.exp(-t*4)*.4
def pad(fs,d,att=.8,rel=1.2):
    t=tt(d); s=sum(2*((t*f*(1+dd/100))%1)-1 for f in fs for dd in (-.2,0,.2))/len(fs)/3
    return lp(s,.03)*np.minimum(1,t/att)*np.clip((d-t)/rel,0,1)
# 장면1 질문 (0~6.6) : 낮은 긴장 드론 + 심장박동
add(drone(41.2,6.8),0,.35); add(hit(),0,.7)
for k in range(6): add(beat(),.6+k*1.0,.6)
add(whoosh(.6),6.0,.6)
# 장면2 도구 6종 (6.6~11.6)
add(hit(1.5),6.6,.6)
for i in range(6): add(hit(.8),6.85+i*.45,.35,(-.4,.4)[i%2]); add(tick(1800+i*150),6.85+i*.45,.5)
add(whoosh(.5),9.05,.7); add(hit(3),9.55,1.0)
for k in range(2): add(beat(),10.4+k*.6,.55)
# 장면3 극한 클로즈업 (11.6~16.6) : 두-둥
add(hit(),11.6,1.0); add(hit(),11.85,.9); add(drone(36.7,5.0),11.6,.4)
add(whoosh(.4),13.7,.6); add(hit(1.6),14.1,.8)
for k in range(4): add(beat(),14.6+k*.5,.45)
# 장면4 좌우 대결 (16.6~20.2) : 점점 빨라지는 시계 + 10번 완료음
add(whoosh(.5),16.1,.5)
for k in range(48):
    tk=16.6+3.6*(k/48)**.85; add(tick(2600 if k%2 else 2000),tk,.45,(.5 if k%2 else -.5))
for k in range(10): add(ding(880*2**((k%5)/12*2)), 16.6+.36*(k+1)-.02,.45,.5)
add(beat(),20.2,.8)                      # 왼쪽은 겨우 1건
# 정적 20.2~20.9 → 쾅
add(whoosh(.35),20.55,.8); add(hit(3),20.9,1.2)
add(pad([55,82.4,110,130.8],2.7,att=.3),20.95,.5)
# 장면5 엔딩 (23.6~30)
add(whoosh(.6),23.0,.6)
for i in range(6): add(whoosh(.3,False),23.65+.05*i,.25,(-.6,.6)[i%2])
for i in range(6): add(ding([523.25,587.33,659.25,783.99,880,1046.5][i],.9),24.8+i*.25,.4)
add(pad([130.81,164.81,196,246.94],3.4,att=.6),23.7,.4)
add(hit(3),27.1,1.0)
add(pad([65.4,130.81,196,261.63,329.63,392],2.9,att=.4,rel=1.0),27.1,.75)
for k,f in enumerate([1046.5,1318.5,1568]): add(ding(f,2.0),27.3+k*.18,.5,(-.5,0,.5)[k])

# ── 타격감 보강 ──
def braam(d=2.6,f=43.65):
    t=tt(d); s=sum(np.sign(np.sin(2*np.pi*f*m*t*(1+0.002*k)))/m for m in (1,2,3) for k in (-1,1))
    return lp(s,.02)*np.exp(-t*1.2)*np.minimum(1,t*30)*.5
def tom(f=90):
    t=tt(.45); return np.sin(2*np.pi*(f+60*np.exp(-t*25))*t)*np.exp(-t*7)
for h in (1.0,3.0,12.3,22.5): add(hit(1.2),h,.55)
add(whoosh(.4),3.5,.8); add(hit(2.0),3.9,.9)
add(braam(),9.55,.8); add(braam(3,36.7),11.6,.7); add(braam(3.2,32.7),20.9,1.0)
add(hit(1.5),21.05,.7)
for k in range(28):                      # 점점 빨라지는 북
    tk=16.6+3.6*(k/28)**.8; add(tom(80 if k%2 else 110),tk,.5,(-.3 if k%2 else .3))
for k in range(8): add(tom(70),3.95+k*.33,.35)
mix=np.stack([L,R],1); mix=np.tanh(mix*1.2); mix/=np.max(np.abs(mix))*1.08
f=int(.45*SR); mix[-f:]*=np.linspace(1,0,f)[:,None]
with wave.open(sys.argv[1] if len(sys.argv)>1 else 'music.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype('<i2').tobytes())
print('ok')
