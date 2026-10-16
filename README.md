# Fondement-de-IA

Projet de TP — *Intelligence artificielle : Fondements* (4e année du cycle FISA ICy, INSA Hauts-de-France, 2026–2027, A. Daoud).

Groupe :

| Membre | GitHub | Parties prises en charge (séance 1) |
|---|---|---|
| Anton Dion | EdAndEin8 | modélisation, règles et tests, organisation du dépôt |
| Matthieu Meunier | Omicr0ne | recherche (BFS, UCS, DFS, A*), heuristiques, comparaison |
| Sean Persand | SPUPH | affichage, boucle de jeu, agents, générateur de cartes |

Deux robots, Bleu et Rouge, se disputent une balise dans un labyrinthe avec murs, clés et portes. Le projet couvre la recherche dans un espace d'états, la représentation des connaissances, la décision adversariale (Min-Max, Alpha-Bêta), l'information partielle et une campagne d'évaluation.

## Avancement

| Partie | Contenu | État |
|---|---|---|
| Simulateur | carte, état, règles R1–R8, affichage ASCII, `jouer()` | fait (séance 1) |
| I — Recherche | BFS, UCS, DFS, A* (3 heuristiques), expériences | fait (séance 1) |
| II — Connaissances | base de faits, règles, chaînage avant | à venir |
| III — Adversarial | Min-Max, Alpha-Bêta, approfondissement itératif | séance 2 |
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

uv run python experiences/comparaison_recherche.py            # Partie I -> resultats/
uv run python experiences/plan_fige.py salle_fermee
```

Agents disponibles : `aleatoire`, `astar` (heuristique « clés »), `astar-manhattan`.

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
  agents/                  aléatoire, planificateur A*
  cli.py                   ligne de commande
tests/                     pytest (règles, partie, recherche)
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
