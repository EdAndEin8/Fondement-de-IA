# Effet d'horizon

## 1. Bleu devant la porte, avec la clé (salle_fermee, tour 36)

```
Tour 36 | trait : Bleu  | clé Bleu : 1 | clé Rouge : 0 | passes : 0
   0 1 2 3 4 5 6 7 8
 0 R . . . . . . . .
 1 . # # # # # # # .
 2 . # . . . . . # .
 3 . # . . G . . # .
 4 . # . . . . . # .
 5 . # # # D # # # .
 6 . . . . B . . . .
```

**E** : E(s) = 371 (dB = 3, dR = 35) ; après N : 126 (dB = 2, dR = 13)

| d | Coup | Valeur | Valeurs à la racine (bornes pour les coups élagués) |
|---|---|---|---|
| 1 | O | 359 | E : 359, N : 126, O : 359 |
| 2 | O | 359 | E : 359, N : 114, O : 359 |
| 3 | O | 371 | E : 371, N : 128, O : 371 |
| 4 | O | 371 | E : 371, N : 117, O : 371 |
| 5 | N | 995 | E : 359, N : 995, O : 359 |
| 6 | N | 995 | E : 359, N : 995, O : 359 |
| 7 | N | 995 | E : 371, N : 995, O : 371 |

**E+** : E(s) = 421 (dB = 3, dR = 35) ; après N : 427 (dB = 2, dR = 13)

| d | Coup | Valeur | Valeurs à la racine (bornes pour les coups élagués) |
|---|---|---|---|
| 1 | N | 427 | E : 409, N : 427, O : 409 |
| 2 | N | 427 | E : 409, N : 427, O : 409 |
| 3 | N | 441 | E : 421, N : 441, O : 421 |
| 4 | N | 441 | E : 421, N : 441, O : 421 |
| 5 | N | 995 | E : 427, N : 995, O : 427 |
| 6 | N | 995 | E : 427, N : 995, O : 427 |
| 7 | N | 995 | E : 441, N : 995, O : 441 |

## 2. En partie : victoires / nuls / défaites de Bleu (Alpha-Bêta)

Bleu commence. Contre l'aléatoire : 10 graines (0 à 9) ; contre A* : partie déterministe. Entre parenthèses, le nombre moyen de tours.

| Carte | d | Évaluation | contre aléatoire | contre A* |
|---|---|---|---|---|
| salle_fermee | 2 | E | 0/10/0 (80 t.) | 0/1/0 (80 t.) |
| salle_fermee | 2 | E+ | 10/0/0 (41 t.) | 1/0/0 (41 t.) |
| salle_fermee | 3 | E | 0/10/0 (80 t.) | 0/1/0 (80 t.) |
| salle_fermee | 3 | E+ | 10/0/0 (41 t.) | 1/0/0 (41 t.) |
| salle_fermee | 4 | E | 0/10/0 (80 t.) | 0/1/0 (80 t.) |
| salle_fermee | 4 | E+ | 10/0/0 (41 t.) | 1/0/0 (41 t.) |
| salle_fermee | 5 | E | 10/0/0 (41 t.) | 1/0/0 (41 t.) |
| salle_fermee | 5 | E+ | 10/0/0 (41 t.) | 1/0/0 (41 t.) |
| salle_fermee | 6 | E | 10/0/0 (41 t.) | 1/0/0 (41 t.) |
| salle_fermee | 6 | E+ | 10/0/0 (41 t.) | 1/0/0 (41 t.) |
| porte_raccourci | 2 | E | 10/0/0 (18 t.) | 1/0/0 (13 t.) |
| porte_raccourci | 2 | E+ | 10/0/0 (13 t.) | 1/0/0 (13 t.) |
| porte_raccourci | 3 | E | 10/0/0 (18 t.) | 1/0/0 (13 t.) |
| porte_raccourci | 3 | E+ | 10/0/0 (13 t.) | 1/0/0 (13 t.) |
| porte_raccourci | 4 | E | 10/0/0 (18 t.) | 1/0/0 (13 t.) |
| porte_raccourci | 4 | E+ | 10/0/0 (13 t.) | 1/0/0 (13 t.) |
| porte_raccourci | 5 | E | 10/0/0 (13 t.) | 1/0/0 (13 t.) |
| porte_raccourci | 5 | E+ | 10/0/0 (13 t.) | 1/0/0 (13 t.) |
| porte_raccourci | 6 | E | 10/0/0 (13 t.) | 1/0/0 (13 t.) |
| porte_raccourci | 6 | E+ | 10/0/0 (13 t.) | 1/0/0 (13 t.) |
