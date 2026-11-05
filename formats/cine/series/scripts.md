# Scripts prêts — prochains épisodes (écrits le 05/11/2026)

À produire dans l'ordre de la rotation, après CALLER ID ép. 1 (recette et procédure : `../README.md`). Texte à envoyer tel quel à `eleven_v4` : une seule prise par personnage, `[pause]` entre chaque réplique.
Vérifier avant de produire : un vote noté dans `state.json > votes` a pu changer la suite. Voix à confirmer avec `creative_list_voices`.

## OMERTÀ · Épisode 4 · THE ENVELOPE (A — vote de l'ép. 3 : DELIVER)
**Idée :** l'enveloppe te livre toi-même. Environ 30 s, choix posé vers 26 s.

- **Narrateur** (Ra McQueen) : `You voted: deliver. [pause] You don't open it. [pause] Fourteen Mill Street. Midnight. [pause] A woman opens the door. [pause] You know that face. [pause] It's the baker. [pause] [slowly] The bakery you burned. [pause] She tears the envelope. [pause] Inside, a photo. You, in front of the fire. [pause] On the back, his handwriting. [pause] [nervous] He's yours now. [pause] On her table, two cups of coffee. [pause] She was expecting you. [pause] [slowly] Do you stay... or run?`
- **La boulangère** (Charmion `lUCNYQh2kqW2wiie85Qk`, voix grave et calme) : `[calmly] Come in. [pause] Close the door.`, placée juste avant « On her table ».
- **Plans :** enveloppe scellée à la main sous un réverbère, pluie (animé) · numéro 14 sur une porte · silhouette de femme à contre-jour, visage dans l'ombre (animé) · mains qui déchirent l'enveloppe (animé) · polaroïd d'un homme de dos devant un incendie, sans flamme sur une personne · écriture au dos, ajoutée en code · deux tasses qui fument sur une table de cuisine (animé).
- **Fin :** STAY / RUN. Bandeau : `OMERTÀ  |  EP. 4` et heure `11:58 PM` → `00:00 AM`.
- **Sons en banque :** rain, heart, boom, riser, door. **À générer :** déchirure de papier.

## NIGHT DISPATCH · Épisode 1 · THE ORDER (C)
**Idée :** un appel d'urgence déguisé en commande, puis l'adresse est la tienne. Environ 32 s.

- **Narrateur** : `You answer emergency calls at night. [pause] 2:40 a.m. Line four. [pause] A woman is whispering. [pause] [slowly] She wants to order a pizza. [pause] You almost hang up. [pause] Then you hear it. [pause] She's scared. [pause] You ask for her address. [pause] You type it. [pause] [nervous] You know this address. [pause] It's your house. [pause] You live alone. [pause] [slowly] Do you send a patrol... or stay on the line?`
- **L'appelante** (voix féminine, filtre `phone`) : `[whispers] Hi. I'd like to order a large pizza. [pause] [whispers] Please. Don't hang up. [pause] [whispers] Forty-one Alder Road. [pause] [whispers] He just came back upstairs.`
- **Plans :** salle de console sombre, un casque, écrans flous (animé) · console d'appel en code (ligne 4, durée, onde) · mains sur un clavier (animé) · adresse tapée lettre par lettre en code, passe au rouge avec `MATCH: EMPLOYEE HOME ADDRESS` · photo de ta maison, de nuit, une fenêtre allumée à l'étage (animé).
- **Fin :** SEND / STAY. **À ajouter à `ui.py` :** la console d'appel.
- **Sons en banque :** breath, boom, riser, heart. **À générer :** ambiance de centre d'appels, frappe au clavier. Aucun nom de vrai service d'urgence, adresse fictive.

## THE OFFER · Épisode 1 · TEN MILLION (D)
**Idée :** dilemme pur, très court. Environ 24 s. Le résultat du vote ouvre l'épisode suivant.

- **Narrateur** : `A stranger sits across from you. [pause] He slides a briefcase over the table. [pause] Ten million dollars. Yours, tonight. [pause] No tax. No police. No catch. [pause] Just one condition.`
- **L'homme** (Obsidian `acrqYoDVmcpJemOxjC39`, calme) : `[calmly] Somewhere, someone you have never met loses everything. [pause] Their house. Their work. Their family. [pause] They will never know why. [pause] And you will never know who. [long pause] You have ten seconds.`
- **Plans :** table de restaurant vide, deux verres, costume sombre sans visage (animé) · mallette qui glisse (animé) · mallette ouverte, liasses · chaise vide et lumière d'une maison lointaine · compte à rebours de 10 s en code.
- **Fin :** TAKE / WALK. Légende : `Be honest. Would you take it?`
- **Sons en banque :** heart, riser, boom. **À générer :** mallette qui glisse, déclic de serrure.

## COLD FILE · Dossier 1 · ROOM 409 (E)
**Idée :** une énigme qu'on doit revoir pour résoudre, ce qui fait monter le temps regardé. Environ 38 s. La solution est l'épisode suivant.

- **Narrateur** (Danny `0wg6fPA7PA9n5PKb8N2e`) : `Room 409. Locked from the inside. [pause] The man in the chair has been dead for an hour. [pause] Three people saw him last night. [pause] [slowly] One of them is lying. [pause] A. The maid. [pause] B. His wife. [pause] C. His business partner. [pause] One last thing. [pause] The parking camera, at ten p.m. [pause] Look closely. [pause] [slowly] Who's lying?`
- **Dépositions** (une voix par personne, à l'écran en même temps) : la femme de chambre `I brought his dinner at nine. He was on the phone.` · l'épouse `I was asleep. I never left our room.` · l'associé `I left at ten. It was pouring. I ran to my car.`
- **Plans :** porte 409 avec chaîne de sécurité (animé) · fauteuil vu de dos, main posée sur l'accoudoir, jamais de corps en gros plan · 3 fiches de suspect en code (A, B, C) · image de caméra de parking en noir et blanc, sol **sec**, horodatage `22:04` ajouté en code (animé). L'indice n'est jamais dit à voix haute.
- **Fin :** A / B / C (à ajouter à la carte de fin de `ui.py`). Solution, épisode 2 : l'associé, car le sol est sec.
- **Sons en banque :** boom, riser, door. **À générer :** ambiance de couloir d'hôtel.
