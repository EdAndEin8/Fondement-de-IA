# Séance 3 — Raisonnement, information partielle, campagne : notes techniques

Mardi 10 novembre 2026, 14h–17h. Résumé des choix des Parties II, IV et V et des résultats obtenus.

## 1. Organisation du code

| Fichier | Contenu |
|---|---|
| `raisonnement/faits.py` | faits observés d'un état (`faits_de_etat`), affichage d'un fait |
| `raisonnement/moteur.py` | unification, règles, chaînage avant, `BaseConnaissances` |
| `partiel/vue.py` | vue locale d'un robot (`vue_locale`, `Observation`) |
| `partiel/memoire.py` | mémoire des observations, frontière, carte supposée, BFS sur les cases connues |
| `partiel/solo.py` | course d'un robot seul (adversaire immobile) |
| `agents/partiels.py` | `AgentExplorateur`, `AgentAlphaBetaOptimiste` |
| `experiences/information_partielle.py` | carte complète contre découverte progressive |
| `experiences/campagne.py` | tournoi entre agents et Min-Max contre Alpha-Bêta |

## 2. Partie II — Connaissances et raisonnement

- Un fait est un tuple `(prédicat, arg, ...)`. `faits_de_etat` ne produit que des faits **observés** ; les conclusions sont toujours **déduites**, et `BaseConnaissances` garde les deux ensembles séparés.
- 8 règles de Horn à variables (`?r`, `?c`, `?d`...) : `deplacement`, `ouverture`, `franchissement`, `ramassage`, `victoire`, `interdiction_porte`, `infranchissable_mur`, `infranchissable_occupee`.
- Pas de négation dans les prémisses : `libre` et `sans_cle` sont fournis comme faits positifs. Le chaînage avant est monotone, et son résultat ne dépend pas de l'ordre des règles.
- `expliquer(fait)` remonte l'arbre de dérivation jusqu'aux faits observés. C'est ce qui justifie une ouverture de porte avec clé, ou l'interdit sans clé (`uv run fondement-de-ia raisonner salle_fermee`).
- Test principal : les `deplacement_possible` déduits coïncident avec `actions_legales` sur 6 cartes × 12 états.

Une représentation propositionnelle demanderait une règle par robot et par couple de cases voisines : 208 règles `deplacement` sur `salle_fermee`, 1 272 sur le grand labyrinthe, à régénérer pour chaque carte. Avec des prédicats, il n'en faut qu'une seule.

## 3. Partie IV — Information partielle

### Vue et mémoire

- La vue d'un robot couvre les cases à distance de Manhattan au plus `rayon` (1 dans l'énoncé). Seules les dimensions du plateau sont supposées connues.
- `vue_locale` est le seul accès des agents partiels à l'état réel.
- La mémoire garde le dernier contenu vu de chaque case. Une clé ramassée ou une porte ouverte hors du champ n'est corrigée qu'à la prochaine observation.
- L'adversaire est supposé immobile à sa dernière position vue, tant qu'on ne voit pas sa case vide.

**Erreur corrigée en cours de séance.** Au début, l'adversaire n'était un obstacle que lorsqu'il était visible. En course solitaire sur `salle_fermee`, Bleu arrivait en (8, 1) à côté de Rouge, immobile en (8, 0) : la case de Rouge était la frontière la plus proche, mais elle était occupée, donc Bleu partait vers une autre frontière. Un pas plus loin, il ne voyait plus Rouge, la case redevenait atteignable et il revenait : allers-retours (8, 1) / (8, 2) jusqu'à la limite. Garder en mémoire la dernière position de l'adversaire, et la retirer des cibles, règle le problème. Toutes les courses arrivent maintenant à G (testé sur les 7 cartes, les deux robots et trois variantes).

### Stratégie

1. Si G est connue : A* optimiste (cases inconnues libres) sur la carte supposée, premier pas du plan.
2. Sinon : BFS vers la case de frontière la plus proche. Sans clé, les clés connues sont aussi des cibles.
3. Le plan est recalculé à chaque tour.

Variantes : `-r2` (rayon 2), `-g` (position de G donnée au départ). `optimiste-dN` joue Alpha-Bêta avec E+ sur le jeu supposé quand l'adversaire est visible et G connue (adversaire supposé sans clé).

### Résultats (`resultats/information_partielle.md`)

- Surcoût de 1 à 6 en nombre de pas par rapport à A* avec la carte complète, jamais moins (testé).
- Arène : le rayon compte beaucoup (46 pas avec un rayon de 1, 18 avec un rayon de 2).
- Labyrinthes : connaître G avec un plan optimiste **double** le trajet sur `labyrinthe_11x11` (44 pas au lieu de 24), car le plan traverse l'inconnu en ligne droite et mène dans des culs-de-sac.
- En partie : l'explorateur gagne 56 % de ses parties contre l'aléatoire et 12 % contre A* avec la carte complète. Avec un rayon de 1, l'adversaire n'est visible que collé au robot : Alpha-Bêta sert pour 8 % des décisions au plus.

## 4. Partie V — Campagne d'évaluation

- 5 agents à profondeur 4, 6 cartes (sans le 25 × 25), 4 configurations par paire (couleurs et premier joueur inversés), graines 0 à 9 contre l'aléatoire : 1 104 parties, 16 s.
- Le premier joueur gagne 81 % des parties entre agents déterministes. Les défaites du premier joueur ont toutes lieu sur `couloir_5x5`, où Rouge est plus près de G (4 pas contre 6).
- A* fait jeu égal avec les agents adversariaux (12 victoires sur 24) : la course domine sur nos cartes.
- Alpha-Bêta économise 39 à 77 % des nœuds à d = 4, et 64 à 93 % à d = 6 (arène, d = 6 : 2 408 nœuds contre 164, 35,6 ms contre 7,7 ms). À d = 2, il est un peu plus lent à cause du tri.

Décisions surprenantes :

1. `salle_fermee` avec E : 20 nuls sur 20 contre l'aléatoire (effet d'horizon de la séance 2). E+ gagne 75 % des parties sur cette carte.
2. `couloir_5x5`, Alpha-Bêta E+ en Bleu : 16 défaites sur 20 contre l'aléatoire. E+ juge la course perdue (Rouge plus près), la valeur ne dépend plus de la position de Bleu, et Bleu oscille S, N, S, N... Avec E (terme `dR − dB`), seulement 3 défaites. Piste : un petit terme de distance propre dans E+.
3. Min-Max (ordre naturel) fait 5 nuls sur 20 dans l'arène en Rouge, à cause d'allers-retours entre coups ex æquo ; Alpha-Bêta trié n'en fait aucun.
