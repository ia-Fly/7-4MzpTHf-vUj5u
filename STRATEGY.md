# STRATÉGIE — @situation.douteuse (Instagram) / @situation.douteus (TikTok)

Mis à jour par chaque passage de la tâche planifiée. Les chiffres viennent des outils (vidIQ, Metricool), jamais d'estimations.

## Objectif et cap
- 10 000 abonnés au total. Point de départ le 29/10/2026 : Instagram 4 abonnés, TikTok 0 (compte neuf).
- Problème n°1 mesuré : l'abonnement (environ 1 abonné pour 1 100 vues sur Instagram).
- Depuis le 29/10 : tout est publié en anglais pour viser un public international ; Matis veut aussi de nouveaux formats internationaux, comme @cool_games_heel.

## Formats
| Format | Statut | Promesse | Notes |
|---|---|---|---|
| **Fusion** (`formats/fusion`) | prêt, produit seul en ~5 min | « Can it reach … ? » : deux objets identiques fusionnent, dernier niveau caché « ? » | Thèmes : planets, fruits, numbers. Le metteur en scène place le dernier niveau vers 88 % de la vidéo. Sans paroles, donc international. |
| **Omertà** (`formats/omerta`) | épisodes 1 et 2 en anglais faits | Fiction à vote : le choix le plus voté devient l'épisode suivant | Lourd (1–2 h). Seulement si le vote est connu (`state.json > votes`). |

Risque assumé : un même compte mélange fiction et simulations. On mesure la conversion en abonnés par format ; si un format écrase l'autre, on le garde comme cœur du compte et on propose à Matis d'ouvrir un compte dédié pour l'autre (son plan : un compte par catégorie).

## Système des 5 projets (consigne de Matis du 29/10/2026, en vigueur à partir du 31/10)
- 5 projets (séries/formats) tournent en même temps ; **une seule vidéo par jour**, chaque jour le projet suivant de la rotation (A, B, C, D, E, A…). La vidéo du jour va sur Instagram et TikTok (TikTok peut avoir un épisode de décalage via la file).
- Rotation de départ : **A Omertà** · **B Fusion** · **C Escape** (une balle rebondit dans un anneau qui tourne avec une brèche ; chaque sortie fait naître 2 balles : « WILL IT ESCAPE? ») · **D Marble Race** (course de billes de couleur, « Which color wins? Comment before the end ») · **E Fruit Drama EN** (mini-drame de fruits en anglais, reprise du « Zéro », meilleur départ mesuré : skip 28 %).
  Choix du 30/10 : C et D viennent des pistes de cette page (simulations sans paroles, donc internationales, produites seules en quelques minutes, 100 % maison) ; E est le seul autre format déjà testé qui a bien retenu au départ.
- **Bilan de cycle** quand les 5 projets en cours ont chacun 5 épisodes publiés et ≥ 48 h de stats sur leur 5e : comparer médiane des vues, % regardé, skip, commentaires/vues, abonnés gagnés (IG + TikTok). Supprimer le moins bon, garder les autres, créer un nouveau projet à 0 épisode à sa place (même rang dans la rotation), puis continuer. Chaque bilan est écrit ici (classement, projet supprimé, nouveau projet et pourquoi) et dans le rapport.
- Omertà : si son tour arrive sans résultat du vote précédent dans `state.json > votes`, on publie le projet suivant et on revient à Omertà ensuite. Jamais de résultat inventé.
- Compteur d'épisodes : `state.json > projects` (épisodes anglais publiés ; Omertà compte ses ép. 1 à 3 anglais).

## Règle de choix (appliquée chaque jour, voir RUNBOOK §4)
0. Depuis le 31/10, la rotation des 5 projets passe avant tout (voir ci-dessus) ; les points suivants servent à choisir le thème/l'épisode à l'intérieur du projet du jour.
1. File d'attente d'abord (`state.json > queue`).
2. Sinon : jours 0 et 1 du cycle = exploiter le meilleur (format, thème) par réseau d'après la médiane des vues de ses 3 derniers posts ; jour 2 = explorer une nouveauté.
3. Jamais le même thème deux jours de suite sur un réseau ; jamais une vidéo deux fois sur le même réseau.
4. Quand une vidéo dépasse 3× la médiane du compte, refaire sous 48 h une variante proche (même mécanique, autre thème).

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
| 29/10 | IG | omerta-ep2-en | Omertà (EN) | 44 s | 2 928 | 21,5 s (49 %) | 26 % | 43 | 8 | 1 | 0 |
| 29/10 | TikTok | omerta-ep1-en | Omertà (EN) | 23 s | 196 | n.d. | n.d. | 6 | 1 | 0 | n.d. |
| 30/10 | IG | omerta-ep3-en | Omertà (EN) | 26 s | à lire | | | | | | |
| 30/10 | TikTok | omerta-ep2-en | Omertà (EN) | 44 s | à lire | | | | | | |

Abonnés : 29/10 → IG 4 · TikTok 0 ; 30/10 → IG 5 (+1) · TikTok 0.

## Leçons datées
- 28/10 : nos reels (24–39 s) sont plus courts que les références (60–97 s) ; le meilleur départ (skip 28 %) est celui qui montre un objet en mouvement et une situation claire dès la 1re seconde.
- 30/10 : Omertà ép. 2 EN (44 s, ouverture en flash-forward « This coffee is poisoned ») : skip 26 % contre 41 % pour l'ép. 1 FR, et 8 commentaires (0,27 % des vues). Mais 49 % regardé seulement : la moitié part vers 20 s. → ép. 3 raccourci à 26 s, choix posé à 19 s, CTA « follow » affiché sans être dit.
- 30/10 : TikTok démarre lentement (ép. 1 EN : 196 vues, 0 abonné). Instagram : 5 abonnés (+1).
- 29/10 : référence @cool_games_heel (fusion) : 22 posts, 1 602 abonnés ; une fusion de patates a fait environ 972 000 vues. Le format fusion est lancé chez nous.

## Pistes (idées à tester, de la plus prometteuse à la moins)
1. Nouveaux thèmes fusion : pierres précieuses, emojis maison, animaux ronds, boules de sport, desserts, bulles de couleurs, « BLACK HOLE » après le Soleil (suite des planètes).
2. Mécanique « échappe-toi du cercle » : une balle rebondit dans un anneau qui tourne avec une brèche ; à chaque sortie, 2 nouvelles balles (« WILL IT EXPLODE? »).
3. Course de billes de couleurs sur un parcours (« which color wins? ») avec vote en commentaire avant la fin.
4. Durée : comparer 35 s et 48 s sur le même thème.
5. Accroche : afficher dès 0 s le dernier niveau flouté en « ? » au centre du cercle.
6. Son : notes d'une mélodie du domaine public jouées à chaque fusion (ex. « Ode to Joy »), synthétisées maison.

## Prochaine expérience
- Omertà ép. 3 (26 s, choix à 19 s) contre ép. 2 (44 s, choix à 38 s) : % regardé et commentaires/vues. Si l'ép. 3 garde ≥ 70 % des gens jusqu'au choix, tous les épisodes Omertà passent à ≤ 30 s.

## Votes Omertà
Voir `state.json > votes`. Ép. 1 → SIT (vote Instagram FR). Ép. 2 → DRINK (Matis, 29/10). Ép. 3 → OPEN ou DELIVER : résultat à donner par Matis.
