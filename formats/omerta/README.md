# Omertà — épisodes à voix (anglais)

Série à vote : chaque épisode finit sur un choix en 2 mots ; le choix le plus voté en commentaire devient l'épisode suivant.
**Ne jamais produire un épisode sans résultat de vote noté dans `state.json > votes`.**

## Installation
```bash
bash setup.sh --voices                 # pip + voix piper (ryan-high, norman-medium, joe-medium) + Whisper base.en
export OMERTA_WORK=/home/claude/omerta-work
W=$OMERTA_WORK                         # contient scripts/ (lien vers le dépôt), planches/, tts_piper/, asr_dl/
```

## Chaîne (modèle : épisode 2 anglais, 44 s)
1. **Texte** : `planches/ep2en_lines_n.json` (narrateur) et `planches/ep2en_lines_b.json` (parrain) comme modèles. Accroche en « you » dans les 2 s, rappel pour les nouveaux, « Follow » vers 50 %, choix final en 2 mots, « The most voted choice becomes episode N ».
2. **Voix** (meilleure prise vérifiée par Whisper) :
   ```bash
   python3 $W/scripts/best_take_wh.py lines_n.json $W/epN/voix/raw  $W/epN/voix/proc  en_US-ryan-high    0 1.08 0.667 0.8 0.74 0.93 4 ""
   python3 $W/scripts/best_take_wh.py lines_b.json $W/epN/voix/rawb $W/epN/voix/procb en_US-norman-medium 0 1.0  0.667 0.8 0.80 0.88 6 ""
   ```
   Garder les prises ≥ 0,9 de reconnaissance. Les répliques courtes du parrain passent mieux avec Whisper qu'avec le petit modèle.
3. **Timeline** : copier `scripts/build_tl_ep2en.py` (chemins, ORDER, GAP, CAPS = sous-titres par groupes de 1–3 mots, plans, événements). espeak soude parfois des petits mots (« of the », « in the ») : les souder aussi à l'écrit (`of‿the`), l'assert sur le nombre de mots le signale.
4. **Scène** : copier `planches/reel_ep2en.html` (SVG + `render(t)`), aperçu puis vidéo :
   ```bash
   LOCAL_ROOT=$W/planches python3 $W/scripts/reel_frames.py http://local/reel_epN.html preview $W/epN/prev/p 0.5 10 20
   LOCAL_ROOT=$W/planches python3 $W/scripts/reel_frames.py http://local/reel_epN.html video $W/epN/video_raw.mp4 DUREE
   ```
   (~1 image/s : 45 s de vidéo ≈ 20 min, à lancer en arrière-plan.)
5. **Son** : copier `scripts/reel_audio_ep2en.py` (voix, pulsation, bruitages calés sur les événements). Voix du parrain à -13 dB, sans saturation, sinon elle devient incompréhensible.
6. **Mixage** : volume -13,6 LUFS puis limiteur doux (au-dessus de 0,7, plafond 0,89, voir l'épisode 1), mux ffmpeg (AAC 192k), puis `asr_en.py` sur le mixage (≥ 0,9) et `tools/check_video.py`.
7. **Couverture** : `planches/cover_ep2en.html` + fond rendu par `scripts/cover_bg2.py`.

## Légendes (modèle épisode 2)
- Instagram : accroche + `OMERTÀ · Episode N — you voted: …` + question + `Comment X or Y 👇 The most voted choice becomes episode N+1.` + `Send this to someone who'd …` + `AI-generated fiction.` + 5 hashtags. 1er commentaire : le vote.
- TikTok : même texte sur une ligne, dans `text` ET `tiktokData.title`.
