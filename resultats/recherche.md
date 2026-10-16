# Comparaison des algorithmes de recherche

Temps : médiane de 15 exécutions. Pic mémoire : tracemalloc (exécution séparée).

| Carte | Robot | Algorithme | Longueur | Développés | Générés | Frontière max | Mémoire (nœuds) | Temps (ms) | Pic mémoire (Kio) |
|---|---|---|---|---|---|---|---|---|---|
| couloir_5x5 | Bleu | BFS | 6 | 11 | 22 | 2 | 12 | 0.0452 | 3.6 |
| couloir_5x5 | Bleu | UCS | 6 | 12 | 26 | 4 | 20 | 0.0666 | 3.5 |
| couloir_5x5 | Bleu | DFS | 8 | 8 | 17 | 3 | 11 | 0.0365 | 2.1 |
| couloir_5x5 | Bleu | A* Manhattan | 6 | 9 | 19 | 3 | 15 | 0.0494 | 3.8 |
| couloir_5x5 | Bleu | A* relaxée | 6 | 6 | 13 | 3 | 12 | 0.0563 | 3.1 |
| couloir_5x5 | Bleu | A* clés | 6 | 6 | 13 | 3 | 12 | 0.0756 | 4.7 |
| couloir_5x5 | Rouge | BFS | 4 | 6 | 13 | 3 | 8 | 0.0276 | 2.7 |
| couloir_5x5 | Rouge | UCS | 4 | 9 | 20 | 4 | 15 | 0.0495 | 3.5 |
| couloir_5x5 | Rouge | DFS | 4 | 8 | 16 | 3 | 10 | 0.0362 | 2.0 |
| couloir_5x5 | Rouge | A* Manhattan | 4 | 4 | 9 | 3 | 10 | 0.025 | 2.3 |
| couloir_5x5 | Rouge | A* relaxée | 4 | 4 | 9 | 3 | 10 | 0.0456 | 2.6 |
| couloir_5x5 | Rouge | A* clés | 4 | 4 | 9 | 3 | 10 | 0.0725 | 4.1 |
| exemple_7x7 | Bleu | BFS | 6 | 12 | 29 | 6 | 17 | 0.0566 | 4.1 |
| exemple_7x7 | Bleu | UCS | 6 | 17 | 43 | 9 | 35 | 0.1058 | 5.7 |
| exemple_7x7 | Bleu | DFS | 20 | 21 | 50 | 10 | 31 | 0.0986 | 6.0 |
| exemple_7x7 | Bleu | A* Manhattan | 6 | 6 | 15 | 4 | 14 | 0.0383 | 3.4 |
| exemple_7x7 | Bleu | A* relaxée | 6 | 6 | 15 | 4 | 14 | 0.0823 | 4.2 |
| exemple_7x7 | Bleu | A* clés | 6 | 6 | 15 | 4 | 14 | 0.2066 | 8.6 |
| exemple_7x7 | Rouge | BFS | 6 | 18 | 42 | 7 | 24 | 0.0806 | 5.8 |
| exemple_7x7 | Rouge | UCS | 6 | 24 | 55 | 8 | 38 | 0.1536 | 7.5 |
| exemple_7x7 | Rouge | DFS | 12 | 12 | 28 | 6 | 18 | 0.0567 | 3.4 |
| exemple_7x7 | Rouge | A* Manhattan | 6 | 10 | 23 | 6 | 22 | 0.0604 | 4.3 |
| exemple_7x7 | Rouge | A* relaxée | 6 | 6 | 15 | 6 | 18 | 0.0862 | 5.0 |
| exemple_7x7 | Rouge | A* clés | 6 | 6 | 15 | 6 | 18 | 0.2633 | 11.1 |
| grand_labyrinthe_25x25 | Bleu | BFS | 62 | 430 | 901 | 17 | 443 | 2.8426 | 68.5 |
| grand_labyrinthe_25x25 | Bleu | UCS | 62 | 443 | 933 | 17 | 477 | 2.5569 | 100.3 |
| grand_labyrinthe_25x25 | Bleu | DFS | 100 | 142 | 296 | 13 | 155 | 0.6685 | 23.0 |
| grand_labyrinthe_25x25 | Bleu | A* Manhattan | 62 | 349 | 733 | 15 | 379 | 2.0993 | 100.7 |
| grand_labyrinthe_25x25 | Bleu | A* relaxée | 62 | 209 | 441 | 18 | 245 | 1.7861 | 52.7 |
| grand_labyrinthe_25x25 | Bleu | A* clés | 62 | 62 | 134 | 14 | 90 | 2.084 | 55.7 |
| grand_labyrinthe_25x25 | Rouge | BFS | 66 | 485 | 1017 | 16 | 496 | 2.9828 | 71.9 |
| grand_labyrinthe_25x25 | Rouge | UCS | 66 | 496 | 1045 | 16 | 528 | 3.7192 | 103.8 |
| grand_labyrinthe_25x25 | Rouge | DFS | 158 | 176 | 384 | 29 | 205 | 1.2155 | 37.2 |
| grand_labyrinthe_25x25 | Rouge | A* Manhattan | 66 | 385 | 815 | 19 | 423 | 3.163 | 100.8 |
| grand_labyrinthe_25x25 | Rouge | A* relaxée | 66 | 215 | 457 | 13 | 241 | 2.4599 | 53.1 |
| grand_labyrinthe_25x25 | Rouge | A* clés | 66 | 66 | 144 | 16 | 98 | 2.8181 | 56.1 |
| labyrinthe_11x11 | Bleu | BFS | 22 | 62 | 131 | 10 | 69 | 0.4163 | 11.8 |
| labyrinthe_11x11 | Bleu | UCS | 22 | 70 | 152 | 12 | 94 | 0.664 | 13.3 |
| labyrinthe_11x11 | Bleu | DFS | 54 | 74 | 160 | 13 | 87 | 0.5284 | 12.9 |
| labyrinthe_11x11 | Bleu | A* Manhattan | 22 | 34 | 73 | 5 | 44 | 0.1957 | 8.6 |
| labyrinthe_11x11 | Bleu | A* relaxée | 22 | 22 | 49 | 7 | 36 | 0.2236 | 9.8 |
| labyrinthe_11x11 | Bleu | A* clés | 22 | 22 | 49 | 7 | 36 | 0.5548 | 17.4 |
| labyrinthe_11x11 | Rouge | BFS | 22 | 54 | 117 | 10 | 63 | 0.2381 | 11.4 |
| labyrinthe_11x11 | Rouge | UCS | 22 | 64 | 136 | 11 | 82 | 0.4416 | 12.8 |
| labyrinthe_11x11 | Rouge | DFS | 24 | 24 | 54 | 8 | 32 | 0.1692 | 5.7 |
| labyrinthe_11x11 | Rouge | A* Manhattan | 22 | 34 | 73 | 5 | 44 | 0.2617 | 8.6 |
| labyrinthe_11x11 | Rouge | A* relaxée | 22 | 22 | 49 | 7 | 36 | 0.2983 | 9.8 |
| labyrinthe_11x11 | Rouge | A* clés | 22 | 22 | 49 | 7 | 36 | 0.7164 | 17.4 |
| porte_raccourci | Bleu | BFS | 7 | 19 | 40 | 6 | 24 | 0.1184 | 5.8 |
| porte_raccourci | Bleu | UCS | 7 | 24 | 52 | 8 | 40 | 0.2206 | 7.6 |
| porte_raccourci | Bleu | DFS | 13 | 13 | 29 | 5 | 18 | 0.0837 | 3.2 |
| porte_raccourci | Bleu | A* Manhattan | 7 | 10 | 23 | 7 | 24 | 0.085 | 4.4 |
| porte_raccourci | Bleu | A* relaxée | 7 | 7 | 17 | 7 | 21 | 0.1515 | 6.1 |
| porte_raccourci | Bleu | A* clés | 7 | 7 | 17 | 7 | 21 | 0.3724 | 14.7 |
| porte_raccourci | Rouge | BFS | 7 | 14 | 28 | 3 | 16 | 0.0811 | 3.8 |
| porte_raccourci | Rouge | UCS | 7 | 16 | 35 | 5 | 26 | 0.1385 | 4.0 |
| porte_raccourci | Rouge | DFS | 33 | 37 | 77 | 7 | 44 | 0.2566 | 7.0 |
| porte_raccourci | Rouge | A* Manhattan | 7 | 10 | 23 | 5 | 20 | 0.0934 | 3.8 |
| porte_raccourci | Rouge | A* relaxée | 7 | 7 | 17 | 5 | 17 | 0.1497 | 5.7 |
| porte_raccourci | Rouge | A* clés | 7 | 7 | 17 | 5 | 17 | 0.2896 | 11.1 |
| salle_fermee | Bleu | BFS | 21 | 44 | 86 | 3 | 46 | 0.2772 | 9.8 |
| salle_fermee | Bleu | UCS | 21 | 46 | 94 | 6 | 58 | 0.3823 | 11.4 |
| salle_fermee | Bleu | DFS | 21 | 40 | 82 | 6 | 46 | 0.2659 | 6.7 |
| salle_fermee | Bleu | A* Manhattan | 21 | 41 | 84 | 6 | 53 | 0.348 | 11.7 |
| salle_fermee | Bleu | A* relaxée | 21 | 35 | 73 | 7 | 49 | 0.3024 | 10.8 |
| salle_fermee | Bleu | A* clés | 21 | 21 | 45 | 7 | 35 | 0.346 | 16.1 |
| salle_fermee | Rouge | BFS | 21 | 44 | 86 | 3 | 46 | 0.1755 | 9.8 |
| salle_fermee | Rouge | UCS | 21 | 46 | 94 | 6 | 58 | 0.407 | 11.5 |
| salle_fermee | Rouge | DFS | 21 | 43 | 87 | 5 | 48 | 0.2996 | 9.0 |
| salle_fermee | Rouge | A* Manhattan | 21 | 41 | 84 | 6 | 53 | 0.3853 | 11.7 |
| salle_fermee | Rouge | A* relaxée | 21 | 38 | 78 | 6 | 50 | 0.4656 | 13.6 |
| salle_fermee | Rouge | A* clés | 21 | 24 | 50 | 6 | 36 | 0.5392 | 17.2 |
