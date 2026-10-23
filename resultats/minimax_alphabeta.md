# Min-Max et Alpha-Bêta

5 états par carte (départ + milieux de partie, graine 2026). Temps : médiane de 3 exécutions.

Valeurs identiques Min-Max / Alpha-Bêta : **500/500** (toutes cartes, profondeurs et ordres).

## Nœuds visités et temps selon la profondeur (moyennes)

| Carte | d | MM nœuds | MM ms | AB naturel | AB tri E | AB tri E ms | Gain AB tri E |
|---|---|---|---|---|---|---|---|
| exemple_7x7 | 2 | 9 | 0.15 | 8 | 7 | 0.21 | 22 % |
| exemple_7x7 | 4 | 55 | 0.79 | 37 | 24 | 0.84 | 56 % |
| exemple_7x7 | 6 | 360 | 5.83 | 144 | 66 | 2.39 | 82 % |
| exemple_7x7 | 8 | 1978 | 26.34 | 485 | 135 | 4.79 | 93 % |
| exemple_7x7 | 10 | 13624 | 179.39 | 1609 | 263 | 9.58 | 98 % |
| porte_raccourci | 2 | 8 | 0.09 | 7 | 6 | 0.16 | 16 % |
| porte_raccourci | 4 | 35 | 0.40 | 28 | 19 | 0.53 | 44 % |
| porte_raccourci | 6 | 162 | 1.83 | 92 | 48 | 1.69 | 70 % |
| porte_raccourci | 8 | 710 | 9.52 | 265 | 109 | 3.36 | 85 % |
| porte_raccourci | 10 | 3449 | 39.59 | 774 | 234 | 8.81 | 93 % |
| salle_fermee | 2 | 7 | 0.10 | 7 | 6 | 0.16 | 15 % |
| salle_fermee | 4 | 29 | 0.40 | 23 | 17 | 0.57 | 42 % |
| salle_fermee | 6 | 117 | 1.71 | 67 | 41 | 1.36 | 65 % |
| salle_fermee | 8 | 460 | 6.32 | 189 | 92 | 2.97 | 80 % |
| salle_fermee | 10 | 1805 | 23.75 | 507 | 208 | 6.55 | 88 % |
| labyrinthe_11x11 | 2 | 7 | 0.11 | 7 | 6 | 0.20 | 16 % |
| labyrinthe_11x11 | 4 | 34 | 0.51 | 25 | 19 | 0.69 | 44 % |
| labyrinthe_11x11 | 6 | 147 | 2.02 | 79 | 47 | 1.56 | 68 % |
| labyrinthe_11x11 | 8 | 618 | 8.41 | 252 | 106 | 3.20 | 83 % |
| labyrinthe_11x11 | 10 | 2688 | 32.67 | 707 | 233 | 7.16 | 91 % |
| arene_9x9 | 2 | 12 | 0.20 | 9 | 8 | 0.30 | 30 % |
| arene_9x9 | 4 | 120 | 1.90 | 58 | 36 | 1.55 | 70 % |
| arene_9x9 | 6 | 1222 | 20.43 | 207 | 128 | 6.51 | 90 % |
| arene_9x9 | 8 | 12463 | 169.42 | 1430 | 542 | 23.51 | 96 % |
| arene_9x9 | 10 | 133097 | 1882.99 | 5557 | 1853 | 93.04 | 99 % |

## Influence de l'ordre des coups (Alpha-Bêta, d = 8, nœuds moyens)

| Carte | Naturel | Aléatoire | Meilleur d'abord (E) | Pire d'abord | Min-Max |
|---|---|---|---|---|---|
| exemple_7x7 | 485 | 427 | 135 | 1053 | 1978 |
| porte_raccourci | 265 | 282 | 109 | 668 | 710 |
| salle_fermee | 189 | 197 | 92 | 346 | 460 |
| labyrinthe_11x11 | 252 | 230 | 106 | 552 | 618 |
| arene_9x9 | 1430 | 1440 | 542 | 4677 | 12463 |
