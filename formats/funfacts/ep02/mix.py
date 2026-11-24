import numpy as np, librosa, soundfile as sf
SR=48000; D=28.0; N=int(D*SR)
L=lambda p: librosa.load(p,sr=SR,mono=True)[0]
A='/home/claude/fact2/audio/'
v=L(A+'voice.mp3'); v=v/np.max(np.abs(v))*0.89
# silences ajoutés aux pauses détectées (coupe au milieu du silence) : (instant de coupe dans la voix brute, durée ajoutée)
CUTS=[(1.81,0.2),(3.55,0.5),(8.98,0.5),(13.74,0.4),(16.93,0.6),(21.52,0.5)]
parts=[];prev=0
for c,g in CUTS:
    i=int(c*SR); parts+= [v[prev:i], np.zeros(int(g*SR))]; prev=i
parts.append(v[prev:]); vv=np.concatenate(parts)
voice=np.zeros(N); voice[:min(N,len(vv))]=vv[:N]
sf.write(A+'voice_stretched.wav',voice,SR)
from scipy.signal import butter, sosfiltfilt
pres=sosfiltfilt(butter(2,[2000,5000],btype='band',fs=SR,output='sos'),voice)
voice=voice+0.4*pres
voice=voice-sosfiltfilt(butter(2,120,btype='low',fs=SR,output='sos'),voice)*0.7
# musique : boucle sans couture (la fin s'enchaîne sur le début)
m=L(A+'music.mp3'); X=int(1.5*SR)
mus=m[:N].copy(); fi=np.linspace(0,1,X)
mus[:X]=m[:X]*fi+m[N:N+X]*(1-fi)
mus=mus/np.sqrt(np.mean(mus**2))*0.0316     # ~ -30 dBFS RMS
# creuse les médiums de la musique (zone de la voix) pour la lisibilité
from scipy.signal import butter, sosfiltfilt
mid=sosfiltfilt(butter(2,[350,3500],btype='band',fs=SR,output='sos'),mus)
env=np.abs(voice); k=int(0.25*SR); env=np.convolve(env,np.ones(k)/k,'same'); env=np.clip(env/0.08,0,1)
duck=1-0.75*env
out=np.zeros(N)
def fx(p,t,g,dur=1.2,off=0.0):
    x=L(p); x=x[int(off*SR):int((off+dur)*SR)]; x=x/(np.max(np.abs(x))+1e-9)
    f=int(0.08*SR); x[-f:]*=np.linspace(1,0,f); x[:int(0.005*SR)]*=np.linspace(0,1,int(0.005*SR))
    i=int(t*SR); e=min(N,i+len(x)); out[i:e]+=g*x[:e-i]
def synth_pop(t,g,f0=900):
    n=int(0.09*SR); tt=np.arange(n)/SR; x=np.sin(2*np.pi*(f0+800*np.exp(-tt*40))*tt)*np.exp(-tt*45)
    i=int(t*SR); out[i:i+n]+=g*x
def synth_tick(t,g):
    n=int(0.03*SR); x=np.random.RandomState(int(t*100)).randn(n)*np.exp(-np.arange(n)/SR*250)
    x=np.convolve(x,[1,-0.95],'same'); i=int(t*SR); out[i:i+n]+=g*x/np.max(np.abs(x))
fx(A+'impact.mp3',1.75,0.20,0.6)            # virus qui arrivent
for k in range(12): synth_tick(4.85+k*0.17,0.05)   # compteur 164
synth_pop(7.72,0.10,500)                    # carte compte-gouttes
for k in range(3): synth_pop(8.1+k*0.6,0.05,1300)  # gouttes
fx(A+'impact.mp3',11.45,0.22,0.45)           # ×4,2
for k,tt in enumerate([16.35,17.05,17.55]): synth_pop(tt,0.08,700+150*k)
synth_pop(19.36,0.10,1100)                  # l'antidote
synth_tick(21.52,0.12)                      # écran coupé (clic)
fx(A+'shield.mp3',21.62,0.13,1.4)           # bouclier
synth_pop(22.42,0.09,900)                   # 23:00
synth_pop(25.62,0.035,600)                   # épisode suivant
mus_d=(mus-mid*0.6*env)*duck
mix=voice+mus_d+out
mix=mix/np.max(np.abs(mix))*0.9
sf.write('/home/claude/fact2/out/mix_pre.wav',mix,SR)
db=lambda x:20*np.log10(np.sqrt(np.mean(x**2))+1e-9)
print('voix',db(voice),'musique',db(mus*duck),'fx',db(out))
