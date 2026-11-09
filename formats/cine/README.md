# Format CINE — vidéos photoréalistes faites avec ElevenLabs

Le format qui remplace les dessins et les simulations depuis le 05/11/2026 (consigne de Matis : un truc de pro, pas pour les enfants).
Tout passe par le **connecteur ElevenLabs** (pas de clé API : sur l'offre Creator, l'API image/vidéo est réservée à l'offre Pro).
Le montage final (sous-titres, écrans de téléphone, mixage) se fait ici en code : `build.py` + `ui.py`.
**Depuis le 09/11/2026 (consigne de Matis) : tout en français, une seule série, BLACK-OUT** (`series/README.md`), publiée à 19:00 (Paris). Modèle d'épisode : `episodes/blackout-n1/`.

## Coûts mesurés (crédits, offre Creator : 121 000 par mois, soit environ 4 000 par jour)
| Élément | Modèle | Coût |
|---|---|---|
| Voix | `eleven_v4` | environ 1 crédit par caractère (une réplique de 30 s : environ 400) |
| Filtre téléphone / radio / pièce | `eleven_audio_effects` | 0 |
| Temps mot par mot | `eleven_scribe_v1` sur un nœud voix | 0 sur le pilote |
| Image 2K (1440×2560) | `bytedance-seedream-5-lite` | 212 — **modèle par défaut** (meilleur rapport qualité/prix du test du 05/11) |
| Image | `flux-2-pro` 2K : 454 · `gemini-3.1-flash-image` 1K : 406 · `gemini-3-pro-image` : environ 1 218 (visage récurrent) | |
| Plan animé 4 s, sans son | `veo-3.1-lite-generate-001` 720p : 727 · 1080p : 1 212 | **prix réel** |
| Autres vidéos 5 s (estimations) | `kling-2.5-turbo` 2 121 · `bytedance-seedance-v2-mini` 480p 2 133 / 720p 4 581 · `wan-2.6` 3 030 | plus chers que Veo Lite |
| Bruitage | `eleven_text_to_sound_v2` | 3,3 par seconde |
| Musique | `eleven_music_v2_5` | 15 par seconde |

Toujours : `generate_audio: false` sur la vidéo (le son coûte très cher : Veo Lite 8 s avec son = 2 424) et `generations_count: 1`.

## Recettes (`state.json > elevenlabs.recipe` ; choix de Matis du 05/11/2026 : **Pro, 1 vidéo tous les 2 jours**)
| Recette | Contenu d'un épisode de 30-35 s | Crédits | Rythme tenable |
|---|---|---|---|
| **Hybride** | voix 400 · 4 images 850 · 2 plans 1080p 2 424 · écrans en code · sons de la banque | ≈ 3 700 | 1 par jour |
| **Pro** (celle du pilote) | voix 400 · 5 images 1 060 · 4 plans 1080p 4 848 · écrans en code · sons de la banque | ≈ 6 300 | 1 tous les 2 jours |
| **Plein mouvement** | voix 400 · 8 images 1 700 · 8 plans 720p 5 816 | ≈ 7 900 | 1 tous les 2 jours |

## Chaîne d'un épisode (dans l'ordre, tout est dans le même flow)
Charger d'un coup avec ToolSearch : `creative_create_flow, creative_add_flow_node, creative_run_flow_nodes, creative_get_flow_run_status, creative_get_generations, creative_add_flow_asset_node, creative_transcribe_audio`. Éviter `creative_get_flow_node_types` et les guides de modèles (très longs) : tout est ici.
1. **Écrire** : script en français, `episode.json` (modèle : `episodes/blackout-n1/`). Série, voix, images réutilisables et continuité : `series/README.md`. Suites déjà écrites pour chaque résultat de vote : `series/scripts.md`.
2. **Sons d'abord dans la banque** : `sound_library.json`. Un son manquant se génère puis s'ajoute à la banque (consigne de Matis : tout garder).
3. **Voix** : `creative_add_flow_node` (node_type `tts`, model `eleven_v4`, voice_id de la série, `language_code` `fr`), un nœud par personnage ; tout le texte du personnage dans un seul nœud, avec des balises (`[whispers]`, `[slowly]`). **Mettre `[pause]` entre chaque réplique** : le monteur découpe la prise sur ces silences, puis règle lui-même le rythme avec `gap`.
   Lancer avec `creative_run_flow_nodes` et `generations_count: 1`.
4. **Téléphone/radio** : nœud `audio-effects` (`filter_preset_id: "phone"`) relié à la voix, `generations_count: 1`. Gratuit.
5. **Repères** : `creative_transcribe_audio` sur chaque voix **avant filtre** ; copier `transcripts[].words` dans `voice_x.words.json`. Sur une voix générée, ces temps sont approximatifs (répartis au caractère, faux sur les chiffres) : le monteur s'en sert seulement pour retrouver les répliques.
6. **Images** : nœuds `image-generation`, `bytedance-seedream-5-lite`, `{"aspect_ratio":"9:16","resolution":"2K"}`, `generations_count: 1`. **Regarder chaque image** avec `creative_get_generations` (aperçu gratuit) ; refaire si un visage, une main ou un objet cloche, avant d'animer.
7. **Plans animés** : nœud `video-generation`, `veo-3.1-lite-generate-001`, `{"duration_secs":4,"aspect_ratio":"9:16","resolution":"1080p","generate_audio":false}`, `connect_from: [nœud image]`. Décrire le mouvement, pas la scène (« Locked-off camera. The water shivers… »).
8. **Télécharger** : écrire `manifest.json` (nom, lien `content_url`, crédits), puis `python3 tools/el_fetch.py manifest.json ASSETS`. Le registre des crédits se remplit tout seul.
   **Regarder chaque plan animé** : `python3 tools/clip_sheet.py planche_clips.jpg ASSETS/V*.mp4`, puis Read. Choisir ensuite `speed` et `offset` en conséquence, ou remplacer un passage raté par l'image fixe (pilote : l'œil restait fermé de 1,5 à 3,4 s).
9. **Monter** : `python3 formats/cine/build.py episode.json ASSETS OUT --preview 0.5,5,12,20,28` pour vérifier, puis sans `--preview` (environ 4 min).
10. **Contrôler** : `tools/check_video.py`, `tools/asr_check.py VIDEO "texte" --lang fr` (voix comprise dans le mix), regarder `planche.jpg` et `cover.jpg`, relire `timeline.json`.
    En français, le modèle de contrôle (Whisper base multilingue) se trompe aussi sur une voix seule. Si le score est sous 0,85 : passer `asr_check` sur les prises sèches (`voice_n.mp3`, `voice_m.mp3`) ; un mot bien entendu à sec mais faux dans le mix = défaut de mixage à corriger (exemple de la nuit 1 : les coups frappés couvraient « frappe » → coups avant et après la réplique, `lead` + `fx_duck_db`).

Les liens signés expirent après quelques heures : `creative_get_generations` en redonne gratuitement.
Ne jamais relancer une génération pour « réessayer » : chaque appel est facturé. D'abord relire le statut.

## Direction artistique
- **Vue subjective** : « tu » es le héros, jamais de visage récurrent. Dos, mains, silhouettes, objets, gros plans : ça évite les incohérences de personnage d'un plan à l'autre.
- **Bloc de style à la fin de chaque prompt d'image** : `Shot on 35mm film, shallow depth of field, low-key lighting, photorealistic, natural imperfections, subtle film grain, neo-noir thriller mood. No text, no logos.` Toujours demander « no text » : les textes sont ajoutés en code.
- **Textes et écrans en code** (`ui.py`) : écran d'appel, durée d'appel, réveil LED, carte de fin. `screen` colle un écran sur le vrai téléphone d'un plan (coins en fractions de l'image).
- Plans de 2 à 4 s, une relance toutes les 2 à 4 s (coupe, impact, chiffre, nouvel écran). Accroche lisible avant 2 s, dès l'image.
- **Sous-titres** : 1 à 3 mots, Barlow Condensed, mot-clé coloré (rouge signal ; bleu glacé pour une voix au téléphone), vers 63 % de la hauteur. Vérifier qu'ils ne cachent pas l'objet du plan (`zoom` + `center` pour décaler).
- **Son** : voix sèche et proche, ambiance continue (bed), musique très basse et baissée sous la voix (`duck_db`), effets baissés aussi sous la voix (`fx_duck_db`, 6 dB), un impact sur chaque révélation. Un bruit qui raconte (coups, vibration) se place **entre** les répliques, pas dessus. -14 LUFS.
- **Fin** : choix 1 / 2 (un verbe chacun), `ÉCRIS 1 OU 2 EN COMMENTAIRE`, abonnement lié à la suite. La voix dit seulement « Écris 1 ou 2 en commentaire » et ce que décide le vote.

## Limites de contenu (Instagram et TikTok coupent la portée sinon)
Ton adulte : tension, menace, dilemmes, zones grises. Mais **jamais** : gore, sang visible, sexe, drogue, armes pointées sur quelqu'un, mode d'emploi d'un acte dangereux, personne réelle, marque, logo, numéro de téléphone réel (à l'écran : « Numéro inconnu » ou un prénom). IA toujours déclarée (`Fiction générée par IA.`).

## Format de episode.json
- En tête : `lang` (`fr`), `voice_rms_db`, `duck_db` (musique et beds sous la voix), `fx_duck_db` (effets sous la voix, 0 par défaut), `lead` (silence avant la 1re réplique, pour un son d'ouverture).
- `voices` : `{"N": {"file", "words", "phone": bool, "lo", "hi", "caption_color": [r, g, b], "caption_all": bool}}` ; `lo`/`hi` = voix étouffée (derrière une porte : 200 / 2800) ; `caption_all` colore toute la réplique (voix « autre »).
- `lines` : `{"id", "voice", "text", "gap", "keywords", "chunks", "pre", "gain_db"}` ; `text` sans balises, identique à ce qui est dit, découpé en répliques pour maîtriser le rythme (`gap` = silence après).
- `shots` : `{"id", "start", "kind", ...}` ; `start` = `"L3"`, `"L3.end"`, `"L3+0.4"`, `"S2"` ou un nombre. `kind` : `video` (file, zoom, center, offset, speed, screen), `still` (file, move ou zoom+center, screen), `phone` (bg, ui : `incoming`, `active`, `ended`), `console` (bg, console : `elapsed`, `status`, `caller`, `line`, `typed` ou `type {text, at, cps}`, `alert {text, at}`, `y` — console d'appel de NIGHT DISPATCH, onde réactive à la voix), `led` (seq), `end` (a, b, question, cta1, cta2, hold).
- `lines[].skip: true` : réplique présente dans la prise mais coupée au montage (le découpage reste juste). Ne jamais simplement retirer une réplique d'une prise : ses mots iraient dans la réplique voisine.
- `sfx` : `{"file", "at", "offset", "gain_db", "until", "trim", "fade_in", "fade_out", "bed"}` ; `offset` = saute le début du fichier, `trim` = durée gardée (prendre deux coups sur quatre) ; `bed: true` = baissé sous la voix.
- Temps : `12.5`, `"L3"`, `"L3+0.4"`, `"L3.end"`, `"L3.end+0.2"` (après la fin de la réplique), `"S2"`, `"total"`.
- Plans : `cap_y` (hauteur des sous-titres, 0,635 par défaut ; 0,705 sur un téléphone). `screen` collé sur le vrai téléphone (`quad`) : `type` `incoming` (name, label, status, battery), `lock` (time, status, battery, notif [expéditeur, texte]), `sms` (sender, status, battery, time, lines [[temps, texte], …] qui arrivent une à une) ; `steps` [[temps, {champs}]] change l'écran en cours de plan.
- Carte de fin `end` : `swap: true` = bouton 1 rouge et bouton 2 vert (quand le 2 est le geste « sûr », comme décrocher).
- `music`, `impacts` (`shake`, `punch`, `flash`), `hud` (bandeau, `clock` [[temps, "03:12"]…], `battery` [[temps, %]…], rouge à 5 % et moins), `cover` (file, title, episode, subtitle, y, screen).
