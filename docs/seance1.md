# Séance 1 — Simulateur et recherche : notes techniques

Résumé de ce qui a été fait pendant la première séance et des choix retenus.

## 1. Modélisation du jeu

**Carte et état séparés.** La carte (`Carte`) contient ce qui ne change jamais : dimensions, murs, portes et clés initiales, balise, départs. L'état (`Etat`) contient exactement le n-uplet de l'énoncé `s = (PB, PR, j, KB, KR, Ksol, Douvert, t, p)`. Séparer les deux garde les états petits, ce qui compte quand la recherche en mémorise des milliers.

**Immuabilité.** `Etat` est une `dataclass(frozen=True, slots=True)` dont les ensembles sont des `frozenset`. Conséquences :
- `transition` ne peut pas modifier l'état d'origine : elle renvoie une copie (`dataclasses.replace`) ;
- l'état est hashable : on peut le mettre dans un `set` ou s'en servir comme clé de `dict`, comme l'exige l'énoncé (ensembles d'états explorés, plus tard tables de transposition).

**Une seule source de vérité pour les règles.** La fonction `regles.deplacement` applique R2–R5 à un robot isolé. Elle est utilisée à la fois par le jeu à deux joueurs (`Jeu`) et par le problème de recherche mono-agent : impossible d'avoir des règles qui divergent entre la simulation et la planification.

**Points de règle à savoir justifier :**
- R4 : un robot qui a déjà une clé passe sur une autre clé sans la ramasser ; elle reste au sol.
- R5 : entrer sur une porte fermée consomme la clé ; la porte reste ouverte pour les deux robots.
- R6 : la victoire est testée avant les nuls ; un coup gagnant au 80ᵉ tour est une victoire.
- R7 : `PASSER` n'est légal que si aucun déplacement ne l'est ; tout déplacement remet le compteur de passes à zéro.
- `actions_legales` renvoie une liste vide dans un état terminal.

**Tests.** `tests/test_regles.py` contient un test par règle (murs, collisions, clés, une seule clé par robot, porte sans clé, ouverture, porte partagée, victoire des deux couleurs, passes, limite de tours, immuabilité, hashabilité). Les petites cartes sont écrites directement dans les tests pour que chaque situation soit lisible.

## 2. Recherche (Partie I)

**État de recherche.** `EtatRecherche = (position, clé, clés au sol, portes ouvertes)`. La position seule ne suffit pas : sur `porte_raccourci`, la case (3, 0) n'a pas le même avenir avec ou sans clé. L'adversaire est un obstacle fixe.

**Algorithmes** (tous en recherche en graphe) :

| Algorithme | Frontière | Test de but | Optimal (coût unitaire) |
|---|---|---|---|
| BFS | file FIFO | à la génération | oui |
| DFS | pile | au retrait | non |
| UCS | tas sur g | au retrait | oui |
| A* | tas sur f = g + h | au retrait | oui si h admissible |

Remarque : à coût unitaire, UCS développe les mêmes niveaux que BFS ; il développe un peu plus de nœuds car il teste le but au retrait (indispensable pour l'optimalité quand les coûts varient).

**Heuristiques** (toutes admissibles et cohérentes, obtenues par relaxation) :
1. `manhattan` : ignore murs, portes et adversaire (heuristique de l'énoncé).
2. `relaxee` : distance exacte sur la carte où toutes les portes seraient ouvertes (BFS précalculé depuis G). Garde les murs.
3. `cles` : comme `relaxee`, mais si toute route vers G traverse une porte fermée et que le robot n'a pas de clé, impose le détour par la meilleure clé : `min_k d(pos, k) + d(k, G)`.

L'admissibilité est **vérifiée par un test** : pour chaque état atteignable de chaque carte, `h(s) ≤ h*(s)` où `h*` est calculé par BFS.

## 3. Résultats (extrait de `resultats/recherche.md`)

Nœuds développés pour Bleu :

| Carte | BFS | UCS | DFS (longueur) | A* Manhattan | A* relaxée | A* clés | Longueur optimale |
|---|---|---|---|---|---|---|---|
| exemple_7x7 | 12 | 17 | 21 (20) | 6 | 6 | 6 | 6 |
| porte_raccourci | 19 | 24 | 13 (13) | 10 | 7 | 7 | 7 |
| salle_fermee | 44 | 46 | 40 (21) | 41 | 35 | 21 | 21 |
| labyrinthe_11x11 | 62 | 70 | 74 (54) | 34 | 22 | 22 | 22 |
| grand_labyrinthe_25x25 | 430 | 443 | 142 (100) | 349 | 209 | 62 | 62 |

À commenter :
- DFS développe parfois peu de nœuds, mais renvoie des chemins bien trop longs : 20 coups au lieu de 6 sur `exemple_7x7`, et 33 au lieu de 7 pour Rouge sur `porte_raccourci`.
- Manhattan est peu informée dans un labyrinthe : les murs imposent de gros détours qu'elle ignore.
- Sur les cartes où la balise est enfermée derrière une porte (`salle_fermee`, `grand_labyrinthe`), seule l'heuristique « clés » tient compte du détour obligatoire ; A* ne développe alors que les nœuds du chemin optimal.
- Les temps sont de l'ordre de la milliseconde : sur ces tailles, le coût de construction de l'heuristique (BFS précalculés) n'est pas négligeable. Le nombre de nœuds est donc la mesure la plus fiable.

## 4. Pourquoi le plus court chemin devient sous-optimal en partie

Démonstration : `uv run python experiences/plan_fige.py salle_fermee` (sortie dans `resultats/plan_fige.txt`).

Sur `salle_fermee`, les deux robots sont à 4 cases de l'unique clé et calculent chacun un plan de 21 coups qui commence par aller la chercher. Bleu joue en premier : il prend la clé au tour 6. Au tour 7, l'action prévue par Rouge l'enverrait sur la case de Bleu ; le plan figé est caduc, et de toute façon la clé a disparu.

Raisons générales :
1. le plan suppose l'adversaire immobile, alors qu'il bouge et peut bloquer un couloir (R3) ;
2. les ressources sont partagées : une clé ramassée par l'autre disparaît (R4), une porte qu'il ouvre crée un raccourci pour les deux (R5) ;
3. c'est une course : le plus court chemin pour soi n'est pas le coup qui maximise ses chances de gagner. Parfois il vaut mieux gêner l'adversaire ou lui prendre la clé, même au prix d'un détour (section 1.4 de l'énoncé).

Replanifier à chaque tour (agent A*) corrige le point 1 en partie, mais pas les points 2 et 3 : il faut anticiper les réponses de l'adversaire, ce qui motive Min-Max (séance 2).
