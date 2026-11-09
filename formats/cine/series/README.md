# BLACK-OUT — la série (seule série suivie depuis le 09/11/2026)

Consigne de Matis du 09/11/2026 : **tout en français, une seule série**, fiction à choix « survie chez toi », un épisode (une « nuit ») tous les 2 jours à 19:00 (Paris). Chaque nuit commence par la suite du choix le plus voté. Le résultat du vote vient de Matis (`state.json > votes`), jamais d'une estimation.

## Promesse
À minuit pile, toute la ville s'éteint : plus de courant, plus de réseau. Tu es seul chez toi. Un seul message arrive, d'un numéro inconnu : « N'ouvre à personne cette nuit. Même à quelqu'un que tu aimes. » Puis des gens que tu aimes viennent frapper. Ce ne sont pas eux.
Mystères de fond, à ne jamais résoudre d'un coup : qui sont « ceux qui frappent » ? Qui a envoyé le message ? Pourquoi le téléphone sonne-t-il sans réseau ?

## Règles d'écriture
- 2e personne (« tu »), présent, répliques de 12 mots au plus ; le personnage n'a ni prénom ni genre marqué à l'écran (éviter « seul·e », « sûr », « muet » dans les choix : verbes à l'infinitif).
- 45 à 70 s. Une révélation, un son ou un nouvel écran toutes les 5 à 8 s. Accroche comprise en une phrase et sans le son (image + sous-titres), en retour en arrière si besoin (« Trois heures plus tôt »).
- Ouverture d'une suite : `Tu as choisi d'ouvrir.` (vote connu) dès la 1re seconde, ou l'ouverture « deux chemins » (vote inconnu, voir `scripts.md`).
- Une seule nouvelle menace par nuit ; fin sur un choix **1 / 2**, un verbe chacun (OUVRIR / DÉCROCHER), les deux défendables. Pas de voix pour expliquer le vote au-delà de « Écris 1 ou 2 en commentaire. »
- La peur vient de ce qu'on entend, lit et n'ouvre pas : **jamais** de violence montrée, de sang, de blessure, d'arme, de mode d'emploi dangereux. La ville n'est pas nommée.
- `Fiction générée par IA.` dans chaque légende.

## Voix (fixes)
| Rôle | Voix | Réglages |
|---|---|---|
| Narrateur | French John `5DD3eZMBEVRcWAmpxded` | `eleven_v4`, `language_code` `fr`, une prise pour tout l'épisode, `[pause]` entre chaque réplique |
| « Maman » (la chose qui imite ta mère) | Isabelle `1cNpTcbDy2UA0duXppd5` | derrière la porte : `lo` 200, `hi` 2800, `gain_db` +3 ; sous-titres bleu glacé (`caption_color` [150, 215, 255], `caption_all`) |
| Autre voix imitée (voisin, ami) | voix de la bibliothèque, choisie une fois puis fixe | même traitement derrière la porte ; au téléphone, `phone: true` |

## Continuité (à compléter après chaque nuit)
| Nuit | Publiée | Heure à la fin | Batterie | Ce qui s'est passé | Choix posé | Vote |
|---|---|---|---|---|---|---|
| 1 | 09/11/2026 | 03:13 | 2 % | Panne à 00:00. SMS d'un numéro inconnu à 00:01. À 02:40, quelqu'un hurle ton prénom dehors. À 03:12, « maman » frappe (ta mère habite à 600 km). Ton téléphone sonne « Maman »… sans réseau. | 1 OUVRIR · 2 DÉCROCHER | à donner par Matis |

HUD : `BLACK-OUT · NUIT N`, heure et batterie (rouge à 5 % et moins) qui reprennent là où la nuit précédente s'arrête. Écrans de téléphone dessinés en code (`ui.py`) : `lock` (écran verrouillé + notification), `sms` (conversation), `incoming` (appel entrant), toujours « Pas de service ».

## Images et plans de la série (flow ElevenLabs `svWwFUy11l9jmpeQIqYZ`)
Les liens se récupèrent gratuitement avec `creative_get_generations` sur ce flow. **Réutiliser avant de générer.**
| Fichier | Contenu | Remarques |
|---|---|---|
| `A.png` | ta porte d'entrée vue du couloir, judas, lumière dessous, manteau accroché | revient à chaque coup frappé |
| `VA2.mp4` | plan animé de A | une silhouette passe de 0,4 à 1,7 s : `offset` 2,0 au moins (`VA.mp4` est raté : la porte s'ouvre) |
| `B.png` · `VB.mp4` | fenêtre ouverte sur la ville éclairée, pluie · la ville s'éteint | la panne |
| `C.png` | ta main, ton téléphone (écran blanc), le lit | écran collé en code ; quad `[[0.4611,0.3824],[0.6903,0.384],[0.6854,0.634],[0.4667,0.6363]]`, `cap_y` 0,705 |
| `D.png` | la rue sous la pluie vue de ta fenêtre, une silhouette immobile | « dehors » |
| `E.png` · `VE.mp4` | « maman » vue par le judas (fish-eye) · plan animé | VE recule après 3 s : `speed` 0,52 au plus. Pour tout nouveau plan d'elle, partir de E.png (édition d'image) pour garder le même visage |
| `F.png` | la vraie photo de ta mère (plage), sur une étagère | « elle habite à 600 km » |
| `G.png` · `VG.mp4` | la poignée et le verrou · la poignée bouge | tension à la porte |
| `cover_bg.png` | image de VE à 2,2 s | fond de couverture |

## Séries archivées (anglais, arrêtées le 09/11/2026)
Omertà (3 épisodes), CALLER ID (1), NIGHT DISPATCH (1), THE OFFER et COLD FILE (jamais publiées). Leurs scripts restent dans `scripts.md` (fin du fichier) et `episodes/` pour mémoire ; ne plus les publier.
