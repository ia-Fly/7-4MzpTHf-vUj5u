import numpy as np, librosa, soundfile as sf
from scipy.signal import butter, sosfiltfilt
SR=48000; D=28.0; N=int(D*SR)
L=lambda p: librosa.load(p,sr=SR,mono=True)[0]
A='/home/claude/ff3b/audio/'; B='/home/claude/ep2/assets/'; C='/home/claude/ep3b/assets/'
v=L(A+'voice.mp3'); v=v/np.max(np.abs(v))*0.89
voice=np.zeros(N); voice[:min(N,len(v))]=v[:N]
pres=sosfiltfilt(butter(2,[2000,5000],btype='band',fs=SR,output='sos'),voice)
voice=voice+0.4*pres
voice=voice-sosfiltfilt(butter(2,120,btype='low',fs=SR,output='sos'),voice)*0.7
m=L(A+'music.mp3'); X=int(1.5*SR)
mus=m[:N].copy(); fi=np.linspace(0,1,X)
mus[:X]=m[:X]*fi+m[N:N+X]*(1-fi)
mus=mus/np.sqrt(np.mean(mus**2))*0.0316
mid=sosfiltfilt(butter(2,[350,3500],btype='band',fs=SR,output='sos'),mus)
env=np.abs(voice); k=int(0.25*SR); env=np.convolve(env,np.ones(k)/k,'same'); env=np.clip(env/0.08,0,1)
duck=1-0.75*env
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
fx(C+'slash.mp3',0.15,0.10,0.6)                    # billets qui sortent
fx(B+'coins.mp3',0.55,0.08,0.6)
fx(B+'boom.mp3',2.4,0.14,0.9)                     # DÉJÀ DÉPENSÉ
beep(5.0,0.05,1500); synth_tick(6.4,0.06)         # notif retrait / barré
synth_pop(8.17,0.09,1100)                         # résultat
for k in range(10): synth_pop(9.3+k*0.08,0.035,700+k*40)   # silhouettes
for k in range(6): synth_tick(10.8+k*0.12,0.06)   # ? rouges
synth_pop(13.03,0.08,700)                         # carte étude
for k in range(6): synth_tick(15.6+k*0.15,0.05)   # barre 63
for k in range(4): synth_tick(20.9+k*0.15,0.04)   # barre 26
synth_pop(22.35,0.09,1200)                        # l'astuce
fx(B+'spell-ok.mp3',23.3,0.15,1.4)                # ticket
fx(C+'slash.mp3',24.8,0.07,0.6)                   # relance : billets
mus_d=(mus-mid*0.6*env)*duck
mix=voice+mus_d+out
import pyloudnorm as pyln
meter=pyln.Meter(SR); lu=meter.integrated_loudness(mix)
mix=mix*10**((-12.9-lu)/20)
mix=np.tanh(mix*1.2)/1.2
mix=mix/max(1,np.max(np.abs(mix))/0.89)
print('LUFS final',round(meter.integrated_loudness(mix),2))
sf.write('/home/claude/ff3b/out/mix.wav',mix,SR)
db=lambda x:20*np.log10(np.sqrt(np.mean(x**2))+1e-9)
print('voix',round(db(voice),1),'musique',round(db(mus_d),1),'fx',round(db(out),1))
