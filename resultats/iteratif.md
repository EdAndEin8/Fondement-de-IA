# Approfondissement itératif sous budget

5 états par carte (graine 2026), Alpha-Bêta avec tri par E, meilleur coup précédent en tête.

Une action légale est renvoyée dans 100 % des cas, même avec 1 ms.

| Carte | Budget (ms) | Profondeur moy. | Min–max | Temps moy. (ms) | Temps max (ms) | Itération abandonnée | Nœuds |
|---|---|---|---|---|---|---|---|
| exemple_7x7 | 1 | 4.0 | 4–4 | 1.5 | 2.1 | 0 % | 48 |
| exemple_7x7 | 5 | 5.2 | 4–6 | 5.0 | 6.7 | 60 % | 102 |
| exemple_7x7 | 20 | 6.8 | 4–9 | 10.7 | 22.3 | 20 % | 279 |
| exemple_7x7 | 100 | 7.2 | 4–11 | 13.8 | 39.3 | 0 % | 414 |
| exemple_7x7 | 500 | 7.2 | 4–11 | 15.2 | 40.4 | 0 % | 414 |
| salle_fermee | 1 | 4.6 | 4–5 | 1.3 | 1.7 | 0 % | 52 |
| salle_fermee | 5 | 7.2 | 7–8 | 6.4 | 6.6 | 100 % | 180 |
| salle_fermee | 20 | 10.0 | 9–11 | 20.5 | 20.9 | 60 % | 602 |
| salle_fermee | 100 | 13.8 | 12–15 | 101.0 | 101.7 | 100 % | 2597 |
| salle_fermee | 500 | 18.0 | 16–20 | 500.7 | 501.4 | 100 % | 12491 |
| labyrinthe_11x11 | 1 | 4.0 | 4–4 | 1.2 | 1.6 | 0 % | 39 |
| labyrinthe_11x11 | 5 | 6.0 | 6–6 | 6.2 | 9.5 | 100 % | 117 |
| labyrinthe_11x11 | 20 | 8.8 | 8–10 | 20.8 | 21.7 | 60 % | 425 |
| labyrinthe_11x11 | 100 | 13.2 | 13–14 | 101.7 | 102.1 | 100 % | 2442 |
| labyrinthe_11x11 | 500 | 17.4 | 17–18 | 501.1 | 503.2 | 100 % | 11753 |
| arene_9x9 | 1 | 3.6 | 3–4 | 1.7 | 2.2 | 0 % | 48 |
| arene_9x9 | 5 | 4.6 | 4–5 | 6.3 | 7.4 | 100 % | 100 |
| arene_9x9 | 20 | 6.6 | 6–7 | 21.1 | 22.4 | 100 % | 378 |
| arene_9x9 | 100 | 8.8 | 8–10 | 101.5 | 103.5 | 100 % | 1648 |
| arene_9x9 | 500 | 11.2 | 10–12 | 500.9 | 502.0 | 100 % | 7300 |
| grand_labyrinthe_25x25 | 1 | 4.2 | 4–5 | 1.3 | 1.6 | 0 % | 45 |
| grand_labyrinthe_25x25 | 5 | 6.2 | 6–7 | 5.7 | 6.8 | 100 % | 134 |
| grand_labyrinthe_25x25 | 20 | 9.4 | 9–10 | 21.1 | 21.6 | 60 % | 581 |
| grand_labyrinthe_25x25 | 100 | 13.2 | 12–14 | 101.2 | 101.9 | 100 % | 2743 |
| grand_labyrinthe_25x25 | 500 | 17.2 | 16–18 | 501.1 | 501.7 | 100 % | 13001 |

Une profondeur moyenne qui plafonne avant le budget maximal signifie qu'une issue certaine (victoire ou défaite forcée) a été trouvée, ou que la profondeur atteint le nombre de tours restants.
