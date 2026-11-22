import numpy as np, librosa, soundfile as sf
SR=48000; D=28.9; N=int(D*SR)
L=lambda p: librosa.load(p,sr=SR,mono=True)[0]
A='/home/claude/ep2/assets/'; B='/home/claude/ep3b/assets/'
v=L('/home/claude/fact1/audio/voice.mp3'); v=v/np.max(np.abs(v))*0.89
voice=np.zeros(N); voice[:min(N,len(v))]=v[:N]
# musique : boucle sans couture (la fin s'enchaîne sur le début)
m=L(A+'score.mp3'); X=int(1.5*SR)
mus=m[:N].copy(); fi=np.linspace(0,1,X)
mus[:X]=m[:X]*fi+m[N:N+X]*(1-fi)
mus=mus/np.sqrt(np.mean(mus**2))*0.042      # ~ -26 dBFS RMS
# ducking sous la voix
env=np.abs(voice); k=int(0.25*SR); env=np.convolve(env,np.ones(k)/k,'same'); env=np.clip(env/0.08,0,1)
duck=1-0.45*env
# bruitages (banque ElevenLabs locale), un à la fois, fondus
def fx(p,t,g,dur=1.2,off=0.0):
    x=L(p); x=x[int(off*SR):int((off+dur)*SR)]; x=x/(np.max(np.abs(x))+1e-9)
    f=int(0.05*SR); x[-f:]*=np.linspace(1,0,f); x[:int(0.005*SR)]*=np.linspace(0,1,int(0.005*SR))
    i=int(t*SR); e=min(N,i+len(x)); out[i:e]+=g*x[:e-i]
out=np.zeros(N)
def synth_pop(t,g,f0=900):
    n=int(0.09*SR); tt=np.arange(n)/SR; x=np.sin(2*np.pi*(f0+800*np.exp(-tt*40))*tt)*np.exp(-tt*45)
    i=int(t*SR); out[i:i+n]+=g*x
def synth_tick(t,g):
    n=int(0.03*SR); x=np.random.RandomState(int(t*100)).randn(n)*np.exp(-np.arange(n)/SR*250)
    x=np.convolve(x,[1,-0.95],'same'); i=int(t*SR); out[i:i+n]+=g*x/np.max(np.abs(x))
fx(B+'impact.mp3',2.02,0.30,1.0)          # cœur qui se fend
fx(B+'slash.mp3',3.80,0.22,0.8)           # croix sur la tromperie
fx(A+'boom.mp3',4.84,0.38,1.6)            # LE MÉPRIS
for i in range(0,40,3): synth_pop(6.69+i*0.07,0.05,700+i*15)   # couples qui apparaissent
for k in range(10): synth_tick(8.6+k*0.13,0.06)                 # compteur 40 ans
fx(B+'wind.mp3',11.15,0.16,1.0)           # zoom sur le visage
synth_pop(13.4,0.12,500)                  # yeux au ciel
synth_pop(14.86,0.10); synth_pop(16.07,0.10)                    # bulles
fx(A+'boom.mp3',19.88,0.22,1.0)           # message caché
synth_pop(21.47,0.09,1200)
fx(A+'spell-ok.mp3',22.5,0.26,1.6)        # merci : le cœur se ressoude
synth_pop(26.6,0.10,500)                  # yeux au ciel (fin)
mix=voice+mus*duck+out
mix=np.tanh(mix*1.1)/np.tanh(1.1)*0.9
sf.write('/home/claude/fact1/out/mix_pre.wav',mix,SR)
print('ok', 20*np.log10(np.sqrt(np.mean(voice**2))), 20*np.log10(np.sqrt(np.mean((mus*duck)**2))), 20*np.log10(np.sqrt(np.mean(out**2))+1e-9))
