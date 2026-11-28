import numpy as np, librosa, soundfile as sf
from scipy.signal import butter, sosfiltfilt
SR=48000; D=28.5; N=int(D*SR)
L=lambda p: librosa.load(p,sr=SR,mono=True)[0]
A='/home/claude/ff5/audio/'
v=L(A+'voice.mp3'); v=v/np.max(np.abs(v))*0.89
# silences ajoutés aux pauses détectées (coupe au milieu du silence) : (instant dans la voix brute, durée ajoutée)
CUTS=[(2.95,0.3),(8.55,0.3),(11.41,0.3),(15.52,0.3),(21.91,0.3),(23.57,0.3)]
parts=[];prev=0
for c,g in CUTS:
    i=int(c*SR); parts+=[v[prev:i],np.zeros(int(g*SR))]; prev=i
parts.append(v[prev:]); vv=np.concatenate(parts)
voice=np.zeros(N); voice[:min(N,len(vv))]=vv[:N]
pres=sosfiltfilt(butter(2,[2000,5000],btype='band',fs=SR,output='sos'),voice)
voice=voice+0.4*pres
voice=voice-sosfiltfilt(butter(2,120,btype='low',fs=SR,output='sos'),voice)*0.7
# musique réutilisée (flow raa3nwek3AfIh8xt8w9h) : boucle sans couture
m=L(A+'music.mp3'); X=int(1.5*SR)
if len(m)<N+X: m=np.concatenate([m,m])
mus=m[:N].copy(); fi=np.linspace(0,1,X)
mus[:X]=m[:X]*fi+m[N:N+X]*(1-fi)
mus=mus/np.sqrt(np.mean(mus**2))*0.0316
mid=sosfiltfilt(butter(2,[350,3500],btype='band',fs=SR,output='sos'),mus)
env=np.abs(voice); k=int(0.25*SR); env=np.convolve(env,np.ones(k)/k,'same'); env=np.clip(env/0.08,0,1)
duck=1-0.8*env
out=np.zeros(N)
def put(t,x,g):
    i=int(t*SR); e=min(N,i+len(x)); out[i:e]+=g*x[:e-i]
def synth_pop(t,g,f0=900):
    n=int(0.09*SR); tt=np.arange(n)/SR; put(t,np.sin(2*np.pi*(f0+800*np.exp(-tt*40))*tt)*np.exp(-tt*45),g)
def synth_tick(t,g):
    n=int(0.03*SR); x=np.random.RandomState(int(t*100)).randn(n)*np.exp(-np.arange(n)/SR*250)
    x=np.convolve(x,[1,-0.95],'same'); put(t,x/np.max(np.abs(x)),g)
def thump(t,g,f=70):
    n=int(0.35*SR); tt=np.arange(n)/SR; x=np.sin(2*np.pi*(f+60*np.exp(-tt*30))*tt)*np.exp(-tt*12)
    nz=np.random.RandomState(7).randn(n)*np.exp(-tt*60)*0.3; put(t,x+nz,g)
def noise_band(t,d,g,lo,hi,seed=1,mod=0):
    n=int(d*SR); tt=np.arange(n)/SR; x=np.random.RandomState(seed).randn(n)
    x=sosfiltfilt(butter(2,[lo,hi],btype='band',fs=SR,output='sos'),x); x/=np.max(np.abs(x))
    envv=np.minimum(1,np.minimum(tt/0.15,(d-tt)/0.3))
    if mod: envv*=0.6+0.4*np.abs(np.sin(2*np.pi*mod*tt))
    put(t,x*envv,g)
def chime(t,g):
    for j,f in enumerate([1320,1760,2640]):
        n=int(0.6*SR); tt=np.arange(n)/SR; put(t+j*0.07,np.sin(2*np.pi*f*tt)*np.exp(-tt*7),g)
def blop(t,g):
    n=int(0.12*SR); tt=np.arange(n)/SR; put(t,np.sin(2*np.pi*(300+500*tt/0.12)*tt)*np.exp(-tt*25),g)
synth_pop(3.30,0.07,800)            # carte NHS
thump(4.30,0.12)                    # tampon OFFICIEL
noise_band(6.15,2.6,0.035,500,3000,3)   # l'eau qui coule
synth_pop(12.30,0.06,900)           # bain de bouche
thump(13.98,0.13,90)                # croix PAREIL
synth_pop(14.69,0.08,1000)          # carte horloge
for j in range(4): synth_tick(14.9+j*0.2,0.05)
synth_pop(16.85,0.08,1200)          # le bon geste
noise_band(18.5,1.6,0.03,2500,7000,5,mod=5.5)  # brossage
chime(19.80,0.05)                   # fluor revenu
blop(20.76,0.10)                    # on crache
thump(22.19,0.10,110)               # verre barré
synth_pop(23.50,0.07,800)           # carte abonnement
synth_tick(24.40,0.10); synth_pop(24.48,0.09,1400)   # clic + passage à ABONNÉ
mus_d=(mus-mid*0.6*env)*duck
mix=voice+mus_d+out
import pyloudnorm as pyln
meter=pyln.Meter(SR); lu=meter.integrated_loudness(mix)
mix=mix*10**((-12.6-lu)/20)
mix=np.tanh(mix*1.2)/1.2
mix=mix/max(1,np.max(np.abs(mix))/0.89)
print('LUFS final',round(meter.integrated_loudness(mix),2))
sf.write('/home/claude/ff5/out/mix.wav',mix,SR)
sf.write('/home/claude/ff5/out/voice_only.wav',voice/np.max(np.abs(voice))*0.89,SR)
db=lambda x:20*np.log10(np.sqrt(np.mean(x**2))+1e-9)
print('voix',round(db(voice),1),'musique',round(db(mus_d),1),'avant ducking',round(db(mus),1),'fx',round(db(out),1))
