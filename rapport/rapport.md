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

## 6. Partie IV — Information partielle *(à venir)*

## 7. Partie V — Campagne d'évaluation *(à venir)*

## 8. Conclusion et limites *(à rédiger)*
