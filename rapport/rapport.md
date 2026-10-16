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

## 4. Partie II — Connaissances et raisonnement *(à venir)*

## 5. Partie III — Décision adversariale *(séance 2)*

## 6. Partie IV — Information partielle *(à venir)*

## 7. Partie V — Campagne d'évaluation *(à venir)*

## 8. Conclusion et limites *(à rédiger)*
