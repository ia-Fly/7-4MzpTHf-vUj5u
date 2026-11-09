# Scripts prêts — BLACK-OUT, nuit 2 (écrits le 09/11/2026)

La nuit 2 dépend du vote de la nuit 1 (`state.json > votes.blackout_n1.result`, donné par Matis) : **1 · OUVRIR**, **2 · DÉCROCHER**, ou résultat inconnu → **DEUX CHEMINS**. Ne jamais choisir une branche « au jugé ».
Procédure et recette : `../README.md` ; voix, images et continuité : `README.md`. Texte à envoyer tel quel à `eleven_v4` (`language_code` `fr`) : une prise par personnage, `[pause]` entre chaque réplique ; `text` des répliques dans `episode.json` = la même chose sans balises.
HUD : `BLACK-OUT · NUIT 2`, l'heure repart de 03:13 et la batterie de 2 %. Fin : carte 1 / 2 (`swap` si le 2 est le choix « prudent », comme la nuit 1), `cta2` `LE PLUS VOTÉ = LA NUIT 3 · ABONNE-TOI`.

## Nuit 2 · si 1 · OUVRIR a gagné — « ELLE EST CHEZ TOI » (environ 55 s)
**Idée :** tu as ouvert, elle est entrée ; tout est presque normal, sauf des détails impossibles. Nouvelle règle : ne jamais lui dire ton prénom.

- **Narrateur** (French John) : `Tu as ouvert la porte. [pause] Et maintenant... elle est chez toi. [pause] Elle enlève son manteau. [pause] Il est sec. [pause] Dehors, il pleut depuis deux heures. [pause] Elle traverse le salon. Sans allumer. [pause] Elle ne se cogne à rien. [pause] [slowly] Elle n'est jamais venue ici. [pause] Ton téléphone vibre. 1 %. [pause] Numéro inconnu. [pause] Elle va te demander ton prénom. [pause] Ne le dis jamais. [pause] [slowly] C'est ta mère. Elle devrait le connaître. [pause] Alors... tu mens ? [pause] Ou tu te tais ? [pause] Écris 1 ou 2 en commentaire. [pause] Le choix le plus voté décidera de la nuit 3.`
- **« Maman »** (Isabelle, dans la pièce : `lo` 120, `hi` 6000, sous-titres bleu glacé) : `[softly] Tu ne m'embrasses pas, mon cœur ? [pause] [sweetly] Mon cœur... rappelle-moi ton prénom ?` — 1re réplique après « Elle n'est jamais venue ici », 2e après « Ne le dis jamais ».
- **Écrans :** `sms` (« Numéro inconnu » : « Elle va te demander ton prénom. » puis « Ne le dis jamais. »), batterie 1 %.
- **Images :** à générer — manteau beige accroché dans l'entrée sombre, parfaitement sec, à côté d'une fenêtre qui ruisselle · salon dans le noir, une femme assise très droite sur le canapé, vue de dos, face à la fenêtre (animé : la tête tourne lentement, le visage reste dans l'ombre ; partir de E.png pour la coiffure et le manteau). Réutiliser : A.png (porte, couloir), C.png (SMS), F.png (la vraie photo : « elle devrait le connaître »), D.png.
- **Fin :** 1 · MENTIR / 2 · SE TAIRE. Heure 03:13 → 03:21.
- **Sons en banque :** rain, heart, buzz, boom, riser, whoosh. **À générer :** pas lents sur un parquet, froissement de manteau.

## Nuit 2 · si 2 · DÉCROCHER a gagné — « LA MÊME VOIX » (environ 60 s)
**Idée :** au téléphone, ta vraie mère, réveillée ; derrière la porte, la même voix répète chaque mot, une seconde après. Ta mère avoue avoir envoyé le message de minuit. La chose a entendu ta voix.

- **Narrateur** : `Tu as décroché. [pause] Tu as dit : « Allô ? » [pause] C'est sa voix. Au téléphone. [pause] Et derrière ta porte... [pause] La même voix. Les mêmes mots. [pause] Elle répète tout. Une seconde après. [pause] Le message de minuit. [pause] La ligne coupe. 1 %. [pause] Silence. [pause] [slowly] Derrière ta porte... quelqu'un parle avec ta voix. [pause] Alors... tu rappelles ta mère ? [pause] Ou tu ne dis plus un mot jusqu'à l'aube ? [pause] Écris 1 ou 2 en commentaire. [pause] Le choix le plus voté décidera de la nuit 3.`
- **Ta mère au téléphone** (Isabelle, `phone: true`) : `[sleepy] Mon cœur ? Il est trois heures du matin... [pause] Tu m'entends ? Pourquoi tu ne dis rien ? [pause] [whispers] Écoute-moi. C'est moi qui t'ai envoyé le message. [pause] [whispers] Ne lui parle pas. S'il entend ta voix... il la garde.`
- **La porte** (même prise qu'au téléphone, pour un écho parfait : copier le fichier de la mère en `voice_m.mp3`, mêmes répliques, `skip: true` sur celles que la porte ne répète pas ; filtre porte `lo` 200, `hi` 2800, placées 1 s après l'original) : répète « Mon cœur ? Il est trois heures du matin… » et « Pourquoi tu ne dis rien ? ».
- **Ta voix** (une voix jeune et neutre de la bibliothèque, filtre porte) : `Allô ?`, juste avant « Derrière ta porte… quelqu'un parle avec ta voix ».
- **Écrans :** appel en cours « Maman », durée qui défile, « Pas de service » ; puis fin d'appel, batterie 1 %.
- **Images :** réutiliser C.png (appel), A.png et G.png/VG.mp4 (porte, poignée), E.png (« elle répète tout »), F.png (la vraie mère). À générer : le judas vu de l'intérieur en très gros plan, noir derrière.
- **Fin :** 1 · RAPPELER / 2 · SE TAIRE. Heure 03:13 → 03:16.
- **Sons en banque :** rain, heart, boom, riser, whoosh. **À générer :** tonalité de fin d'appel (bip bip bip).

## Nuit 2 · vote inconnu — « DEUX CHEMINS » (environ 55 s)
**Idée :** sans résultat de vote, on ne prétend rien : on montre les deux suites en 20 s, elles se rejoignent, et la nuit repart sur un nouveau choix. Légende : `Ouvrir ou décrocher : voici les deux chemins.` (jamais « vous avez choisi »).

- **Narrateur** : `Trois heures treize. Ta mère frappe. Ton téléphone sonne. [pause] Si tu as ouvert... [pause] Le couloir est vide. [pause] Mais sur le paillasson... des traces mouillées. [pause] Elles entrent chez toi. [pause] Si tu as décroché... [pause] Derrière ta porte, la même voix répète chaque mot. [pause] Dans les deux cas, à trois heures quatorze... un deuxième message. [pause] Numéro inconnu. [pause] « Il ne voit que dans le noir. » [pause] Ta seule lumière : la lampe de ton téléphone. [pause] Batterie : 1 %. [pause] Alors... tu allumes ? [pause] Ou tu attends l'aube dans le noir ? [pause] Écris 1 ou 2 en commentaire. [pause] Le choix le plus voté décidera de la nuit 3.`
- **« Maman »** : au téléphone (`phone: true`) `[sleepy] Allô ? Mon cœur ?`, puis la même réplique derrière la porte (filtre porte), 1 s après.
- **Écrans :** appel en cours (branche « décroché ») ; `sms` du numéro inconnu (« Il ne voit que dans le noir. ») ; batterie 1 %.
- **Images :** à générer — porte ouverte sur un couloir d'immeuble vide et sombre · paillasson avec des traces de pas mouillées qui entrent. Réutiliser : A.png, C.png, E.png, G.png.
- **Fin :** 1 · ALLUMER / 2 · ATTENDRE. Heure 03:13 → 03:15.
- **Sons en banque :** rain, heart, buzz, boom, riser, whoosh, knock.

---

## Archives — séries anglaises arrêtées le 09/11/2026 (ne plus publier)

### OMERTÀ · Épisode 4 · THE ENVELOPE (A — vote de l'ép. 3 : DELIVER)
**Idée :** l'enveloppe te livre toi-même. Environ 30 s, choix posé vers 26 s.

- **Narrateur** (Ra McQueen) : `You voted: deliver. [pause] You don't open it. [pause] Fourteen Mill Street. Midnight. [pause] A woman opens the door. [pause] You know that face. [pause] It's the baker. [pause] [slowly] The bakery you burned. [pause] She tears the envelope. [pause] Inside, a photo. You, in front of the fire. [pause] On the back, his handwriting. [pause] [nervous] He's yours now. [pause] On her table, two cups of coffee. [pause] She was expecting you. [pause] [slowly] Do you stay... or run?`
- **La boulangère** (Charmion `lUCNYQh2kqW2wiie85Qk`, voix grave et calme) : `[calmly] Come in. [pause] Close the door.`, placée juste avant « On her table ».
- **Plans :** enveloppe scellée à la main sous un réverbère, pluie (animé) · numéro 14 sur une porte · silhouette de femme à contre-jour, visage dans l'ombre (animé) · mains qui déchirent l'enveloppe (animé) · polaroïd d'un homme de dos devant un incendie, sans flamme sur une personne · écriture au dos, ajoutée en code · deux tasses qui fument sur une table de cuisine (animé).
- **Fin :** STAY / RUN. Bandeau : `OMERTÀ  |  EP. 4` et heure `11:58 PM` → `00:00 AM`.
- **Sons en banque :** rain, heart, boom, riser, door. **À générer :** déchirure de papier.

### NIGHT DISPATCH · Épisode 1 · THE ORDER (C) — publié le 07/11
- **Narrateur** : `You answer emergency calls at night. [pause] 2:40 a.m. Line four. [pause] A woman is whispering. [pause] [slowly] She wants to order a pizza. [pause] You almost hang up. [pause] Then you hear it. [pause] She's scared. [pause] You ask for her address. [pause] You type it. [pause] [nervous] You know this address. [pause] It's your house. [pause] You live alone. [pause] [slowly] Do you send a patrol... or stay on the line?`
- **L'appelante** (voix féminine, filtre `phone`) : `[whispers] Hi. I'd like to order a large pizza. [pause] [whispers] Please. Don't hang up. [pause] [whispers] Forty-one Alder Road. [pause] [whispers] He just came back upstairs.`

### THE OFFER · Épisode 1 · TEN MILLION (D)
- **Narrateur** : `A stranger sits across from you. [pause] He slides a briefcase over the table. [pause] Ten million dollars. Yours, tonight. [pause] No tax. No police. No catch. [pause] Just one condition.`
- **L'homme** (Obsidian `acrqYoDVmcpJemOxjC39`, calme) : `[calmly] Somewhere, someone you have never met loses everything. [pause] Their house. Their work. Their family. [pause] They will never know why. [pause] And you will never know who. [long pause] You have ten seconds.`
- **Fin :** TAKE / WALK.

### COLD FILE · Dossier 1 · ROOM 409 (E)
- **Narrateur** (Danny `0wg6fPA7PA9n5PKb8N2e`) : `Room 409. Locked from the inside. [pause] The man in the chair has been dead for an hour. [pause] Three people saw him last night. [pause] [slowly] One of them is lying. [pause] A. The maid. [pause] B. His wife. [pause] C. His business partner. [pause] One last thing. [pause] The parking camera, at ten p.m. [pause] Look closely. [pause] [slowly] Who's lying?`
- **Dépositions** : la femme de chambre `I brought his dinner at nine. He was on the phone.` · l'épouse `I was asleep. I never left our room.` · l'associé `I left at ten. It was pouring. I ran to my car.` Solution : l'associé, car le sol est sec.
