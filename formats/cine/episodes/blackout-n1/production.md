# BLACK-OUT · Nuit 1 — production (09/11/2026)

- **Flow ElevenLabs :** `svWwFUy11l9jmpeQIqYZ` (images, plans, voix et sons de la série : à réutiliser, liste dans `../../series/README.md`).
- **Durée :** 57,1 s · -14,2 LUFS · `check_video` : VERDICT OK · `asr_check --lang fr` : 0,91 sur le mix (0,92 sur la voix seule).
- **Fin :** 1 · OUVRIR / 2 · DÉCROCHER (vote → nuit 2, suites dans `../../series/scripts.md`).

## Crédits (9 086, registre `elevenlabs/ledger.jsonl`)
| Poste | Détail | Crédits |
|---|---|---|
| Essais de voix | Kevan, French John, Bass (153 chacun) — Matis a choisi French John | 459 |
| Voix | narration French John 899 · la mère, Isabelle 134 | 1 033 |
| Images | 7 × Seedream 5 Lite 2K (A à G) | 1 485 |
| Plans animés | 5 × Veo 3.1 Lite 4 s 1080p sans son (VA raté, VA2, VB, VE, VG) | 6 060 |
| Bruitages neufs | knock, powerdown, shout, handle | 50 |
| Musique et autres sons | banque (score-tension, rain, heart, buzz, boom, riser, whoosh) | 0 |

## Ce qui a été corrigé au montage
- `VA.mp4` raté (la porte s'ouvre, une silhouette apparaît) → `VA2.mp4`, prompt négatif strict et image de fin = A ; une silhouette passe encore de 0,4 à 1,7 s → `offset` 2,0, `speed` 0,33.
- `VE.mp4` recule après 3 s → `speed` 0,52.
- Écran verrouillé sans date (épisodes intemporels) ; carte de fin : OUVRIR en rouge, DÉCROCHER en vert (comme le bouton vert du téléphone).
- 1er rendu : Whisper entendait « Ta mère **fera pas** ta porte » (les coups frappés tombaient sur la phrase) alors que la voix seule était bien comprise. Corrigé : `lead` 0,55 s (deux coups avant la voix), deux coups dans le silence après la réplique (`L1.end+0.05`, `offset` 2,45), coups de la 2e scène après « On frappe » (`L15.end-0.1`), effets baissés de 6 dB sous la voix (`fx_duck_db`), coupure de courant à -6 dB. Score du mix : 0,78 → 0,91.
- Limites connues du contrôle : Whisper base entend « s'est un » pour « s'éteint », « tu es » pour « tu aimes » et « six froid » pour « si froid », y compris sur les voix seules ; les sous-titres les affichent correctement.
