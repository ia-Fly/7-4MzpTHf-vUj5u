# Format FUN FACTS (depuis le 22/11/2026) — format principal, 1 vidéo tous les 2 jours à 19:00 Paris

Demande de Matis : vidéos style graphique « Omertà » (fond sombre quadrillé, pictos line-art blancs, HUD mono en haut,
gros sous-titres Barlow Condensed avec mot-clé rouge #FF4B2B, menthe #5EF5B4 pour le positif), sur des fun facts qui
apprennent quelque chose : couples, vie de tous les jours, choses importantes à savoir. Sujet cherché sur le web, source fiable.
~30 s, **la vidéo boucle** (dernière phrase qui s'enchaîne sur la première, dernière image = première image).
ElevenLabs pour voix, musique de fond, bruitages. **La voix doit dominer et être parfaitement compréhensible.**
FROMAGISTAN reste un bonus occasionnel.

## Choix figés
- Voix : **Lucas Doré — Casual Narrator** `ULDw9NhSQODAHXxn70tR`, modèle `eleven_v4`, 1 prise. (Matis l'a choisie le 22/11.)
- Compte ElevenLabs du connecteur = **gratuit** (10 000 caractères/mois). Script ≤ 480 caractères. Si « Free generations are busy » :
  ne pas relancer en boucle ; musique de repli = `ep01/score` (dans la banque : score.mp3, drone sombre) — à stocker dans assets.
- Rendu : `planches/style.css` + fonts de `assets/fonts` (Anton, Barlow Condensed, JetBrains Mono, Inter) ; `rf2.py URL video out.mp4 DUR t0 n_fin`
  (2 processus en parallèle, ~5 min pour 29 s). `LOCAL_ROOT=<dossier planches>`.
- Mixage : voix normalisée, musique ~ -30 dBFS RMS + ducking 45 % sous la voix, bruitages courts un à la fois, loudnorm -14 LUFS.
- Vérif : `tools/check_video.py` puis `tools/asr_check.py <mp4> "<texte>" --lang fr` → score ≥ 0,85.
- Publication : `tools/media.py add` → Metricool (brand 7631727) Instagram REEL isAiGenerated + TikTok isAigc, couverture = image à 0,5 s,
  1er commentaire = la source. Puis `media.py rm`.

## Structure qui marche (ép. 01)
Accroche choc 0-3 s (« Le signe n°1… ce n'est pas X ») → révélation (carte rouge) → preuve/chiffre (carte étude) → exemples concrets animés
(gros plan) → message caché → antidote (menthe) → relance qui reboucle (« Alors la prochaine fois… souviens-toi : »).
Jauge HUD (« RISQUE… ») qui revient à l'état du début avant la fin.

## Épisodes
| N° | Date | Sujet | Source |
|---|---|---|---|
| 01 | 22/11/2026 | Le mépris, 1er prédicteur de rupture (Gottman) | gottman.com/blog/the-four-horsemen-contempt |
| 02 | 24/11/2026 | Moins de 6 h de sommeil = 4,2× plus de risques d'attraper un rhume (Prather, Sleep 2015) | cmu.edu/news/stories/archives/2015/august/sleep-and-sickness.html |
| 03 | 25/11/2026 | Liquide déjà retiré = compté comme déjà dépensé ; 6/10 ne savent pas où est passé leur retrait (Barclays) ; effet de dénomination 63 % vs 26 % (Raghubir & Srivastava 2009) | atmmarketplace.com (Barclays ATMnesia) ; doi 10.1086/599222 |
| 04 | 26/11/2026 | Effet du témoin : seul, 85 % donnent l'alerte avant la fin de la crise ; avec 4 autres témoins, 31 % ; antidote = désigner quelqu'un (Darley & Latané 1968) | doi.org/10.1037/h0025589 |
