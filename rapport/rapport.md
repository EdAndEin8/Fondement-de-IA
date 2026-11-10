# La course à la balise — rapport technique

*Anton Dion, Matthieu Meunier, Sean Persand — 4e année du cycle FISA ICy, INSA Hauts-de-France, 2026–2027*

> Rapport de groupe (6 à 10 pages). Les sections marquées « à rédiger » seront complétées au fil des séances.

## 1. Introduction

Le jeu, les objectifs, le plan du rapport. *(à rédiger)*

## 2. Modélisation et simulateur

- Séparation carte immuable / état hashable `s = (PB, PR, j, KB, KR, Ksol, Douvert, t, p)`.
- Règles R1–R8 centralisées dans `regles.py`, fonction `deplacement` partagée avec la recherche.
- Format texte des cartes, cartes de test, générateur de labyrinthes.
- Tests : un test par règle (voir `tests/test_regles.py`).

## 3. Partie I — Recherche et planification

### 3.1 Formulation
État de recherche (position, clé, clés au sol, portes ouvertes) ; adversaire = obstacle fixe ; coût unitaire.

### 3.2 Algorithmes et heuristiques
BFS, UCS, DFS, A* ; heuristiques Manhattan, distance relaxée, détour par clé. Preuve d'admissibilité par relaxation, vérifiée par test.

### 3.3 Résultats
Tableau complet : `resultats/recherche.md`. Graphique nœuds développés par algorithme et par carte. *(à rédiger)*

### 3.4 Plus court chemin et vraie partie
Démonstration `experiences/plan_fige.py`. *(à rédiger, voir docs/seance1.md §4)*

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

## 7. Partie V — Campagne d'évaluation *(à venir)*

## 8. Conclusion et limites *(à rédiger)*
