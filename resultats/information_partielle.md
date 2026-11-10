# Partie IV — Information partielle

Script : `experiences/information_partielle.py`.

## 1. Course en solitaire : pas jusqu'à G

Adversaire immobile sur sa case de départ. Entre parenthèses : rapport au nombre de pas avec la carte complète.

| Carte | Robot | astar-cles | explorateur | explorateur-r2 | explorateur-g | explorateur-r2-g |
|---|---|---|---|---|---|---|
| couloir_5x5 | B | 6 | 8 (1.33) | 8 (1.33) | 8 (1.33) | 8 (1.33) |
| couloir_5x5 | R | 4 | 4 (1.0) | 4 (1.0) | 4 (1.0) | 4 (1.0) |
| exemple_7x7 | B | 6 | 22 (3.67) | 6 (1.0) | 6 (1.0) | 6 (1.0) |
| exemple_7x7 | R | 6 | 12 (2.0) | 6 (1.0) | 8 (1.33) | 8 (1.33) |
| porte_raccourci | B | 7 | 13 (1.86) | 13 (1.86) | 13 (1.86) | 13 (1.86) |
| porte_raccourci | R | 7 | 19 (2.71) | 17 (2.43) | 17 (2.43) | 17 (2.43) |
| salle_fermee | B | 21 | 63 (3.0) | 59 (2.81) | 63 (3.0) | 59 (2.81) |
| salle_fermee | R | 21 | 63 (3.0) | 59 (2.81) | 63 (3.0) | 59 (2.81) |
| arene_9x9 | B | 12 | 46 (3.83) | 18 (1.5) | 18 (1.5) | 14 (1.17) |
| arene_9x9 | R | 12 | 50 (4.17) | 20 (1.67) | 22 (1.83) | 12 (1.0) |
| labyrinthe_11x11 | B | 22 | 24 (1.09) | 24 (1.09) | 44 (2.0) | 38 (1.73) |
| labyrinthe_11x11 | R | 22 | 22 (1.0) | 24 (1.09) | 48 (2.18) | 38 (1.73) |
| grand_labyrinthe_25x25 | B | 62 | 174 (2.81) | 196 (3.16) | 364 (5.87) | 280 (4.52) |
| grand_labyrinthe_25x25 | R | 66 | 242 (3.67) | 388 (5.88) | 318 (4.82) | 246 (3.73) |

Part de la carte découverte à l'arrivée (moyenne Bleu / Rouge) et nœuds développés en tout :

| Carte | explorateur (connu / nœuds) | explorateur-r2 (connu / nœuds) | explorateur-g (connu / nœuds) | explorateur-r2-g (connu / nœuds) | astar-cles (nœuds) |
|---|---|---|---|---|---|
| couloir_5x5 | 48% / 14 | 70% / 20 | 48% / 18 | 70% / 20 | 16 |
| exemple_7x7 | 53% / 49 | 44% / 21 | 32% / 26 | 49% / 26 | 21 |
| porte_raccourci | 45% / 41 | 61% / 63 | 44% / 78 | 61% / 86 | 28 |
| salle_fermee | 83% / 634 | 100% / 700 | 83% / 764 | 100% / 730 | 238 |
| arene_9x9 | 88% / 146 | 56% / 106 | 48% / 107 | 48% / 66 | 78 |
| labyrinthe_11x11 | 39% / 57 | 53% / 106 | 52% / 419 | 60% / 361 | 253 |
| grand_labyrinthe_25x25 | 62% / 1252 | 90% / 5753 | 84% / 5183 | 85% / 5182 | 2082 |

## 2. Parties contre des adversaires

Cartes : couloir_5x5, exemple_7x7, porte_raccourci, salle_fermee, arene_9x9, labyrinthe_11x11. Couleurs et premier joueur inversés ; graines 0 à 4 contre l'aléatoire, une partie sinon (agents déterministes). Issue du point de vue de l'agent à information partielle.

| Agent | Adversaire | Parties | Victoires | Nuls | Défaites | Tours moyens | Décisions Alpha-Bêta |
|---|---|---|---|---|---|---|---|
| explorateur | aleatoire | 120 | 56% | 33% | 11% | 48.9 | 0.0% |
| explorateur | astar-cles | 24 | 12% | 0% | 88% | 27.8 | 0.0% |
| explorateur | explorateur | 24 | 42% | 17% | 42% | 43.0 | 0.0% |
| explorateur-g | aleatoire | 120 | 60% | 33% | 7% | 43.4 | 0.0% |
| explorateur-g | astar-cles | 24 | 12% | 0% | 88% | 27.8 | 0.0% |
| explorateur-g | explorateur | 24 | 58% | 0% | 42% | 34.9 | 0.0% |
| optimiste-d4 | aleatoire | 120 | 56% | 33% | 11% | 48.9 | 0.0% |
| optimiste-d4 | astar-cles | 24 | 12% | 0% | 88% | 27.8 | 0.0% |
| optimiste-d4 | explorateur | 24 | 42% | 17% | 42% | 43.0 | 0.0% |
| optimiste-d4-g | aleatoire | 120 | 60% | 33% | 7% | 43.4 | 2.1% |
| optimiste-d4-g | astar-cles | 24 | 12% | 0% | 88% | 27.8 | 0.3% |
| optimiste-d4-g | explorateur | 24 | 58% | 0% | 42% | 34.9 | 8.3% |
| optimiste-d4-r2-g | aleatoire | 120 | 74% | 20% | 6% | 41.2 | 9.7% |
| optimiste-d4-r2-g | astar-cles | 24 | 17% | 0% | 83% | 27.8 | 0.6% |
| optimiste-d4-r2-g | explorateur | 24 | 58% | 4% | 38% | 32.7 | 15.3% |
