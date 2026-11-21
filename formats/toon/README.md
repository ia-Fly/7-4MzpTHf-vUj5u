# Format TOON — série FROMAGISTAN (depuis le 11/11/2026)

Consigne de Matis (11/11/2026) : BLACK-OUT est abandonné. Une seule série : **FROMAGISTAN**, un jeu en dessin où le public gouverne. Un épisode tous les 2 jours, 19:00 (Paris), Instagram + TikTok, en français. **Ce fichier remplace les sections 0 (série, voix, format), 4 et 5 du RUNBOOK** ; le reste du RUNBOOK (installation, doublons, stats, contrôle, publication, mémoire, rapport) s'applique tel quel.
Bible complète (pitch, règles du jeu, pays voisins) : doc du projet `claude/bible-fromagistan.md`, résumée ici.

## ⚠️ RÈGLES ANTI-DÉCROCHAGE (Matis, 19/11/2026, PERMANENTES — priment sur « DURÉE », « Bilan d'abord » et le squelette plus bas)
Diagnostic complet : doc projet `claude/fromagistan-bilan-stats-2026-11-19.md`. Modèle de montage : `ep4/ep4.py` (+ `cover.py`).
- **Durée 35 à 50 s**, 100 à 130 mots, 6 à 9 répliques, 2 ou 3 personnages qui parlent.
- **0-2 s** : un plan qui BOUGE + une phrase compréhensible sans avoir vu la série. Interdit dans les 3 premières secondes : « Épisode N », chiffres, résultat de vote brut, @pseudos, cartes ou bandeaux, image fixe, écran noir. **Avant 5 s** : une phrase de contexte (« Ici, c'est toi qui gouvernes un pays de fromage. »).
- **Rythme** : un changement de plan toutes les 2 à 3 s ; au moins 2 plans Veo (le 1er dès 0 s) ; jamais plus de 3 s sur la même image fixe, mouvement de caméra rapide ; un bruitage court à chaque changement de plan, un seul à la fois.
- **Design épuré** : en plus des sous-titres, UN SEUL élément d'interface à la fois (carte, compteur ou bulle) ; gros plans ; sous-titres gros en bas-centre ; bulles de noms après 3 s, une à la fois ; aucun texte sur un visage.
- **Bilan à la FIN** (3-4 s, juste avant l'abonne-toi), une phrase, 2 chiffres au plus ; le détail va dans la légende.
- **Un seul appel à l'action** (le choix à commenter) ; « Abonne-toi pour devenir citoyen » dans les 2 dernières secondes seulement ; pas de « like + republie ».
- **Légende** : 1re ligne = l'accroche ; 2e ligne `FROMAGISTAN · ép. N` ; couverture = le plan le plus spectaculaire + 3 à 5 mots.
- Voix : Doudou Dictador = Gronk `Pu9MMuPx0BqjFaVxHf8W` (l'ancien `30ndZrqtoeQllE13MnID` est désactivé). Images 3 à 5 neuves (Seedream 5 Lite, style manga d'action du spécial). 2 plans Veo. Budget ≈ 3 500 crédits par épisode.
- **Mesure à chaque passage** dans `STRATEGY.md` : dernier Reel contre les objectifs (skip < 40 %, regardé > 30 %, vues IG > 1 000), cause probable, correction.
- **Si le compte ElevenLabs connecté n'est pas celui de Matis** (21/11 : compte gratuit vide → planches inaccessibles, pas de Veo, 3 images/jour, voix de bibliothèque « creator » refusées) : extraire des images de référence des anciens Reels (branche `media`, historique git : `git show <commit>:<fichier>.mp4`), les téléverser (`creative_create_asset_upload`), remplacer Veo par du mouvement en code (`swirl`, `melt`, `shake_fr`, `speed_lines` de `ep4.py`), et prévenir Matis tout de suite.

## ⚠️ NOUVEAU FORMAT ET NOUVELLE DA (Matis, 14/11/2026 — fait foi, remplace « Style », « Effets », « Caméra », « Squelette » et « Fabriquer » plus bas)
Tant que Matis n'a pas dit non, chaque épisode reprend ce format. Modèle de montage : `formats/toon/ep3/ep3.py` (+ `cover.py`) pour le format 1 min ; `ep2/ep2.py` pour mémoire.

### Format
- Images et plans générés avec **ElevenLabs** (flow `lVEnH7dvj0Qcr2g2eiaE`) ; en code seulement l'interface (jauges, bandeaux, compteurs, sous-titres, bulles de noms, nom de qui parle), le montage, et le dessin en dernier recours.
- **Images** : `bytedance-seedream-5-lite` (≈ 212 crédits), planches de référence branchées en `connect_from` (`creative_add_flow_asset_node`), 1 image par plan, nœud créé avec `model_parameters {"aspect_ratio":"9:16","resolution":"2K"}` puis `creative_run_flow_nodes` (generations_count 1). Jamais `gemini-3-pro-image`.
- **Vidéo** : plans clés animés image → vidéo, `veo-3.1-lite-generate-001`, `{"duration_secs":4,"aspect_ratio":"9:16","resolution":"720p","generate_audio":false}` ≈ 727 crédits ; regarder chaque plan (`tools/clip_sheet.py`) et couper les passages ratés. Les autres plans = images avec mouvement de caméra. Images vidéo gardées en uint8 dans le monteur (7 Go de RAM).
- **Musique** : node music ElevenLabs, une piste par ambiance, réutilisée (thème `YGZxsgSlEjvIiAq1ieZe`, tension `sqty9Uj1GzKtv1Ss1BG7` flow `cuSYy0Hs63XrJf0fCN6Q`, Guimauvie `MRV9sFyVk7z7nJGtbsaP` + `KEwAgJYynEbtXREeBkDA`). **Bruitages** : banque `formats/cine/sound_library.json` d'abord, sinon node sfx `eleven_text_to_sound_v2`.
- **Une voix par personne** (`eleven_v4`, une prise) ; chaque personne de l'histoire dit au moins une petite phrase ; le nom de qui parle s'affiche au-dessus des sous-titres.
- **DURÉE (Matis, 17/11/2026, remplace « 2 à 3 min »)** : environ 1 min (50 à 75 s), 150 à 180 mots, 8 à 12 répliques, 2 à 4 personnages qui parlent, une intrigue principale. Structure : 0-3 s accroche (résultat du vote) → 3-12 s bilan éclair (vrais chiffres, compteurs) → 12-45 s action + un indice → 45-55 s 3 choix chiffrés → 55-60 s question + « abonne-toi ». Présentations : une phrase maximum. Voix à vitesse normale, respirations 0,3 à 0,6 s. Modèle : `ep3/ep3.py` (une prise de voix par réplique, fichiers v1…v9 ; plus besoin de Scribe).
- **Intrigues** : au moins 2 fils mystérieux ouverts, un nouvel indice par épisode, fin sur une question.
- **Budget** : ≈ 6 500 crédits par épisode (121 000 par mois pour ~15 épisodes). Estimer avant de générer ; réduire d'abord les plans animés, puis les images. Chaque dépense dans `elevenlabs/ledger.jsonl`.
- Pas de rubrique fixe « demandes des commentaires ».
- **Bilan d'abord (Matis, 15/11/2026, permanent)** : après l'intro, bilan rapide de l'épisode précédent avec les vrais chiffres (likes → écus, commentaires, partages → popularité, enregistrements → magie, abonnés → citoyens), compteurs animés, puis action directe. Présentations de personnages en une phrase.
- **Bruitages (Matis, 15/11/2026)** : jamais deux en même temps, jamais sur une réplique (logique du monteur ep2).

### Bulle de nom (Reels)
Chaque personnage joué par une vraie personne a, dès sa première apparition, une petite boule lumineuse (≈ 40 px, cœur blanc-or, halo, 4 étincelles en orbite, « pop » à l'apparition, flotte de 4 à 6 px) au-dessus de la tête, avec « @pseudo » (Montserrat ExtraBold 34 px, blanc contour or) sur une pastille noire translucide aux bords dorés. OR pour les gentils, ROUGE (#FF2A2A, pastille bordeaux) pour Guimauvie. Hors des 10 % du haut, des 25 % du bas et de la colonne de boutons. Code : fonction `bubble` de `ep2/ep2.py`. Citoyens anonymes et personnages inventés : pas de bulle.

### DA (permanente)
Dessin 2D, grosses têtes rondes, rendu des planches : halo et rim light autour des personnages, contrastes forts, vignettage, particules / étincelles, éclairage dramatique. **Ce n'est pas « la nuit »** : jour, nuit, aube, crépuscule selon l'histoire ; de jour, ciel lumineux mais contrasté (soleil doré, ombres franches, halos gardés).
- Gentils (Fromagistan) : violet royal `#4B1E8C` `#7A3FD1`, or et jaune fromage `#FFC400` `#FFE066` (halos, magie, titres) ; de nuit fonds `#0B0B0D` `#141826`. Lunettes de Barbichu qui brillent en or.
- Méchants (Guimauvie, Doudou Dictador) : `#0B0B0D` `#1A1A1F` `#B3001B` `#6E0A14` `#FF2A2A`, de jour comme de nuit. Or = gentils, rouge = méchants. Dark mais jamais effrayant, rien de gore, pas de sang.
- Rival au monocle : lueur gris-vert. Reine de Beurrélie : lueur ivoire-dorée.
- Interface : panneaux noirs translucides, bords et chiffres or (rouge pour Guimauvie).

### Planches de référence (flow `lVEnH7dvj0Qcr2g2eiaE`, relire avec `creative_get_generations`, 0 crédit)
| Quoi | Principale | Variantes |
|---|---|---|
| Président Barbichu (réf. DA) | `hXaP3xaDm6TBqjv9Kbsi` | `zssQvD5WGR3ZIEJFPyap`, `9IygikbYFKVS3r4PRFPJ` |
| Pigeon, rival, reporter, citoyen type | `4qaAGKnBlqcwXiQaSSJF` | `MJKvknvcVDZjoVD3biCQ`, `TJnBfyfxfEhItVIAGXpm`, `p0luVGCQEZIwwMOQf0OA` |
| Reine de Beurrélie | `DKVHfZuF1G2e7cGXHuWb` | `DTQiOiNXrn1h2NtsTk28`, `Tg0oVBYBokOvp8aKOGUI`, `5XAiFJyrwXO2w5jbAiL9` |
| Kxpl (@justnaxt) | `eqST47ay8kJRx1qRgI8L` | `vVP4Uwy8TJ0AbIsJ9pAi` |
| Comptable Esteban (@esteban_gi19) | `17DnL0zA4WwHGXlswFZW` | `p2BZKfQHHUNhG8rs6R1d`, `5qHc2heohbBgJtMLZj9r` |
| Docteur (@nat_gbz) | `1hxEKYtBS4pDbDSI2shj` | `Yg87Kn6O0iT93SjnXq7c` |
| Garde royale | `oC1Cka8Yin97YQB0piAM` | `a87EugwoanbqdDWtyHxr` |
| Capitaine de la Garde montée (@elo_zht, visière fermée, 3 étoiles) | `iHPA1wHMXMKNZhqr4rN2` | `DMJGViDbyjCwtYDreJt9` ; vertical ép. 2 `DcGhjL9qzEaRVOuhZbud` |
| Doudou Dictador | `WhsnClrHnKVRGyH60KyA` | `cYeB0myTNtI57ltDwytr`, `zG7WB2OZw28ISpphmXVc`, `Zygc04VNFeYcKlyWoJ26` |
| Château de Guimauvie | `imMXroDhPyxJIi3ZKEX5` | `sxIVea96ju0Q1RgZHdS8` ; scène verticale ép. 2 `F7m1l6TZ7cv1s9H7HzUx` |
| Sbires-oursons + chèvre noire (sans brassards rouges) | `FQeMnCPGnc6tWat2ubiP` | chèvre `vDSJ2bPfvZWAQOXWzEXF` ; espion sous le carrosse `R3OeCqZn2I6unAm9ojZD` |
| Place du Fromagistan (nuit) | `0dYDZKjnzlFO8bnmb61K` | `5rCtfiG1GScmu5glxadu`, `lQFdEFF8pxI47wWLOgmi`, `yDcA8yoFQPaZXRwCFIGR` |
| Marché aux fromages (jour) | `xsbcbdgfQpEIV2zCjNa7` | `FELlr7L6pKLKJV7LucEn` |
| Bureau présidentiel | `0IueMHSZGLdxXpbbcpZ5` | `8g80jdjLEpYB5hVpJ4OT` |
| Circuit du Grand Prix | `RJQLTXBcoGEnCbYivqr3` | `El5PSY8aFkgc4AX56lWs` |
| Porte de la cave | `1by4TRMxqJh8SW4B0npt` | |
| Réserve royale de fromages | `nrNWFIRWo9mTWPny4UNh` | |

### Rôles et voix (tenus aussi dans `state.json > roles` et `voix`)
| Qui | Rôle | Voix |
|---|---|---|
| — | Président Barbichu / narrateur | Hugo `3Tp5mYhT9wrfnry9pzvV` |
| — | Reine de Beurrélie | Morgane `ZYOBieLaunTiQrTrvNQq` |
| doudou dictador (TikTok) | Doudou Dictador, roi de Guimauvie | Gronk `Pu9MMuPx0BqjFaVxHf8W` (ancien `30ndZrqtoeQllE13MnID` désactivé) |
| @justnaxt | Kxpl, marchand officiel du royaume | Jean-Patrick `Hs8dAyliGDIYLwC3jaSJ` |
| @esteban_gi19 | Esteban, Comptable royal (garde les écus des likes) | Bastien `69ujSsYIBOGW4duCBBSW` |
| @nat_gbz | Docteur | Paul `RAFNgKBJ8SavtpwF6uUV` |
| @elo_zht | Capitaine de la Garde montée (3 étoiles) | Emilio `FmOMKTYDTzzmpxukR0kC` |
| @pancakemiam450 | a fait inviter la Reine | |
| @matska_prv | bar à cocktails | |
| @naelmomo8 | Grand Prix | |
| Kets4eki, E_kling (TikTok) | citoyens | |
Nouveau personnage = nouvelle voix française choisie avec `creative_list_voices`, notée ici et dans `state.json`.
Identifier les personnes : Instagram `@pseudo` dans la légende et le 1er commentaire (+ `carouselTags` pour un carrousel) ; TikTok pseudo sans @ (sauf comptes TikTok connus).

### Règle du comptable (Matis, 14/11/2026, permanente)
Vote sur l'ARGENT (budget, dépense, taxe, commerce, chantier payant) : le vote de @esteban_gi19 vaut 30 % ; les autres se partagent 70 %. À l'écran : boulier doré, « VOTE DU COMPTABLE : 30 % ». S'il n'a pas voté, vote normal.

## La série
- **Pitch** : un vieux mage, le Président Barbichu, est devenu président du Fromagistan par erreur. Pays en ruine, magie qui rate. Il raconte à la 1re personne.
- **Personnages** (dessinés en code, `rig.py`) : Barbichu, le pigeon conseiller (blasé), le rival au monocle, la reporter de « Fromagistan Info », les citoyens. Tous inventés. **Jamais de caricature ressemblante ni de nom déformé d'une personne réelle** ; pas de personnage protégé.
- **Style** (précisé par Matis le 11/11/2026) : dessin à plat sans contour, mais détaillé et pas enfantin : ombres en deux tons, yeux ouverts avec iris, vêtements avec col, boutons et ceinture, décor avec fenêtres, fissures et pavés. Personnages animés (marche, salut, parole, clignement), cartes et compteurs façon jeu mobile.
- **Effets visuels** (`fx.py`, consigne de Matis du 12/11/2026 : « pas un PNG de flamme posé dessus ») : jamais un dessin d'effet collé à plat. Feu en couches floutées qui ondulent, braises, fumée ; lumière additive qui éclaire le visage, le décor et le sol (`fx.glow`) ; la nuit se fait avec `fx.darken` sur un décor normal, et c'est la source de lumière qui rend la couleur ; trait de magie du bâton vers la cible (`fx.bolt`), étincelles (`fx.sparkles`), éclair d'allumage léger (`fx.flash`). Un effet laisse une trace (barbe roussie, fumée qui s'échappe).
- **Caméra** (`SHOTS` + `engine.shot_cam`) : plans serrés sur les visages (zoom 1,5 à 1,9), un plan par réplique, plan large seulement pour poser un décor ; léger balancement gauche-droite, petit zoom d'attaque et lente avancée, glissé fluide entre deux plans d'une même scène. Les cartes, le bandeau et les sous-titres sont dessinés sur le calque d'interface `u`, hors caméra ; les personnages se posent vers y = 1650 pour que le visage reste au-dessus des sous-titres (y = 1500).
- **Règles du jeu, affichées avec les VRAIS chiffres de l'épisode précédent** (lus dans les stats, Instagram + TikTok additionnés) : 1 abonné = 1 citoyen · 1 like = +2 écus · 1 partage = +3 popularité · 1 enregistrement = +1 magie · commentaire = 1 voix (1, 2 ou 3) · commentaire le plus liké = « loi citoyenne » de l'épisode suivant. Ne jamais inventer un chiffre ni un résultat.
- **Une seule vidéo pour les deux réseaux, tout est additionné** (consigne de Matis du 11/11/2026) : abonnés Instagram + TikTok = citoyens ; likes, partages, enregistrements et commentaires des deux réseaux additionnés ; **votes des deux réseaux additionnés** (capture Instagram de Matis + commentaires TikTok) ; le commentaire le plus liké est cherché sur les deux. Jamais une version par réseau.
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
| 2 | 15/11/2026 | Nouveau format (2 min 40). Bilan ép. 1 : 155 likes = 310 écus, 21 commentaires, 5 partages, 6 enregistrements, 52 citoyens (IG 42 + TikTok 10). Toit réparé (vote d'argent : comptable 30 % + Kets4eki 35 % contre justnaxt 35 % pour le marché). Kxpl marchand officiel, sa loi en vote ; cabinet du Docteur ; Garde royale et Garde montée (Capitaine @elo_zht) ; bar sans alcool ; circuit du Grand Prix, grille vide ; marché aux fromages proposé, pas construit. Visite de la Reine : elle signe beurre contre fromage si on LIKE et REPUBLIE (Beurrélie 50/100). Guimauvie de Doudou Dictador (3 habitants + 1 chèvre, rivalité 10/100). **Mystères ouverts** : espion-ourson sous le carrosse ; 3 meules volées (touffe de peluche noire, petites empreintes) ; la porte de la cave a frappé 3 coups | 1 loi de Kxpl (100) · 2 marché aux fromages (150) · 3 mur anti-guimauve (200) — vote d'argent, comptable 30 % |
| 3 | 17/11/2026 | Format 1 min (69 s). Mur anti-guimauve construit (vote 3 à 100 % : @esteban_gi19 30 %, @justnaxt, @alice._.glt31). Bilan ép. 2 : 16 likes = 32 écus, 7 partages, 6 commentaires, 51 citoyens (IG 41 + TikTok 10). Coffre 342 − mur 200 − loi de Kxpl 100 (avance du comptable) = 42 écus. Loi de Kxpl votée ; écurie « First » de Kxpl 1re inscrite au Grand Prix. Reine : 7 partages sur 5 demandés → accord beurre contre fromage signé (Beurrélie 60/100). **Indice** : sous le mur, une piste d'empreintes de peluche noire SORT de la porte fermée à clé de la cave (3 coups) → le voleur de meules serait dans le château. Mystères ouverts : voleur/espion dans le château ; ce qu'il y a derrière la porte de la cave | 1 Kxpl ministre des commerces et des cultures (0) · 2 marché aux fromages (150, coffre 42) · 3 la Garde fouille la cave (30) — vote d'argent, comptable 30 % |
| Spécial | 18/11/2026 | Bataille manga dans la cave : la cave était pleine de guimauves et d'oursons de Doudou (= les voleurs de meules) ; attaques du Capitaine, de Kxpl, d'Esteban ; contre-attaque « Guimauve géante » ; le public propose des attaques | attaques en commentaire |
| 4 | 21/11/2026 | 49 s, règles anti-décrochage. Attaque gagnante (commentaire le plus liké, capture Instagram de Matis 19/11) : @justnaxt, Tempête des épices → la Guimauve géante fond. Bonus : taxe sur le revenu d'@esteban_gi19 (les oursons ruinés lâchent les meules), Serment mortel de @nat_gbz. Doudou s'enfuit : « Je reviendrai… au Grand Prix ! ». **Indice** : un badge d'ourson portant la marque du carrosse de la Reine de Beurrélie. Bilan ép. 3 + spécial : 21 likes = +42 écus (coffre 84), 1 partage = +3 popularité, 55 citoyens (IG 42 + TikTok 13). Mystères ouverts : qui a ouvert la cave à Doudou ? l'espion vient-il du carrosse de la Reine ? Doudou au Grand Prix | 1 Kxpl ministre des commerces et des cultures (0) · 2 marché aux fromages (150, coffre 84) · 3 piège à espion (30) — vote d'argent, comptable 30 % |
