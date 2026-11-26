# Fun fact 04 — l'effet du témoin (26/11/2026, programmé 19:00 Paris, Metricool post 443082833)
- Source : Darley & Latané (1968), Journal of Personality and Social Psychology 8(4), 377-383, doi 10.1037/h0025589.
  Crise simulée entendue à l'interphone ; alerte donnée avant la fin de la crise : 85 % quand le participant se croit seul témoin, 31 % quand il croit 4 autres témoins présents.
  (PDF original illisible depuis l'agent web ; chiffres recoupés via simplypsychology.org et arabpsychology.com, qui citent le tableau de l'article.)
- ElevenLabs (compte gratuit, flow sZ47DJT1AJLU0Z3F5ckL) : voix 441 crédits (gen kzjQIY5Mua7gQYuev6gS, 25,4 s),
  musique 32 s 900 crédits (gen WntpYopDD9YBNv6HVlVX, réutilisable ; 1er essai « Free generations are busy », non facturé, 2e essai OK).
  Bruitages de la banque (0 crédit, flow x6xdsbzCDw113q2iTovj) : impact-manga, sceau-magique, swirl ; le reste synthétisé dans mix.py.
- Voix étirée à 27,8 s (CUTS dans mix.py). Musique -30 dBFS RMS avant ducking 80 % (≈ -36 après), -14,0 LUFS.
- ASR : tools/asr_check.py (Whisper base) plafonne à 0,84 sur la VOIX SEULE (entend « 1978 », « chaque impense », avale « pointe ») et donne 0,79 sur le mp4
  (dont un doublon à la jonction des tranches de 25 s). Contre-vérification Whisper small (même outil, modèle small) : 1,00 sur le mp4 final.
  Le mix n'est donc pas en cause ; la limite vient du modèle base.
- Couverture = image à 0,5 s. Légende : appel à l'action « enregistre ». 1er commentaire = la source.
