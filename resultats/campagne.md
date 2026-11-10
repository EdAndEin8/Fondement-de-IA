# Partie V — Campagne d'évaluation

Script : `experiences/campagne.py`.

Agents : aleatoire, astar, minmax-d4, alphabeta-d4, alphabeta+-d4 (profondeur 4, évaluation E pour Min-Max et Alpha-Bêta, E+ pour Alpha-Bêta amélioré, coups triés par évaluation pour Alpha-Bêta). A* utilise l'heuristique « clés » et replanifie à chaque tour.

Cartes : couloir_5x5, exemple_7x7, porte_raccourci, salle_fermee, arene_9x9, labyrinthe_11x11. Chaque paire joue dans 4 configurations : couleurs (et donc positions de départ) inversées, et joueur qui commence inversé. Graines 0 à 9 pour les parties contre l'agent aléatoire, graine 0 sinon (agents déterministes). Total : 1104 parties.

## 1. Bilan par agent

Durée : temps total d'une partie (décisions des deux agents et transitions, sans affichage). Temps et nœuds : moyenne par décision de l'agent.

| Agent | Parties | Victoires | Nuls | Défaites | Tours moyens | Durée moyenne (ms) | Temps par décision (ms) | Nœuds par décision |
|---|---|---|---|---|---|---|---|---|
| aleatoire | 960 | 3% | 10% | 87% | 29.2 | 10.0 | 0.005 | 0 |
| astar | 312 | 87% | 2% | 12% | 24.3 | 6.8 | 0.336 | 8 |
| minmax-d4 | 312 | 69% | 18% | 13% | 32.6 | 15.2 | 0.795 | 63 |
| alphabeta-d4 | 312 | 72% | 16% | 12% | 30.1 | 13.2 | 0.721 | 23 |
| alphabeta+-d4 | 312 | 79% | 6% | 15% | 28.3 | 12.6 | 0.720 | 23 |

## 2. Résultats par paire

Victoires / nuls / défaites de l'agent en ligne contre l'agent en colonne.

| Agent \ adversaire | aleatoire | astar | minmax-d4 | alphabeta-d4 | alphabeta+-d4 |
|---|---|---|---|---|---|
| aleatoire | – | 4/1/235 | 7/45/188 | 3/40/197 | 17/11/212 |
| astar | 235/1/4 | – | 12/2/10 | 12/2/10 | 12/0/12 |
| minmax-d4 | 188/45/7 | 10/2/12 | – | 10/4/10 | 8/4/12 |
| alphabeta-d4 | 197/40/3 | 10/2/12 | 10/4/10 | – | 9/3/12 |
| alphabeta+-d4 | 212/11/17 | 12/0/12 | 12/4/8 | 12/3/9 | – |

## 3. Taux de victoire / nul par carte

| Carte | aleatoire | astar | minmax-d4 | alphabeta-d4 | alphabeta+-d4 |
|---|---|---|---|---|---|
| couloir_5x5 | 18% / 0% | 81% / 0% | 77% / 0% | 83% / 0% | 58% / 0% |
| exemple_7x7 | 1% / 0% | 88% / 0% | 87% / 0% | 88% / 0% | 88% / 0% |
| porte_raccourci | 1% / 1% | 88% / 0% | 87% / 2% | 87% / 2% | 83% / 8% |
| salle_fermee | 0% / 55% | 87% / 10% | 0% / 92% | 0% / 92% | 75% / 21% |
| arene_9x9 | 0% / 4% | 88% / 0% | 77% / 12% | 88% / 0% | 87% / 4% |
| labyrinthe_11x11 | 0% / 1% | 88% / 0% | 88% / 0% | 88% / 0% | 87% / 2% |

## 4. Effet du joueur qui commence

Parties entre agents déterministes seulement.

| Agent | Commence (V / N / D) | Second (V / N / D) |
|---|---|---|
| astar | 92% / 0% / 8% | 8% / 11% / 81% |
| minmax-d4 | 69% / 22% / 8% | 8% / 6% / 86% |
| alphabeta-d4 | 72% / 19% / 8% | 8% / 6% / 86% |
| alphabeta+-d4 | 92% / 0% / 8% | 8% / 19% / 72% |
| tous (point de vue du premier) | 81% / 10% / 8% | – |

## 5. Min-Max contre Alpha-Bêta à profondeur identique

Min-Max (ordre naturel) contre Alpha-Bêta (tri par E), même évaluation E, 4 configurations par carte. V/N/D du point de vue de Min-Max ; nœuds et temps par décision.

| d | Carte | Min-Max V/N/D | Nœuds Min-Max | Nœuds Alpha-Bêta | Économie | ms Min-Max | ms Alpha-Bêta |
|---|---|---|---|---|---|---|---|
| 2 | couloir_5x5 | 2/0/2 | 7 | 6 | 16% | 0.09 | 0.15 |
| 2 | exemple_7x7 | 2/0/2 | 10 | 8 | 27% | 0.16 | 0.23 |
| 2 | porte_raccourci | 2/0/2 | 9 | 7 | 24% | 0.19 | 0.25 |
| 2 | salle_fermee | 0/4/0 | 7 | 6 | 14% | 0.08 | 0.14 |
| 2 | arene_9x9 | 2/0/2 | 18 | 11 | 40% | 0.26 | 0.38 |
| 2 | labyrinthe_11x11 | 2/0/2 | 8 | 7 | 19% | 0.12 | 0.19 |
| 4 | couloir_5x5 | 2/0/2 | 34 | 18 | 47% | 0.34 | 0.45 |
| 4 | exemple_7x7 | 2/0/2 | 65 | 24 | 64% | 0.74 | 0.73 |
| 4 | porte_raccourci | 2/0/2 | 51 | 20 | 61% | 0.59 | 0.61 |
| 4 | salle_fermee | 0/4/0 | 27 | 17 | 39% | 0.36 | 0.48 |
| 4 | arene_9x9 | 2/0/2 | 205 | 48 | 77% | 3.01 | 2.22 |
| 4 | labyrinthe_11x11 | 2/0/2 | 41 | 20 | 51% | 0.44 | 0.53 |
| 6 | couloir_5x5 | 2/0/2 | 123 | 35 | 72% | 1.17 | 0.84 |
| 6 | exemple_7x7 | 2/0/2 | 397 | 57 | 86% | 4.23 | 1.76 |
| 6 | porte_raccourci | 2/0/2 | 285 | 44 | 84% | 2.29 | 1.08 |
| 6 | salle_fermee | 0/2/2 | 103 | 37 | 64% | 1.30 | 1.08 |
| 6 | arene_9x9 | 2/0/2 | 2408 | 164 | 93% | 32.39 | 7.46 |
| 6 | labyrinthe_11x11 | 2/0/2 | 195 | 49 | 75% | 2.62 | 1.74 |

## 6. Échecs et décisions surprenantes

### 6.1 Parties non gagnées contre l'agent aléatoire

Toutes configurations confondues (premier joueur et graines).

| Agent | Carte | Couleur | Parties | Nuls | Défaites |
|---|---|---|---|---|---|
| minmax-d4 | couloir_5x5 | B | 20 | 0 | 6 |
| minmax-d4 | exemple_7x7 | R | 20 | 0 | 1 |
| minmax-d4 | salle_fermee | B | 20 | 20 | 0 |
| minmax-d4 | salle_fermee | R | 20 | 20 | 0 |
| minmax-d4 | arene_9x9 | R | 20 | 5 | 0 |
| alphabeta-d4 | couloir_5x5 | B | 20 | 0 | 3 |
| alphabeta-d4 | salle_fermee | B | 20 | 20 | 0 |
| alphabeta-d4 | salle_fermee | R | 20 | 20 | 0 |
| alphabeta+-d4 | couloir_5x5 | B | 20 | 0 | 16 |
| alphabeta+-d4 | porte_raccourci | R | 20 | 2 | 1 |
| alphabeta+-d4 | salle_fermee | B | 20 | 3 | 0 |
| alphabeta+-d4 | salle_fermee | R | 20 | 4 | 0 |
| alphabeta+-d4 | arene_9x9 | B | 20 | 1 | 0 |
| alphabeta+-d4 | labyrinthe_11x11 | B | 20 | 1 | 0 |

### 6.2 Parties non gagnées en commençant, contre un agent déterministe plus faible

Ordre indicatif des agents : aleatoire < astar < minmax-d4 < alphabeta-d4 < alphabeta+-d4. Les défaites quand l'agent joue en second sont attendues (section 4) et ne sont pas listées.

| Agent | Adversaire | Carte | Couleur | Issue | Raison | Tours |
|---|---|---|---|---|---|---|
| minmax-d4 | astar | couloir_5x5 | B | defaite | victoire R | 8 |
| minmax-d4 | astar | salle_fermee | R | nul | nul (limite de tours) | 80 |
| minmax-d4 | astar | salle_fermee | B | nul | nul (limite de tours) | 80 |
| alphabeta-d4 | astar | couloir_5x5 | B | defaite | victoire R | 8 |
| alphabeta-d4 | astar | salle_fermee | R | nul | nul (limite de tours) | 80 |
| alphabeta-d4 | astar | salle_fermee | B | nul | nul (limite de tours) | 80 |
| alphabeta+-d4 | astar | couloir_5x5 | B | defaite | victoire R | 8 |
| alphabeta-d4 | minmax-d4 | couloir_5x5 | B | defaite | victoire R | 8 |
| alphabeta-d4 | minmax-d4 | salle_fermee | R | nul | nul (limite de tours) | 80 |
| alphabeta-d4 | minmax-d4 | salle_fermee | B | nul | nul (limite de tours) | 80 |
| alphabeta+-d4 | minmax-d4 | couloir_5x5 | B | defaite | victoire R | 8 |
| alphabeta+-d4 | alphabeta-d4 | couloir_5x5 | B | defaite | victoire R | 8 |
