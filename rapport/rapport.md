# La course à la balise — rapport technique

*Anton Dion, Matthieu Meunier, Sean Persand — 4e année du cycle FISA ICy, INSA Hauts-de-France, 2026–2027*

> Rapport de groupe (6 à 10 pages). Les sections marquées « à rédiger » seront complétées au fil des séances.

## 1. Introduction

Deux robots, Bleu et Rouge, se disputent une balise G sur un plateau quadrillé. Des murs bloquent le passage, des portes verrouillées ne s'ouvrent qu'avec une clé, et une clé ramassée disparaît du plateau. Le premier robot qui entre sur G gagne ; la partie est nulle après 80 tours ou après deux passes consécutives. Le jeu est à deux joueurs, à somme nulle, déterministe et, dans sa version de référence, à information complète.

Le projet construit pas à pas des agents de plus en plus élaborés pour ce jeu :

- un simulateur fidèle aux règles R1 à R8, testé règle par règle (section 2) ;
- des agents de recherche qui ignorent l'adversaire : BFS, UCS, DFS et A* avec trois heuristiques (section 3, Partie I) ;
- une base de connaissances avec chaînage avant, qui justifie ou interdit une action (section 4, Partie II) ;
- des agents adversariaux : Min-Max, Alpha-Bêta, approfondissement itératif, avec deux fonctions d'évaluation (section 5, Partie III) ;
- un mode à information partielle, où chaque robot ne voit que les cases voisines et découvre la carte (section 6, Partie IV) ;
- une campagne d'évaluation de 1 104 parties entre cinq agents (section 7, Partie V).

Le code est écrit en Python 3.14 avec la seule bibliothèque standard ; les algorithmes sont tous implémentés par le groupe. Le projet est géré avec `uv`, et les 190 tests passent avec `uv run pytest`. Toutes les expériences sont reproductibles : les graines sont fixées et les scripts de `experiences/` écrivent leurs résultats dans `resultats/`.

## 2. Modélisation et simulateur

### 2.1 Carte et état

La **carte** (`carte.py`) regroupe tout ce qui ne change jamais : dimensions, murs, portes et clés initiales, balise, cases de départ. Elle se lit depuis un fichier texte (une ligne par rangée, `#` mur, `.` libre, `B`, `R`, `K` clé, `D` porte, `G` balise). L'**état** (`etat.py`) est exactement le n-uplet de l'énoncé, `s = (PB, PR, j, KB, KR, Ksol, Douvert, t, p)`.

L'état est une `dataclass` gelée dont les ensembles sont des `frozenset` :

- `transition` ne peut pas modifier l'état d'entrée : elle renvoie une copie ;
- l'état est hashable : il sert d'élément d'ensemble ou de clé de dictionnaire, comme l'exige l'énoncé pour les ensembles d'états explorés.

Séparer la carte de l'état garde les états petits, ce qui compte quand une recherche en mémorise des milliers.

### 2.2 Règles

Les règles R1 à R8 sont centralisées dans `regles.py`. La fonction `deplacement` applique R2 à R5 à un robot isolé ; elle sert à la fois au jeu à deux joueurs (classe `Jeu`) et aux problèmes de recherche de la Partie I. Les règles ne peuvent donc pas diverger entre la simulation et la planification. La classe `Jeu` fournit les opérations demandées : `actions_legales`, `transition`, `terminal`, `utilite`. La fonction `jouer(agent_bleu, agent_rouge, carte, graine)` (`jeu.py`) simule une partie et mesure le temps de chaque décision, séparément du temps d'affichage.

Points de règle retenus : un robot qui possède déjà une clé passe sur une autre sans la ramasser (R4) ; ouvrir une porte consomme la clé et la porte reste ouverte pour les deux robots (R5) ; la victoire est testée avant les nuls, donc un coup gagnant au 80e tour reste une victoire (R6, R8) ; `PASSER` n'est légal que si aucun déplacement ne l'est (R7). Le joueur qui commence est un paramètre, ce qui permet d'inverser l'ordre dans la campagne d'évaluation.

### 2.3 Cartes

| Carte | Taille | Rôle |
|---|---|---|
| `couloir_5x5` | 5 × 5 | petite carte sans clé ni porte ; Rouge est à 4 pas de G, Bleu à 6 |
| `exemple_7x7` | 7 × 7 | plateau de la figure 1 de l'énoncé |
| `porte_raccourci` | 9 × 7 | une porte offre un raccourci de 7 pas au lieu de 13 |
| `salle_fermee` | 9 × 7 | G enfermée derrière une porte, une seule clé pour deux robots |
| `arene_9x9` | 9 × 9 | salle ouverte, symétrique, jusqu'à 4 coups par robot |
| `labyrinthe_11x11` | 11 × 11 | labyrinthe symétrique par rapport au centre |
| `grand_labyrinthe_25x25` | 25 × 25 | labyrinthe généré (`outils/generer_labyrinthe.py`, graine 27) |

Sur le grand labyrinthe, chaque robot a besoin de plus de 60 pas : la limite de 80 tours rend toute victoire impossible. Cette carte sert à la recherche (Partie I) et à l'exploration (Partie IV), pas aux confrontations.

### 2.4 Affichage, ligne de commande et tests

`afficher(etat, carte)` produit un plateau ASCII, en couleurs dans un terminal, et `jouer(..., animation=True)` l'anime en place. La commande `uv run fondement-de-ia` donne accès à tout le projet : `afficher`, `chemin`, `jouer`, `decider`, `raisonner`, `decouvrir`.

`tests/test_regles.py` contient 25 tests, au moins un par règle : murs, collisions, ramassage des clés, une seule clé par robot, porte sans clé, ouverture, porte partagée, victoire des deux couleurs, passes, limite de tours, immuabilité et hashabilité de l'état. Chaque situation est une petite carte écrite dans le test, lisible d'un coup d'œil. Les tests de la Partie I vérifient aussi que, sur chaque carte fournie, chaque robot a un chemin vers G (`tests/test_recherche.py`).

## 3. Partie I — Recherche et planification

### 3.1 Formulation

L'adversaire est considéré comme un obstacle fixe à sa position actuelle, et chaque déplacement coûte 1. L'état de recherche est `(position, clé, clés au sol, portes ouvertes)` : la position seule ne suffit pas. Sur `porte_raccourci`, par exemple, la case (3, 0) n'a pas le même avenir selon que le robot a ramassé la clé ou non. Le problème (`recherche/probleme.py`) réutilise la fonction `deplacement` du simulateur.

### 3.2 Algorithmes et heuristiques

Les quatre algorithmes sont des recherches en graphe (`recherche/algorithmes.py`) :

| Algorithme | Frontière | Test de but | Optimal (coût unitaire) |
|---|---|---|---|
| BFS | file FIFO | à la génération | oui |
| DFS | pile | au retrait | non |
| UCS | tas sur g | au retrait | oui |
| A* | tas sur f = g + h | au retrait | oui si h est admissible |

Trois heuristiques sont obtenues en relâchant des contraintes, ce qui les rend admissibles et cohérentes :

1. `manhattan` : ignore murs, portes et adversaire (heuristique de l'énoncé) ;
2. `relaxee` : distance exacte sur la carte où toutes les portes seraient ouvertes (un BFS depuis G, précalculé) ;
3. `cles` : comme `relaxee`, mais si toute route vers G traverse une porte fermée et que le robot n'a pas de clé, elle impose le détour par la meilleure clé, `min_k d(pos, k) + d(k, G)`.

L'admissibilité est vérifiée par un test : pour tout état atteignable de chaque carte, `h(s) ≤ h*(s)`, où `h*` est calculé par BFS.

### 3.3 Résultats

Tableau complet, avec les nœuds générés, la taille maximale de la frontière, le temps et le pic mémoire : `resultats/recherche.md` (`experiences/comparaison_recherche.py`). Nœuds développés pour Bleu :

| Carte | BFS | UCS | DFS (longueur) | A* Manhattan | A* relaxée | A* clés | Longueur optimale |
|---|---|---|---|---|---|---|---|
| exemple_7x7 | 12 | 17 | 21 (20) | 6 | 6 | 6 | 6 |
| porte_raccourci | 19 | 24 | 13 (13) | 10 | 7 | 7 | 7 |
| salle_fermee | 44 | 46 | 40 (21) | 41 | 35 | 21 | 21 |
| labyrinthe_11x11 | 62 | 70 | 74 (54) | 34 | 22 | 22 | 22 |
| grand_labyrinthe_25x25 | 430 | 443 | 142 (100) | 349 | 209 | 62 | 62 |

- DFS développe parfois peu de nœuds, mais ses chemins sont bien trop longs : 20 coups au lieu de 6 sur `exemple_7x7`, 100 au lieu de 62 sur le grand labyrinthe.
- À coût unitaire, UCS développe les mêmes niveaux que BFS, avec un peu plus de nœuds car il teste le but au retrait.
- Manhattan est peu informée dans un labyrinthe : elle ignore les détours imposés par les murs.
- Quand la balise est enfermée derrière une porte (`salle_fermee`, grand labyrinthe), seule l'heuristique « clés » voit le détour obligatoire : A* ne développe alors que les nœuds du chemin optimal (62 contre 430 pour BFS).
- Les temps restent de l'ordre de la milliseconde (2,8 ms pour BFS sur le 25 × 25), et le pic mémoire sous 105 Kio. À cette échelle, le nombre de nœuds est la mesure la plus fiable : le coût de construction des heuristiques (BFS précalculés) n'est pas négligeable devant celui de la recherche.

### 3.4 Plus court chemin et vraie partie

`experiences/plan_fige.py salle_fermee` fait suivre à chaque robot son plan initial sans le recalculer. Les deux robots sont à 4 cases de l'unique clé, et leurs plans de 21 coups commencent tous deux par aller la chercher. Bleu joue en premier et la ramasse au tour 6. Au tour 7, l'action prévue par Rouge l'enverrait sur la case de Bleu : le plan est caduc, et de toute façon la clé a disparu.

Le plus court chemin calculé sans adversaire devient sous-optimal pour trois raisons :

1. l'adversaire bouge et peut bloquer un couloir (R3) ;
2. les ressources sont partagées : une clé ramassée par l'autre disparaît (R4), et une porte qu'il ouvre sert aux deux (R5) ;
3. c'est une course : le plus court chemin pour soi n'est pas toujours le coup qui maximise ses chances de gagner. Gêner l'adversaire ou lui prendre la clé peut valoir un détour.

L'agent A* qui replanifie à chaque tour corrige en partie le premier point (en partie, il gagne en 41 tours sur `salle_fermee` en commençant), mais pas les deux autres : il faut anticiper les réponses de l'adversaire, ce que font les agents de la Partie III.

## 4. Partie II — Connaissances et raisonnement

Code : `src/course_balise/raisonnement/` (`faits.py`, `moteur.py`), commande `uv run fondement-de-ia raisonner <carte>`, tests `tests/test_raisonnement.py`.

### 4.1 Base de faits

Un fait est un tuple immuable `(prédicat, arg1, ...)`, par exemple `("possede_cle", "bleu")` ou `("voisine", (2, 2), (2, 3))`. La fonction `faits_de_etat(carte, etat)` produit les **faits observés** d'un état, c'est-à-dire ce qu'on lit directement sur le plateau :

| Prédicat | Sens |
|---|---|
| `but(g)`, `trait(r)` | position de la balise, joueur qui a le trait |
| `position(r, c)`, `occupee(c)` | position d'un robot, case occupée par un robot |
| `possede_cle(r)`, `sans_cle(r)` | possession d'une clé |
| `mur(c)`, `cle(k)` | mur, clé au sol |
| `porte_fermee(d)`, `porte_ouverte(d)` | état d'une porte |
| `voisine(c, c')` | `c` et `c'` adjacentes et toutes deux hors mur |
| `libre(c)` | case praticable, inoccupée, et qui n'est pas une porte fermée |

Sur `salle_fermee` (9 × 7), l'état initial donne 174 faits observés, dont 104 faits `voisine`. Les conclusions (déplacement possible, coup gagnant, interdiction) ne sont jamais produites par `faits_de_etat` : elles sont **déduites**. La classe `BaseConnaissances` conserve séparément les deux ensembles (`faits_base` et `faits_deduits()`), et un test vérifie qu'ils sont disjoints.

### 4.2 Règles

Les règles sont des clauses de Horn à variables (préfixe `?`). Les schémas de l'énoncé ont été complétés par les conditions exactes qui les rendent conformes aux règles R1 à R8 : trait au robot, position du robot, adjacence, case libre.

| Règle | Si | Alors | Règle du jeu |
|---|---|---|---|
| `deplacement` | `trait(r) ∧ position(r, c) ∧ voisine(c, d) ∧ libre(d)` | `deplacement_possible(r, d)` | R2, R3 |
| `ouverture` | `trait(r) ∧ possede_cle(r) ∧ position(r, c) ∧ voisine(c, d) ∧ porte_fermee(d)` | `peut_ouvrir(r, d)` | R5 |
| `franchissement` | `peut_ouvrir(r, d)` | `deplacement_possible(r, d)` | R5 |
| `ramassage` | `trait(r) ∧ sans_cle(r) ∧ position(r, c) ∧ voisine(c, k) ∧ cle(k) ∧ libre(k)` | `peut_ramasser(r, k)` | R4 |
| `victoire` | `trait(r) ∧ position(r, c) ∧ voisine(c, g) ∧ but(g) ∧ libre(g)` | `coup_gagnant(r, g)` | R6 |
| `interdiction_porte` | `trait(r) ∧ sans_cle(r) ∧ position(r, c) ∧ voisine(c, d) ∧ porte_fermee(d)` | `interdit(r, d)` | R5 |
| `infranchissable_mur` | `mur(c)` | `infranchissable(c)` | R3 |
| `infranchissable_occupee` | `occupee(c)` | `infranchissable(c)` | R3 |

La règle `franchissement` utilise une conclusion d'une autre règle : il faut deux étapes de chaînage pour conclure qu'ouvrir une porte est un déplacement possible.

### 4.3 Chaînage avant

Le moteur (`moteur.py`) unifie chaque prémisse avec les faits de même prédicat (index par prédicat), instancie la conclusion et l'ajoute si elle est nouvelle, en notant sa **dérivation** : la règle utilisée et les prémisses instanciées. On recommence jusqu'à ce qu'aucune règle ne produise de fait nouveau (point fixe). Comme les règles ne contiennent aucune négation, l'inférence est monotone : le résultat ne dépend pas de l'ordre d'application des règles. Les deux propriétés « négatives » dont on a besoin, `libre` et `sans_cle`, sont fournies comme faits positifs par `faits_de_etat`.

La validation principale est un test de cohérence : sur 6 cartes et 12 états par carte, l'ensemble des cases `d` telles que `deplacement_possible(r, d)` est déduit est exactement l'ensemble des cases atteintes par `jeu.actions_legales`. La base de connaissances et le simulateur donnent donc les mêmes déplacements.

### 4.4 Justifier et interdire une action

Situation : sur `salle_fermee`, Bleu est en (4, 6), juste sous la porte (4, 5) qui ferme la salle de la balise. `BaseConnaissances.expliquer` remonte la dérivation jusqu'aux faits observés.

**Avec une clé, l'ouverture est justifiée** (25 faits déduits) :

```
deplacement_possible(bleu, (4,5))  [règle franchissement]
  peut_ouvrir(bleu, (4,5))  [règle ouverture]
    trait(bleu)  [observé]
    possede_cle(bleu)  [observé]
    position(bleu, (4,6))  [observé]
    voisine((4,6), (4,5))  [observé]
    porte_fermee((4,5))  [observé]
```

**Sans clé, le même déplacement est interdit** : `peut_ouvrir` et `deplacement_possible(bleu, (4,5))` ne sont plus déduits, et la règle `interdiction_porte` conclut :

```
interdit(bleu, (4,5))  [règle interdiction_porte]
  trait(bleu)  [observé]
  sans_cle(bleu)  [observé]
  position(bleu, (4,6))  [observé]
  voisine((4,6), (4,5))  [observé]
  porte_fermee((4,5))  [observé]
```

Seul le fait `possede_cle(bleu)`, remplacé par `sans_cle(bleu)`, distingue les deux situations. Les tests couvrent aussi le coup gagnant devant la balise et le ramassage d'une clé voisine.

### 4.5 Limites d'une représentation propositionnelle

Nos faits sont des **prédicats** : une seule règle `deplacement` avec les variables `?r`, `?c` et `?d` vaut pour les deux robots et toutes les cases. Dans une représentation purement propositionnelle, chaque fait est une variable booléenne sans structure (`bleu_en_4_6`, `voisine_4_6_4_5`...), et chaque règle doit être écrite pour chaque instanciation :

- pour `deplacement`, il faut une règle par robot et par couple de cases voisines : 2 × 104 = 208 règles sur `salle_fermee` (44 cases praticables), 1 272 sur `grand_labyrinthe_25x25`, contre une seule ici ;
- la base de règles dépend de la carte : il faut la régénérer pour chaque carte, alors que nos règles sont indépendantes du plateau ;
- on ne peut pas exprimer une propriété générale comme « aucun robot ne traverse un mur » ni poser une question à variable comme `deplacement_possible(bleu, ?d)` : il faudrait énumérer toutes les propositions candidates ;
- les relations entre objets (adjacence, possession) se réduisent à des noms de variables, que le moteur ne peut pas analyser.

La logique des prédicats garde la structure (objets, relations, variables) et rend les règles **génériques**. L'unification fait le travail d'instanciation au moment du raisonnement. Notre représentation garde cependant deux limites : les règles sont des clauses de Horn positives, donc sans négation ni quantificateur universel dans les prémisses (d'où les faits `libre` et `sans_cle` calculés à part), et la base décrit un seul état, sans raisonnement sur le temps ou sur les actions futures de l'adversaire.

## 5. Partie III — Décision adversariale

### 5.1 Valeurs terminales et fonction d'évaluation
Utilités ±(1000 − ply) pour préférer les victoires rapides. Distances avec clés et portes (BFS précalculés), normalisation par la taille de la carte, poids 1 / 0,4 / 0,1 pas, borne |E| < 920. Erreur de la première version (écart écrêté qui sature). *(à rédiger, voir docs/seance2.md §3)*

### 5.2 Min-Max et Alpha-Bêta
Mêmes fonctions de transition, de test terminal et d'évaluation ; égalité des valeurs vérifiée sur 500 cas. Tableau des nœuds et des temps par profondeur : `resultats/minimax_alphabeta.md`. Graphique nœuds = f(d), échelle logarithmique. *(à rédiger)*

### 5.3 Ordre des coups
Naturel, aléatoire, meilleur d'abord, pire d'abord : facteur 3 à 8 sur les nœuds à d = 8. *(à rédiger)*

### 5.4 Budget de calcul et effet d'horizon
Approfondissement itératif (`resultats/iteratif.md`) ; effet d'horizon devant la porte de salle_fermee et évaluation améliorée E+ (`resultats/horizon.md`). *(à rédiger)*

## 6. Partie IV — Information partielle

Code : `src/course_balise/partiel/` (`vue.py`, `memoire.py`, `solo.py`), `agents/partiels.py`, commande `uv run fondement-de-ia decouvrir <carte>`, tests `tests/test_partiel.py`, expérience `experiences/information_partielle.py` (résultats : `resultats/information_partielle.md`).

### 6.1 Vue locale et mémoire

Les règles physiques ne changent pas : seul ce que l'agent sait est restreint. `vue_locale(carte, etat, joueur, rayon)` renvoie une `Observation` : les cases à distance de Manhattan au plus `rayon` (1 dans l'énoncé, soit au plus 5 cases), avec leur contenu (`#` mur, `.` case ordinaire ou porte ouverte, `D` porte fermée, `K` clé, `G` balise), la clé du robot, et la position de l'adversaire s'il est dans le champ. On suppose seulement les dimensions du plateau connues. Cette fonction est le **seul** accès des agents partiels à l'état réel.

La `Memoire` stocke, pour chaque case déjà vue, le dernier contenu observé ; une case vue reste connue. Ce contenu peut devenir faux sans que le robot le sache (une clé ramassée par l'adversaire hors du champ, une porte qu'il a ouverte) : il est corrigé à la prochaine observation. L'adversaire est supposé immobile à sa dernière position vue, jusqu'à ce que le robot voie cette case vide.

Avec un rayon d'au moins 1, les quatre voisines du robot sont toujours observées. Les actions légales se déduisent donc exactement de la mémoire, et un test vérifie qu'elles coïncident avec `jeu.actions_legales` sur 72 états. Un autre test vérifie que l'agent joue le même coup sur deux cartes identiques autour de lui mais différentes ailleurs.

### 6.2 Exploration des frontières et planification optimiste

La **frontière** est l'ensemble des cases connues praticables qui ont au moins une voisine inconnue. L'agent `explorateur` décide ainsi à chaque tour :

1. si G est connue, il calcule un plan **optimiste** par A* sur une carte supposée, où les cases inconnues sont libres, et joue son premier pas ;
2. sinon, il va vers la case de frontière la plus proche (BFS sur les cases connues ; sans clé, les clés connues sont aussi des cibles, car il faudra sans doute franchir une porte).

Le plan est recalculé à chaque tour : dès qu'une observation contredit l'hypothèse optimiste (un mur sur le chemin prévu), le plan change. La méthode termine : chaque pas vers une cible la rapproche, et chaque arrivée sur la frontière révèle au moins une case inconnue. Tant qu'une cible reste atteignable, l'agent finit donc par la découvrir.

Avec un rayon de 1, G n'est vue qu'en arrivant à côté, si bien que la planification optimiste sert peu. Nous avons donc ajouté deux variantes : un rayon de 2 (`-r2`), et une balise dont seule la position est connue dès le départ (`-g`), comme si elle émettait un signal.

### 6.3 Carte complète contre découverte progressive

Course en solitaire (`partiel/solo.py`) : l'adversaire reste sur sa case de départ, le robot joue tous les coups jusqu'à G. Nombre de pas, Bleu / Rouge :

| Carte | A* (carte complète) | explorateur | explorateur-r2 | explorateur-g | explorateur-r2-g |
|---|---|---|---|---|---|
| couloir_5x5 | 6 / 4 | 8 / 4 | 8 / 4 | 8 / 4 | 8 / 4 |
| exemple_7x7 | 6 / 6 | 22 / 12 | 6 / 6 | 6 / 8 | 6 / 8 |
| porte_raccourci | 7 / 7 | 13 / 19 | 13 / 17 | 13 / 17 | 13 / 17 |
| salle_fermee | 21 / 21 | 63 / 63 | 59 / 59 | 63 / 63 | 59 / 59 |
| arene_9x9 | 12 / 12 | 46 / 50 | 18 / 20 | 18 / 22 | 14 / 12 |
| labyrinthe_11x11 | 22 / 22 | 24 / 22 | 24 / 24 | 44 / 48 | 38 / 38 |
| grand_labyrinthe_25x25 | 62 / 66 | 174 / 242 | 196 / 388 | 364 / 318 | 280 / 246 |

- L'explorateur arrive toujours, mais jamais en moins de pas que A* avec la carte complète (vérifié par test). Le surcoût va de 1 à près de 6.
- Dans une salle ouverte (`arene_9x9`), voir plus loin compte beaucoup : de 46 à 18 pas pour Bleu avec un rayon de 2.
- Sur `porte_raccourci`, aucun explorateur ne prend le raccourci : la porte n'est utile qu'avec la clé, et le robot ne le sait qu'après l'avoir vue. Sur `salle_fermee`, il faut d'abord trouver l'unique clé, en haut, puis revenir à la porte, en bas : le parcours est trois fois plus long.
- Dans les labyrinthes, l'optimisme coûte cher : connaître la position de G (`-g`) **double** le nombre de pas sur `labyrinthe_11x11` (44 au lieu de 24). Le plan optimiste traverse des zones inconnues en ligne droite vers G, et le robot s'engage dans des culs-de-sac. L'exploration systématique de la frontière la plus proche parcourt les couloirs dans l'ordre et s'en sort mieux.
- Un rayon plus grand n'aide pas toujours (Rouge sur le grand labyrinthe : 388 pas au lieu de 242) : la règle « frontière la plus proche » est gloutonne, et voir plus de cases change l'ordre de visite sans garantie de gain.

En partie (cartes sans le 25 × 25, couleurs et premier joueur inversés, graines 0 à 4 contre l'aléatoire), l'explorateur gagne 56 % de ses parties contre l'agent aléatoire, avec 33 % de nuls, et seulement 12 % contre A* avec la carte complète, qui va droit au but. La meilleure variante, `optimiste-d4-r2-g`, monte à 74 % contre l'aléatoire.

### 6.4 Pourquoi Min-Max ne s'applique pas directement à l'état caché

Appliquer Min-Max à l'état réel reviendrait à faire décider le robot avec des informations qu'il n'a pas : la position des murs non vus, celle de l'adversaire, sa clé. La décision dépendrait alors de la partie cachée de la carte, ce que le robot ne peut pas faire en vrai. Deux situations qu'il ne sait pas distinguer recevraient des coups différents. De plus, Min-Max suppose que **les deux** joueurs connaissent l'état ; ici, l'adversaire a lui aussi une vue partielle, et ses réponses dépendent de ce qu'il a vu, pas de l'état réel. L'arbre de jeu correct porterait sur des ensembles d'états possibles (jeu à information imparfaite), ce qui sort du cadre du TP.

**Approximation retenue** (`optimiste-dN`) : quand l'adversaire est visible et que G est connue, l'agent joue Alpha-Bêta, avec l'évaluation E+, sur un **jeu supposé** construit à partir des seules observations :

- carte supposée optimiste : cases inconnues libres, murs, portes et clés tels qu'ils ont été vus ;
- adversaire à sa position observée, supposé sans clé (sa clé n'est pas observable) ;
- tour et passes connus de tous.

Sinon, l'agent se comporte comme l'explorateur. Cette approximation ne prétend pas résoudre le jeu à information imparfaite : elle traite le jeu supposé comme s'il était le vrai. Elle reste sûre, car le coup choisi est toujours légal (les voisines sont observées), mais elle peut se tromper sur la suite. En pratique, avec un rayon de 1, l'adversaire n'est visible que lorsqu'il est collé au robot : Alpha-Bêta n'est utilisé que pour 8 % des décisions au plus selon la variante et l'adversaire, et jusqu'à 15 % avec un rayon de 2.

## 7. Partie V — Campagne d'évaluation

Script : `experiences/campagne.py` ; résultats complets : `resultats/campagne.md`, une ligne par agent et par partie dans `resultats/campagne.csv`.

### 7.1 Protocole

- **Agents** : aléatoire, A* (heuristique « clés », plan recalculé après chaque action adverse), Min-Max, Alpha-Bêta (coups triés par E) et Alpha-Bêta avec l'évaluation améliorée E+, tous à profondeur 4.
- **Cartes** : `couloir_5x5`, `exemple_7x7`, `porte_raccourci`, `salle_fermee`, `arene_9x9`, `labyrinthe_11x11` (le 25 × 25 est exclu, voir 2.3).
- **Configurations** : chaque paire d'agents joue dans 4 configurations, en inversant les couleurs (donc les positions de départ) et le joueur qui commence. Les cartes étant symétriques, inverser le premier joueur est indispensable.
- **Graines** : 0 à 9 pour les parties contre l'agent aléatoire ; les autres agents sont déterministes, une partie par configuration suffit. Dans `jouer`, Bleu reçoit la graine 2g et Rouge 2g + 1.
- **Total** : 1 104 parties, en 16 s environ. Les temps sont ceux du calcul des agents, sans affichage.

### 7.2 Résultats par agent

| Agent | Parties | Victoires | Nuls | Défaites | Tours moyens | Durée d'une partie (ms) | Temps par décision (ms) | Nœuds par décision |
|---|---|---|---|---|---|---|---|---|
| aléatoire | 960 | 3 % | 10 % | 87 % | 29,2 | 10,0 | 0,005 | 0 |
| A* | 312 | 87 % | 2 % | 12 % | 24,3 | 6,8 | 0,36 | 8 |
| Min-Max d = 4 | 312 | 69 % | 18 % | 13 % | 32,6 | 15,3 | 0,79 | 63 |
| Alpha-Bêta d = 4 | 312 | 72 % | 16 % | 12 % | 30,1 | 12,8 | 0,69 | 23 |
| Alpha-Bêta E+ d = 4 | 312 | 79 % | 6 % | 15 % | 28,3 | 12,8 | 0,72 | 23 |

Résultats par paire, en victoires / nuls / défaites de l'agent en ligne :

| | aléatoire | A* | Min-Max | Alpha-Bêta | Alpha-Bêta E+ |
|---|---|---|---|---|---|
| A* | 235/1/4 | – | 12/2/10 | 12/2/10 | 12/0/12 |
| Min-Max | 188/45/7 | 10/2/12 | – | 10/4/10 | 8/4/12 |
| Alpha-Bêta | 197/40/3 | 10/2/12 | 10/4/10 | – | 9/3/12 |
| Alpha-Bêta E+ | 212/11/17 | 12/0/12 | 12/4/8 | 12/3/9 | – |

- Entre agents déterministes, **le joueur qui commence gagne 81 % des parties** et n'en perd que 8 %. Sur des cartes symétriques, à force comparable, avoir un demi-coup d'avance suffit. Les seules défaites du premier joueur ont lieu sur `couloir_5x5`, la seule carte asymétrique : Rouge y est à 4 pas de G, Bleu à 6.
- A* fait jeu égal avec les agents adversariaux (12 victoires sur 24 contre chacun) et bat le mieux l'aléatoire. Sur ces cartes, la partie est surtout une course : aller droit au but est presque toujours le bon coup.
- Alpha-Bêta E+ est l'agent adversarial le plus efficace (79 %), grâce à `salle_fermee`, où il gagne 75 % de ses parties contre 0 % pour Min-Max et Alpha-Bêta avec E.

### 7.3 Min-Max et Alpha-Bêta à profondeur identique

Min-Max (ordre naturel) contre Alpha-Bêta (tri par E), même évaluation E, 4 configurations par carte, nœuds par décision :

| d | exemple_7x7 | porte_raccourci | salle_fermee | arene_9x9 | labyrinthe_11x11 |
|---|---|---|---|---|---|
| 2 | 10 / 8 | 9 / 7 | 7 / 6 | 18 / 11 | 8 / 7 |
| 4 | 65 / 24 | 51 / 20 | 27 / 17 | 205 / 48 | 41 / 20 |
| 6 | 397 / 57 | 285 / 44 | 103 / 37 | 2 408 / 164 | 195 / 49 |

- Les deux agents ont le même résultat dans presque toutes les configurations : chacun gagne quand il commence, et `salle_fermee` donne des nuls. À d = 6 sur `salle_fermee`, Alpha-Bêta gagne deux parties que Min-Max ne gagne pas : les deux algorithmes ont la même valeur Min-Max, mais ils départagent différemment les coups ex æquo (ordre naturel contre tri par E), ce qui change la partie.
- L'élagage économise 14 à 40 % des nœuds à d = 2, 39 à 77 % à d = 4 et 64 à 93 % à d = 6. Dans l'arène à d = 6, la décision passe de 35,6 ms à 7,7 ms.
- À d = 2, Alpha-Bêta est un peu **plus lent** que Min-Max malgré moins de nœuds (0,39 ms contre 0,27 ms dans l'arène) : le tri des coups coûte une évaluation par coup, plus que ce que l'élagage fait gagner sur un arbre aussi petit.

### 7.4 Échecs et décisions surprenantes

**Les nuls de `salle_fermee` (effet d'horizon).** Avec E, Min-Max et Alpha-Bêta d = 4 font 20 nuls sur 20 contre l'aléatoire sur cette carte, et aussi contre A* quand ils commencent. Ouvrir la porte consomme la clé et ouvre le passage à l'adversaire : E chute, alors que la victoire est au-delà de l'horizon (5 demi-coups, voir 5.4). Le robot reste devant la porte jusqu'à la limite de 80 tours. L'évaluation E+, qui estime la course, corrige ce défaut.

**Alpha-Bêta E+ battu par l'aléatoire sur `couloir_5x5`.** En Bleu, l'agent E+ perd 16 parties sur 20 contre l'agent aléatoire, et certaines durent plus de 50 tours. Bleu est à 6 pas de G, Rouge à 4 : E+ juge la course perdue, et sa valeur ne dépend plus que de la distance de Rouge. Tous les coups de Bleu se valent, et il oscille entre deux cases (S, N, S, N...) en attendant que l'aléatoire tombe sur G. Min-Max suppose un adversaire optimal : contre lui la position est perdue, mais pas contre un joueur aléatoire. Avec E, qui garde le terme `dR − dB`, Bleu continue d'avancer et ne perd que 3 parties sur 20. Il suffirait d'ajouter à E+ un petit terme sur la distance du robot en retard pour garder un gradient.

**Les oscillations entre coups ex æquo.** Min-Max, qui explore dans l'ordre naturel, fait 5 nuls sur 20 contre l'aléatoire dans l'arène, en Rouge : à l'horizon plusieurs coups ont la même valeur, et le premier de l'ordre fait reculer le robot. Alpha-Bêta, qui trie les coups par E, ne fait aucun nul dans la même situation. C'est le défaut déjà observé en séance 2.

**A* aussi fort que Min-Max à d = 4.** Sur des cartes symétriques où la course domine, anticiper 4 demi-coups n'apporte presque rien contre un adversaire qui va droit au but. Les situations où l'anticipation compte (bloquer un couloir, prendre la clé de l'autre) sont rares dans nos cartes, et demandent souvent une profondeur supérieure à 4.

## 8. Conclusion et limites

Le projet fournit un simulateur testé et cinq familles d'agents : recherche, raisonnement, décision adversariale, information partielle et campagne d'évaluation. Quelques enseignements :

- **Une seule source de vérité pour les règles.** La fonction `deplacement` est partagée par le jeu, la recherche, l'évaluation, et vérifiée par la base de connaissances. Des tests de cohérence le garantissent : les déplacements déduits par chaînage avant et ceux déduits de la vue locale coïncident avec `actions_legales`.
- **La fonction d'évaluation compte plus que la profondeur.** Les plus gros écarts de la campagne viennent de l'évaluation (E contre E+ sur `salle_fermee` et `couloir_5x5`), pas de l'algorithme : à profondeur égale, Min-Max et Alpha-Bêta ont la même valeur et jouent presque toujours la même partie, mais Alpha-Bêta visite jusqu'à 15 fois moins de nœuds.
- **Le premier joueur a un net avantage** sur des cartes symétriques (81 % de victoires) : toute comparaison doit alterner le joueur qui commence.
- **L'information partielle coûte cher**, de 1 à 6 fois plus de pas qu'avec la carte complète, et l'optimisme n'est pas toujours payant : dans un labyrinthe, connaître la position de G sans connaître les murs peut doubler le trajet.

Limites :

- le chaînage avant ne porte que sur l'état courant, avec des clauses de Horn positives : pas de négation, pas de raisonnement sur les actions futures ;
- E+ n'a plus de gradient pour le robot qui perd la course, ce qui le rend passif contre un adversaire faible (7.4) ;
- nos cartes sont petites et souvent symétriques : les situations stratégiques fines (blocage d'un couloir, vol de clé) y sont rares, et la campagne ne compare que la profondeur 4 ;
- en information partielle, l'adversaire est supposé immobile hors du champ de vision et sans clé ; aucune croyance probabiliste sur l'état n'est maintenue (approfondissement facultatif de l'énoncé) ;
- les temps sont mesurés sur une seule machine, sur des décisions de l'ordre de la milliseconde : seuls les rapports entre agents sont significatifs.

Pistes : ajouter un terme de distance propre à E+, une recherche de quiescence contre l'effet d'horizon, des tables de transposition (les états sont déjà hashables), et une campagne à budget de temps égal (approfondissement itératif) plutôt qu'à profondeur égale.
