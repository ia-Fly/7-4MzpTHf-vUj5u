# STRATÉGIE — @situation.douteuse (Instagram) / @situation.douteus (TikTok)

Mis à jour par chaque passage de la tâche planifiée. Les chiffres viennent des outils (vidIQ, Metricool), jamais d'estimations.

## Objectif et cap
- 10 000 abonnés au total. Point de départ le 29/10/2026 : Instagram 4 abonnés, TikTok 0 (compte neuf).
- Problème n°1 mesuré : l'abonnement (environ 1 abonné pour 1 100 vues sur Instagram).
- Depuis le 29/10 : tout est publié en anglais pour viser un public international.
- **Changement de cap du 05/11/2026 (Matis) :** compte ElevenLabs Creator ; il veut « un truc de pro et pas pour les enfants », et la meilleure qualité possible. Fini les simulations de billes et de fruits, les dessins et les voix de synthèse gratuites. Tout passe au format CINE (`formats/cine/README.md`) : thriller adulte, photoréaliste, voix et son ElevenLabs. Les tâches planifiées sont en pause depuis le 04/11, à la demande de Matis.

## Formats
| Format | Statut | Promesse | Notes |
|---|---|---|---|
| **CINE** (`formats/cine`) | actuel | Thriller adulte en vue subjective : « tu » es dedans, tu choisis | Images Seedream, plans Veo 3.1 Lite, voix `eleven_v4`, bruitages et musique ElevenLabs, écrans et sous-titres en code. |
| Fusion, Escape, Marble Race, Fruit Drama, ancien Omertà | retirés le 05/11/2026 | | Trop enfantins selon Matis. Code conservé pour mémoire ; leurs chiffres restent dans le tableau. |

## Budget ElevenLabs
- Creator : 121 000 crédits par mois, soit environ 4 000 par jour. Registre : `elevenlabs/ledger.jsonl`, `python3 tools/el_fetch.py --summary`.
- **Rythme choisi par Matis le 05/11/2026 : 1 vidéo tous les 2 jours, recette Pro (≈ 6 300 crédits, 4 plans animés).** Environ 15-16 vidéos par mois, soit 95 000 à 100 000 crédits. Autres recettes : `formats/cine/README.md`.
- Tous les bruitages et musiques sont gardés et réutilisés (consigne de Matis, `formats/cine/sound_library.json`).
- Les passages de la tâche planifiée du 03 et du 04/11 ont échoué : limite d'usage Claude atteinte. La production doit rester légère en appels d'outils (voir README CINE).

## Système des 5 projets (consigne de Matis du 29/10/2026, en vigueur à partir du 31/10)
- 5 projets (séries/formats) tournent en même temps ; **une seule vidéo par passage (tous les 2 jours)**, à chaque fois le projet suivant de la rotation (A, B, C, D, E, A…). La vidéo va sur Instagram et TikTok (TikTok peut avoir un épisode de décalage via la file).
- **Rotation depuis le 05/11/2026 (cycle 2) : A OMERTÀ · B CALLER ID · C NIGHT DISPATCH · D THE OFFER · E COLD FILE** (`formats/cine/series/README.md`). Prochain : B, épisode 1. Fusion, Escape, Marble Race et Fruit Drama sont sortis hors bilan de cycle, à la demande de Matis.
- **Bilan de cycle** quand les 5 projets en cours ont chacun 5 épisodes publiés et ≥ 48 h de stats sur leur 5e : comparer médiane des vues, % regardé, skip, commentaires/vues, abonnés gagnés (IG + TikTok). Supprimer le moins bon, garder les autres, créer un nouveau projet à 0 épisode à sa place (même rang dans la rotation), puis continuer. Chaque bilan est écrit ici (classement, projet supprimé, nouveau projet et pourquoi) et dans le rapport.
- Omertà : si son tour arrive sans résultat du vote précédent dans `state.json > votes`, on publie le projet suivant et on revient à Omertà ensuite. Jamais de résultat inventé.
- Compteur d'épisodes : `state.json > projects` (épisodes anglais publiés ; Omertà compte ses ép. 1 à 3 anglais).
- État au 05/11 : A Omertà 3 ép. (l'ép. 4 passe au nouveau style) · B, C, D, E : 0.

## Règle de choix (voir RUNBOOK §4)
1. La rotation des 5 projets passe avant tout. File d'attente d'abord (`state.json > queue`), sinon épisode suivant du projet du jour.
2. Jamais une vidéo deux fois sur le même réseau.
3. Quand une vidéo dépasse 3× la médiane du compte, faire passer sa série en priorité au tour suivant.

## Règles de montage (issues des comptes de référence)
- 0–1 s : mouvement et son fort ; jamais d'écran noir ni de titre seul.
- 0–3 s : la question/le paradoxe est lisible (ex. « CAN IT REACH THE SUN? »).
- Un repère visible jusqu'à la fin (niveau, score, « ? »).
- Relance toutes les 2 à 5 s ; « follow » vers 40 % et 70 %.
- Fin : récompense (dernier niveau) puis appel au commentaire ; ou choix en 2 mots (Omertà).

## Tableau des résultats
| Date | Réseau | Vidéo | Format / thème | Durée | Vues | Regardé (moy.) | Skip 3 s | Likes | Com. | Partages | Enreg. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 25/10 | IG | le-zero-p1-fr | fruit drama (FR) | 39 s | 1 554 | 16,3 s (42 %) | 28 % | 34 | 8 | 3 | 1 |
| 25/10 | IG | omerta-ep1-fr | Omertà (FR) | 24 s | 2 812 | 13,0 s (54 %) | 40 % | 74 | 5 | 0 | 4 |
| 29/10 | IG | omerta-ep2-en | Omertà (EN) | 44 s | 3 118 | 21,5 s (49 %) | 26 % | 44 | 8 | 1 | 0 |
| 29/10 | TikTok | omerta-ep1-en | Omertà (EN) | 23 s | 199 | n.d. | n.d. | 6 | 1 | 0 | n.d. |
| 30/10 | IG | omerta-ep3-en | Omertà (EN) | 26 s | 1 641 | 14,1 s (57 %) | 24 % | 14 | 5 | 0 | 2 |
| 30/10 | IG | (Omertà ép. 1 EN, publié hors routine à 14:05) | Omertà (EN) | 23 s | 689 | 12,2 s (53 %) | 42 % | 4 | 2 | 1 | 0 |
| 30/10 | TikTok | omerta-ep2-en | Omertà (EN) | 44 s | 0 (Metricool, 01/11 — à confirmer) | | | 0 | 0 | 0 | |
| 31/10 | IG | fusion-planets-s10 | Fusion / planets (proj. B ép. 1) | 48 s | 1 698 (19 h) | 18,8 s (39 %) | 29,5 % | 16 | 1 | 0 | 0 |
| 31/10 | TikTok | fusion-planets-s10 | Fusion / planets (proj. B ép. 1) | 48 s | n.d. (pas encore dans Metricool) | | | | | | |
| 01/11 | IG | escape-s1123 | Escape (proj. C ép. 1) | 34 s | à lire | | | | | | |
| 01/11 | TikTok | escape-s1123 | Escape (proj. C ép. 1) | 34 s | à lire | | | | | | |

Abonnés : 29/10 → IG 4 · TikTok 0 ; 30/10 → IG 5 (+1) · TikTok 0 ; 31/10 → IG 5 (=) · TikTok 0 (=) ; 01/11 → IG 6 (+1) · TikTok 0 (=).

## Leçons datées
- 05/11 : pilote CALLER ID monté sur le format CINE. Coûts réels mesurés : plan Veo Lite 4 s 1080p sans son = 1 212 crédits, image Seedream 5 Lite 2K = 212, voix ≈ 1 crédit/caractère, bruitage 3,3/s, musique 15/s. La vidéo avec son généré coûte 3 fois plus : on la génère muette et on fait le son à part. Hypothèse à mesurer : des images réalistes et une vraie voix font baisser le skip sous 25 % et monter le % regardé au-dessus de 57 % (meilleur score : Omertà ép. 3).
- 01/11 : Fusion planets (48 s, ~19 h) : 1 698 vues (≈ Omertà ép. 3 au même âge), mais seulement 39 % regardé (18,8 s) et 1 commentaire (0,06 % des vues, 5× moins qu'Omertà). Skip 29,5 % (Omertà ép. 3 : 24 %). La simulation de 48 s retient moins qu'une fiction de 26 s ; les simulations suivantes passent à 34 s (Escape, Marble Race) pour tester la durée. +1 abonné IG (6). TikTok : toujours 0 abonné ; l'ép. 2 Omertà affiche 0 vue dans Metricool (donnée à reconfirmer demain).
- 31/10 : Omertà ép. 3 (26 s, choix à 19 s) : 57 % regardé (contre 49 % pour l'ép. 2 à 44 s), skip 24 %, 5 com. (0,30 % des vues, comme l'ép. 2). Mais temps moyen 14,1 s < 19 s : la moitié des gens ne voit pas le choix. Vues en baisse (1 641 en 20 h contre 3 118). → Omertà ép. 4 : poser le choix dès 12-14 s et le montrer en grand dans le 1er plan (« OPEN or DELIVER? » en haut dès 0 s). Aucun abonné gagné depuis le 30/10 : le compte convertit très mal ; la rotation 5 projets doit dire quel format convertit.
- 28/10 : nos reels (24–39 s) sont plus courts que les références (60–97 s) ; le meilleur départ (skip 28 %) est celui qui montre un objet en mouvement et une situation claire dès la 1re seconde.
- 30/10 : Omertà ép. 2 EN (44 s, ouverture en flash-forward « This coffee is poisoned ») : skip 26 % contre 41 % pour l'ép. 1 FR, et 8 commentaires (0,27 % des vues). Mais 49 % regardé seulement : la moitié part vers 20 s. → ép. 3 raccourci à 26 s, choix posé à 19 s, CTA « follow » affiché sans être dit.
- 30/10 : TikTok démarre lentement (ép. 1 EN : 196 vues, 0 abonné). Instagram : 5 abonnés (+1).
- 29/10 : référence @cool_games_heel (fusion) : 22 posts, 1 602 abonnés ; une fusion de patates a fait environ 972 000 vues. Le format fusion est lancé chez nous.

## Pistes (idées à tester, de la plus prometteuse à la moins)
1. Voix signature : concevoir une voix propre au compte (`creative_design_voice`) au lieu d'une voix de bibliothèque partagée.
2. Doublage français et espagnol des meilleurs épisodes (nouvelle voix en `eleven_v4`, même montage) pour ouvrir un deuxième public.
3. Durée : comparer 25 s et 40 s sur la même série.
4. Accroche : montrer le choix dès 0 s en petit, dans le bandeau.

## Prochaine expérience
- Comparer les 5 séries sur leurs 5 premiers épisodes : skip, % regardé, commentaires/vues, abonnés gagnés. Hypothèse : les votes (CALLER ID, OMERTÀ) et l'énigme (COLD FILE) donnent plus de commentaires que le dilemme seul.

## Votes Omertà
Voir `state.json > votes`. Ép. 1 → SIT (vote Instagram FR). Ép. 2 → DRINK (Matis, 29/10). Ép. 3 → DELIVER (Matis, 31/10). Ép. 4 = « tu livres l'enveloppe », produit au tour d'Omertà du 04/11 (choix vers 12-14 s, voir leçon du 31/10).
