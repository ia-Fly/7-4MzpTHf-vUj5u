# Atelier @situation.douteuse

Branche `studio` : l'atelier qui fabrique et publie une vidéo tous les 2 jours (20 h à Washington DC, Instagram + TikTok) et la mémoire de ce qui marche.
La branche `media` sert seulement à héberger quelques minutes les vidéos à publier (Metricool lit des liens publics).

| Fichier | Rôle |
|---|---|
| `RUNBOOK.md` | la procédure quotidienne, pas à pas (fait foi) |
| `STRATEGY.md` | objectifs, résultats, leçons, règle de choix, pistes |
| `state.json` | file d'attente, historique des posts, votes, compteurs |
| `journal/` | un compte rendu par jour |
| `formats/cine/` | **le format actuel** : vidéos photoréalistes ElevenLabs, séries, monteur, banque de sons |
| `elevenlabs/ledger.jsonl` | registre des crédits ElevenLabs dépensés |
| `formats/fusion`, `escape`, `marble`, `omerta` | anciens formats, retirés le 05/11/2026 |
| `tools/` | hébergement media, contrôle qualité, téléchargement ElevenLabs |
| `queue/` | vidéos prêtes, pas encore publiées partout |

Installer dans une session neuve : `bash setup.sh`.

Pour mettre la tâche en pause ou changer l'heure : demander à Claude dans la conversation (« mets en pause la vidéo du jour »).
