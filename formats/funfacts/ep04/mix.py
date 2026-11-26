import numpy as np, librosa, soundfile as sf
from scipy.signal import butter, sosfiltfilt
SR=48000; D=27.8; N=int(D*SR)
L=lambda p: librosa.load(p,sr=SR,mono=True)[0]
A='/home/claude/ff4/audio/'
v=L(A+'voice.mp3'); v=v/np.max(np.abs(v))*0.89
# silences ajoutés aux pauses détectées (coupe au milieu du silence) : (instant dans la voix brute, durée ajoutée)
CUTS=[(7.29,0.3),(11.09,0.4),(13.98,0.5),(18.42,0.3),(23.23,0.4)]
parts=[];prev=0
for c,g in CUTS:
    i=int(c*SR); parts+=[v[prev:i],np.zeros(int(g*SR))]; prev=i
parts.append(v[prev:]); vv=np.concatenate(parts)
voice=np.zeros(N); voice[:min(N,len(vv))]=vv[:N]
pres=sosfiltfilt(butter(2,[2000,5000],btype='band',fs=SR,output='sos'),voice)
voice=voice+0.4*pres
voice=voice-sosfiltfilt(butter(2,120,btype='low',fs=SR,output='sos'),voice)*0.7
# musique : boucle sans couture (la fin s'enchaîne sur le début)
m=L(A+'music.mp3'); X=int(1.5*SR)
mus=m[:N].copy(); fi=np.linspace(0,1,X)
mus[:X]=m[:X]*fi+m[N:N+X]*(1-fi)
mus=mus/np.sqrt(np.mean(mus**2))*0.0251
mid=sosfiltfilt(butter(2,[350,3500],btype='band',fs=SR,output='sos'),mus)
env=np.abs(voice); k=int(0.25*SR); env=np.convolve(env,np.ones(k)/k,'same'); env=np.clip(env/0.08,0,1)
duck=1-0.8*env
out=np.zeros(N)
def fx(p,t,g,dur=1.2,off=0.0):
    x=L(p); x=x[int(off*SR):int((off+dur)*SR)]; x=x/(np.max(np.abs(x))+1e-9)
    f=int(0.08*SR); x[-f:]*=np.linspace(1,0,f); x[:int(0.005*SR)]*=np.linspace(0,1,int(0.005*SR))
    i=int(t*SR); e=min(N,i+len(x)); out[i:e]+=g*x[:e-i]
def beep(t,g,f=1800,d=0.12):
    n=int(d*SR); tt=np.arange(n)/SR; x=np.sin(2*np.pi*f*tt)*np.minimum(1,np.minimum(tt/0.005,(d-tt)/0.02))
    i=int(t*SR); out[i:i+n]+=g*x
def synth_pop(t,g,f0=900):
    n=int(0.09*SR); tt=np.arange(n)/SR; x=np.sin(2*np.pi*(f0+800*np.exp(-tt*40))*tt)*np.exp(-tt*45)
    i=int(t*SR); out[i:i+n]+=g*x
def synth_tick(t,g):
    n=int(0.03*SR); x=np.random.RandomState(int(t*100)).randn(n)*np.exp(-np.arange(n)/SR*250)
    x=np.convolve(x,[1,-0.95],'same'); i=int(t*SR); out[i:i+n]+=g*x/np.max(np.abs(x))
for k,t in enumerate([0.75,1.15,1.55,1.95]): synth_pop(t,0.07,700+k*120)   # témoins qui arrivent
synth_pop(3.52,0.08,700)                          # carte expérience
beep(4.4,0.035,620,0.10); beep(4.55,0.035,620,0.10)   # interphone
synth_pop(7.80,0.08,900)                          # carte résultat
for k in range(6): synth_tick(8.9+k*0.15,0.05)    # barre 85 %
fx(A+'impact.mp3',13.61,0.12,0.9)                 # 31 %
for k in range(5): synth_tick(15.46+k*0.15,0.05)  # bulles
fx(A+'swirl.mp3',18.1,0.07,0.9)                   # responsabilité qui s'éparpille
synth_pop(20.22,0.09,1200)                        # l'antidote
synth_tick(21.4,0.07)                             # main qui pointe
fx(A+'magic.mp3',22.39,0.13,1.4)                  # appel au 15
for k,t in enumerate([25.7,26.0,26.3,26.6]): synth_pop(t,0.04,1060-k*120)   # la foule se disperse
mus_d=(mus-mid*0.6*env)*duck
mix=voice+mus_d+out
import pyloudnorm as pyln
meter=pyln.Meter(SR); lu=meter.integrated_loudness(mix)
mix=mix*10**((-12.6-lu)/20)
mix=np.tanh(mix*1.2)/1.2
mix=mix/max(1,np.max(np.abs(mix))/0.89)
print('LUFS final',round(meter.integrated_loudness(mix),2))
sf.write('/home/claude/ff4/out/mix.wav',mix,SR)
db=lambda x:20*np.log10(np.sqrt(np.mean(x**2))+1e-9)
print('voix',round(db(voice),1),'musique',round(db(mus_d),1),'fx',round(db(out),1))
