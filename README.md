# Fondement-de-IA

Projet de TP — *Intelligence artificielle : Fondements* (4e année du cycle FISA ICy, INSA Hauts-de-France, 2026–2027, A. Daoud).

Groupe :

| Membre | GitHub | Séance 1 | Séance 2 |
|---|---|---|---|
| Anton Dion | EdAndEin8 | modélisation, règles et tests, organisation du dépôt | fonction d'évaluation, tests d'équivalence, effet d'horizon |
| Matthieu Meunier | Omicr0ne | recherche (BFS, UCS, DFS, A*), heuristiques, comparaison | Min-Max, Alpha-Bêta, ordre des coups, mesures |
| Sean Persand | SPUPH | affichage, boucle de jeu, agents, générateur de cartes | agents adversariaux, approfondissement itératif, arène |

Deux robots, Bleu et Rouge, se disputent une balise dans un labyrinthe avec murs, clés et portes. Le projet couvre la recherche dans un espace d'états, la représentation des connaissances, la décision adversariale (Min-Max, Alpha-Bêta), l'information partielle et une campagne d'évaluation.

## Avancement

| Partie | Contenu | État |
|---|---|---|
| Simulateur | carte, état, règles R1–R8, affichage ASCII, `jouer()` | fait (séance 1) |
| I — Recherche | BFS, UCS, DFS, A* (3 heuristiques), expériences | fait (séance 1) |
| II — Connaissances | base de faits, règles, chaînage avant | à venir |
| III — Adversarial | évaluation, Min-Max, Alpha-Bêta, ordre des coups, approfondissement itératif, expériences | fait (séance 2) |
| IV — Information partielle | vue locale, exploration des frontières | à venir |
| V — Évaluation | tournoi entre agents | à venir |

## Installation (uv)

```bash
uv sync          # installe Python 3.14 si besoin, puis le projet et pytest
uv run pytest    # lance les tests
```

## Utilisation

```bash
uv run fondement-de-ia cartes                                   # lister les cartes
uv run fondement-de-ia afficher exemple_7x7                     # afficher une carte
uv run fondement-de-ia chemin porte_raccourci --algo astar --heuristique cles
uv run fondement-de-ia jouer salle_fermee --bleu astar --rouge astar --animation
uv run fondement-de-ia jouer exemple_7x7 --bleu astar --rouge aleatoire --graine 3

uv run fondement-de-ia decider salle_fermee --profondeur 6       # Min-Max et Alpha-Bêta sur un état
uv run fondement-de-ia jouer salle_fermee --bleu alphabeta+-d4 --rouge iteratif-100ms --animation

uv run python experiences/comparaison_recherche.py            # Partie I -> resultats/
uv run python experiences/plan_fige.py salle_fermee
uv run python experiences/minimax_alphabeta.py                # Partie III -> resultats/
uv run python experiences/iteratif_budget.py
uv run python experiences/horizon.py
```

Agents disponibles :

| Nom | Agent |
|---|---|
| `aleatoire` | coup légal au hasard |
| `astar`, `astar-manhattan` | planificateur A* (heuristique « clés » ou Manhattan), replanifie à chaque tour |
| `minmax-dN` | Min-Max à profondeur N, évaluation E |
| `alphabeta-dN` | Alpha-Bêta à profondeur N, évaluation E, coups triés par E |
| `alphabeta+-dN` | Alpha-Bêta à profondeur N, évaluation améliorée E+ |
| `iteratif-Nms` | Alpha-Bêta itératif avec E+, budget de N ms par coup |

## Organisation du code

```
cartes/                    cartes texte (# mur, . libre, B, R, K clé, D porte, G balise)
src/course_balise/
  carte.py                 Carte immuable + parseur
  etat.py                  État s = (PB, PR, j, KB, KR, Ksol, Douvert, t, p), hashable
  regles.py                Jeu : actions_legales, transition, terminal, utilite (R1–R8)
  affichage.py             afficher(etat, carte) et animation ASCII
  jeu.py                   jouer(agent_bleu, agent_rouge, carte, graine)
  recherche/               Partie I : problème, BFS/UCS/DFS/A*, heuristiques
  adversarial/             Partie III : évaluation, Min-Max/Alpha-Bêta, ordre des coups, itératif
  agents/                  aléatoire, A*, Min-Max, Alpha-Bêta, Alpha-Bêta itératif
  cli.py                   ligne de commande
tests/                     pytest (règles, partie, recherche, adversarial)
experiences/               scripts d'expériences (graines fixées)
resultats/                 sorties des expériences (CSV, Markdown)
outils/                    générateur de labyrinthes
docs/                      notes techniques par séance
rapport/                   rapport de groupe (Markdown)
```

Les opérations demandées par l'énoncé sont des méthodes de la classe `Jeu`, qui porte la carte (paramètres immuables) :
`jeu.actions_legales(etat)`, `jeu.transition(etat, action)`, `jeu.terminal(etat)`, `jeu.utilite(etat, joueur)`.
Les actions sont `N`, `S`, `E`, `O` et `PASSER`.

### Format d'une carte

Une ligne par rangée, un caractère par case ; les lignes commençant par `%` sont des commentaires. L'origine (0, 0) est en haut à gauche.

```
% Plateau de la figure 1
B..#...
.#...#.
..K#...
#..G.#.
..#D#..
.#...#.
.....KR
```

## Travail en équipe sur GitHub

1. Chacun clone le dépôt et lance `uv sync`.
2. Une branche par fonctionnalité (`partie2-connaissances`, `partie3-alphabeta`…), puis une *pull request* vers `main` relue par un autre membre.
3. La CI (`.github/workflows/tests.yml`) lance `pytest` à chaque push : une PR ne se fusionne que si les tests passent.
4. Conventions de commit : `feat(...)`, `fix(...)`, `test:`, `exp(...)`, `docs:`.

## Reproductibilité

Toutes les simulations prennent une `graine`. Dans `jouer`, l'agent Bleu reçoit la graine `2g` et Rouge `2g+1`. Les temps de décision sont mesurés hors affichage.
