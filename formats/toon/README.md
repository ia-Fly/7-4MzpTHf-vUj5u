# Format TOON — série FROMAGISTAN (depuis le 11/11/2026)

Consigne de Matis (11/11/2026) : BLACK-OUT est abandonné. Une seule série : **FROMAGISTAN**, un jeu en dessin où le public gouverne. Un épisode tous les 2 jours, 19:00 (Paris), Instagram + TikTok, en français. **Ce fichier remplace les sections 0 (série, voix, format), 4 et 5 du RUNBOOK** ; le reste du RUNBOOK (installation, doublons, stats, contrôle, publication, mémoire, rapport) s'applique tel quel.
Bible complète (pitch, règles du jeu, pays voisins) : doc du projet `claude/bible-fromagistan.md`, résumée ici.

## La série
- **Pitch** : un vieux mage, le Président Barbichu, est devenu président du Fromagistan par erreur. Pays en ruine, magie qui rate. Il raconte à la 1re personne.
- **Personnages** (dessinés en code, `rig.py`) : Barbichu, le pigeon conseiller (blasé), le rival au monocle, la reporter de « Fromagistan Info », les citoyens. Tous inventés. **Jamais de caricature ressemblante ni de nom déformé d'une personne réelle** ; pas de personnage protégé.
- **Style** : aplats de couleur, sans contour, grosses têtes rondes, personnages animés (marche, salut, parole, clignement), cartes et compteurs façon jeu mobile.
- **Règles du jeu, affichées avec les VRAIS chiffres de l'épisode précédent** (lus dans les stats, Instagram + TikTok additionnés) : 1 abonné = 1 citoyen · 1 like = +2 écus · 1 partage = +3 popularité · 1 enregistrement = +1 magie · commentaire = 1 voix (1, 2 ou 3) · commentaire le plus liké = « loi citoyenne » de l'épisode suivant. Ne jamais inventer un chiffre ni un résultat.
- **Jauges** tenues dans `state.json > fromagistan` : citoyens, budget (écus), popularité (0 = destitution), magie, relation avec chaque pays voisin (0 à 100), lieux ouverts dans la ville.
- **Pays voisins** (inventés, thème nourriture) : Royaume de Beurrélie (la Reine), Empire du Ketchup (l'Empereur), Principauté du Tofu (le Prince), Duché de la Raclette (la Duchesse). Accord commercial = écus à chaque épisode ; relation sous 20 = crise.
- **La ville** : chaque chantier voté ouvre un lieu qui rapporte ou coûte à chaque épisode (marché aux fromages, fête de la raclette, école de magie…).
- **Fromagistan Info** : jusqu'à 4 infos RÉELLES par épisode, trouvées par WebSearch le jour même (insolite, politique drôle, science, médias), transposées au Fromagistan avec les personnages inventés. Rien de dramatique, aucune victime, aucune personne réelle reconnaissable. Pas d'info solide = moins d'infos, jamais d'invention présentée comme réelle. Citer les sources dans le journal.

## Votes et commentaires
- Résultat du vote et commentaire le plus liké : `state.json > votes.fromagistan_ep<N>`. Sources : la capture d'écran envoyée par Matis, et **TikTok** par `vidiq_tiktok_video_comments` (5 crédits la page, autorisé pour cet usage : texte, likes). Instagram : pas d'outil de lecture pour l'instant.
- Sans résultat : montrer les trois options « en attente » et faire avancer l'histoire par un événement (visite d'un voisin, info du jour), sans rien prétendre sur le vote.
- Loi citoyenne : seulement si elle est drôle, sans attaque contre une personne ou un groupe, sans rien de dangereux ; sinon prendre le commentaire suivant.

## Squelette d'un épisode (50 à 70 s)
1. Résultat du vote + loi citoyenne (dès la 1re seconde). 2. Rappel du pitch en une phrase. 3. Compteurs réels. 4. Le chantier : 3 ratés drôles puis réussite. 5. Fromagistan Info. 6. La facture. 7. Trois choix chiffrés. 8. Un mystère + « abonne-toi pour devenir citoyen ».

## Fabriquer un épisode (environ 1 400 crédits : voix ≈ 920, le reste en banque)
1. Copier `ep1.py` en `ep<N>.py` : `LINES` (répliques), `SFX` (bruitage, réplique, décalage, dB, durée), `frame()` (une branche par scène, placée sur le début des répliques `T['L3']`).
2. Voix : flow ElevenLabs de la série `lVEnH7dvj0Qcr2g2eiaE`, `creative_generate_speech`, `eleven_v4`, voix **Hugo – Punchy French Creator `3Tp5mYhT9wrfnry9pzvV`**, `generations_count` 1, une seule prise. Puis un nœud `speech-to-text` (`eleven_scribe_v1`, gratuit) branché dessus → `words.json`.
3. Dans un dossier d'assets : `voice.mp3`, `words.json`, `theme.mp3` (musique de la série, génération `YGZxsgSlEjvIiAq1ieZe`) et les bruitages (`formats/cine/sound_library.json`, `creative_get_generations` redonne les liens gratuitement).
4. `python3 formats/toon/ep<N>.py ASSETS OUT --preview 1,10,20,…` puis regarder `preview.jpg` : les sous-titres ne doivent jamais couvrir un visage (`cy` par scène), les cartes ne doivent pas se chevaucher.
5. `python3 formats/toon/ep<N>.py ASSETS OUT` (environ 6 min, en arrière-plan) → `video.mp4`, `cover.jpg`. Contrôle : RUNBOOK §6.
6. Légende : accroche, `FROMAGISTAN · Épisode N`, les 3 choix, `Vote en commentaire. Le commentaire le plus liké devient une loi.`, `Fiction générée par IA.`, 5 hashtags au plus (`#jeu #histoire #humour #pourtoi #france`). 1er commentaire Instagram : les 3 choix.
7. Après publication : mettre à jour `state.json > fromagistan` (jauges, épisode, vote ouvert), `history`, le journal, et noter ici ce qui a changé dans le monde.

## État du monde
| Épisode | Publié | Ce qui s'est passé | Vote ouvert |
|---|---|---|---|
| 1 | 13/11/2026 | Barbichu devient président par erreur ; 0 citoyen, 0 écu, palais sans toit ; lumière rallumée à la bougie ; une porte fermée à clé dans la cave | 1 réparer le toit (400 écus) · 2 marché aux fromages (150) · 3 inviter la reine (0) |
