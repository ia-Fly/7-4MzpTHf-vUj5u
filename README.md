# Atelier @situation.douteuse

Branche `studio` : l'atelier qui fabrique et publie une vidéo par jour (19 h, Instagram + TikTok) et la mémoire de ce qui marche.
La branche `media` sert seulement à héberger quelques minutes les vidéos à publier (Metricool lit des liens publics).

| Fichier | Rôle |
|---|---|
| `RUNBOOK.md` | la procédure quotidienne, pas à pas (fait foi) |
| `STRATEGY.md` | objectifs, résultats, leçons, règle de choix, pistes |
| `state.json` | file d'attente, historique des posts, votes, compteurs |
| `journal/` | un compte rendu par jour |
| `formats/fusion/` | simulation de fusion « Can it reach … ? » (sans paroles) |
| `formats/omerta/` | série à vote avec voix (épisodes 1 et 2 anglais) |
| `tools/` | hébergement media, contrôle qualité, modèles de voix |
| `queue/` | vidéos prêtes, pas encore publiées partout |

Installer dans une session neuve : `bash setup.sh` (format fusion) ou `bash setup.sh --voices` (épisodes à voix).

Pour mettre la tâche en pause ou changer l'heure : demander à Claude dans la conversation (« mets en pause la vidéo du jour »).
