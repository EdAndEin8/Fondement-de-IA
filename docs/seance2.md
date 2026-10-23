# Séance 2 — Décision adversariale : notes techniques

Vendredi 23 octobre 2026, 9h30–12h30. Résumé des choix de la Partie III et des résultats obtenus.

## 1. Organisation du code

| Fichier | Contenu |
|---|---|
| `adversarial/evaluation.py` | distances avec clés et portes, mobilité, E(s), E+(s) |
| `adversarial/minimax.py` | `valeur_feuille`, `minimax`, `alphabeta`, statistiques, échéance |
| `adversarial/ordre.py` | ordres d'exploration : naturel, aléatoire, meilleur d'abord, pire d'abord |
| `adversarial/iteratif.py` | approfondissement itératif avec budget de temps |
| `agents/adversariaux.py` | agents Min-Max, Alpha-Bêta, Alpha-Bêta amélioré, Alpha-Bêta itératif |

Min-Max et Alpha-Bêta appellent les mêmes fonctions `jeu.actions_legales`, `jeu.transition`, `jeu.terminal` et `valeur_feuille` (point de méthode de l'énoncé). Bleu est toujours MAX, Rouge toujours MIN ; un même agent peut donc jouer les deux couleurs.

## 2. Valeurs terminales

`+1000 − ply` si Bleu gagne, `−1000 + ply` si Rouge gagne, `0` pour un nul, où `ply` est le nombre de demi-coups depuis la racine. L'ajustement fait préférer la victoire la plus rapide et la défaite la plus lente, sans changer le signe : |U| ≥ 1000 − 80 = 920, toujours au-dessus de l'évaluation.

## 3. Fonction d'évaluation

### Distances

`dB` et `dR` estiment le nombre de pas jusqu'à G **en tenant compte des clés et des portes**, l'adversaire étant ignoré (il bouge) :
- avec une clé : distance sur la carte où les portes sont franchissables ;
- sans clé : minimum entre la distance qui évite les portes fermées et le détour par une clé au sol, `d(pos, k) + d(k, G)`.

Toutes les tables sont des BFS précalculés et mis en cache : une évaluation ne coûte que quelques accès à des dictionnaires. Un test vérifie que l'estimation est exacte sur les cartes à une seule clé.

### Normalisation et poids

    pas = 400 / Dcap      Dcap = 2 × (plus grande distance à G) + 1
    E(s) = pas × [ (dR − dB) + 0,4 (kB − kR) + 0,1 (mB − mR) ]

- `Dcap` majore toute distance finie et sert de distance pour un robot qui ne peut plus atteindre G.
- Un pas d'avance est le critère principal. La clé (0,4 pas) ne fait que départager, car elle est déjà prise en compte dans la distance. La mobilité (0,1 pas par coup possible) pénalise les culs-de-sac sans jamais compenser un pas de retard.
- Borne : |E| ≤ 400 + 50 + 0,8 pas < 920. Les valeurs terminales priment toujours (testé sur toutes les cartes).

**Deux erreurs corrigées en cours de séance.** En faisant jouer Alpha-Bêta d = 6 en Bleu contre A* sur `salle_fermee`, on obtenait un match nul au bout de 80 tours, alors qu'A* en Bleu gagne en 41 tours. Il y avait deux causes, et il a fallu corriger les deux :

1. **Saturation de l'évaluation.** La première version écrêtait l'écart `dR − dB` à ±40 avec des poids fixes (10, 4, 1). Dès que Bleu a la clé, Rouge ne peut plus gagner : `dR` devient très grand, l'écart reste au plafond quelle que soit la position de Bleu, et Bleu n'a plus aucune raison d'avancer. La normalisation par la taille de la carte garde un gradient partout (test `test_avancer_reste_utile_quand_l_adversaire_est_bloque`).
2. **Oscillation entre coups ex æquo.** Avec l'ordre naturel N, S, O, E, plusieurs coups ont la même valeur à l'horizon (par exemple avancer de deux cases puis être forcé de dépasser la porte, ou reculer puis revenir). Le premier ex æquo rencontré est O : Bleu fait des allers-retours. Trier les coups par évaluation met en tête le coup qui progresse immédiatement ; c'est devenu l'ordre par défaut des agents.

| Version de E | Ordre naturel | Ordre trié par E |
|---|---|---|
| écrêtée (première version) | nul | nul |
| normalisée | nul | victoire en 41 tours |

### Évaluation améliorée E+

Elle estime l'issue de la course vers G si personne ne gênait personne. Avec le trait, Bleu fait son `dB`-ième pas au demi-coup `2dB − 1`, Rouge le sien au demi-coup `2dR` :

- Bleu arrive le premier ⇔ `dB ≤ dR` s'il a le trait, `dB < dR` sinon ;
- le terme de distance devient `± (450 − pas × d_gagnant)`.

La valeur ne dépend plus que de la distance du robot qui gagne la course : pour lui, avancer l'améliore toujours.

## 4. Résultats

### Min-Max contre Alpha-Bêta (`resultats/minimax_alphabeta.md`)

Valeurs identiques dans **500 cas sur 500** (5 cartes × 5 états × 5 profondeurs × 4 ordres). Nœuds moyens :

| Carte | d | Min-Max | AB naturel | AB tri par E |
|---|---|---|---|---|
| exemple_7x7 | 6 | 360 | 144 | 66 |
| exemple_7x7 | 10 | 13 624 | 1 609 | 263 |
| arene_9x9 | 6 | 1 222 | 207 | 128 |
| arene_9x9 | 8 | 12 463 | 1 430 | 542 |
| arene_9x9 | 10 | 133 097 (1,9 s) | 5 557 | 1 853 (≈ 90 ms) |

- La croissance est exponentielle : facteur ≈ 3 par demi-coup dans l'arène ouverte, ≈ 2 dans les couloirs des labyrinthes.
- Alpha-Bêta avec tri par E économise 90 à 99 % des nœuds à partir de d = 6.
- À d = 2, trier coûte plus cher que ce que l'élagage fait gagner (deux évaluations par coup) : Alpha-Bêta trié est alors un peu plus lent que Min-Max.

### Ordre des coups (Alpha-Bêta, d = 8)

| Carte | Naturel | Aléatoire | Meilleur d'abord | Pire d'abord | Min-Max |
|---|---|---|---|---|---|
| exemple_7x7 | 485 | 427 | 135 | 1 053 | 1 978 |
| arene_9x9 | 1 430 | 1 440 | 542 | 4 677 | 12 463 |

L'ordre ne change pas la valeur, mais il change d'un facteur 3 à 8 le nombre de nœuds. L'ordre naturel et l'ordre aléatoire se valent ; « pire d'abord » montre ce qu'on perd avec un mauvais ordre.

### Approfondissement itératif (`resultats/iteratif.md`)

- Une action légale est toujours renvoyée, même avec un budget nul : avant toute recherche, l'agent prend le meilleur coup selon E à profondeur 0.
- Le meilleur coup de l'itération d − 1 est exploré en premier à l'itération d.
- Une itération qui dépasse l'échéance est abandonnée (exception `TempsEcoule`, vérifiée tous les 64 nœuds), et on garde le coup de la dernière itération complète.
- On s'arrête aussi dès qu'une victoire ou une défaite forcée est trouvée.
- Profondeur atteinte avec 100 ms : 14 sur `salle_fermee`, 9 dans l'arène. Le dépassement de budget reste inférieur à 1 % à partir de 100 ms. Il y a environ 0,5 ms de coût fixe (coup de secours et première itération).

### Effet d'horizon (`resultats/horizon.md`)

Situation : Bleu a la clé, devant la porte de `salle_fermee`, Rouge est loin.

- Ouvrir la porte (N) gagne en 3 coups (5 demi-coups). Mais cela consomme la clé et ouvre aussi le passage à Rouge, qui n'a plus besoin de clé : avec E, la valeur passe de 371 à 126.
- À profondeur ≤ 4, la victoire est au-delà de l'horizon : Bleu ne voit que la chute de l'évaluation et refuse d'ouvrir, partie après partie, jusqu'au nul à 80 tours. À d = 5, il voit la victoire (995).
- En partie, Alpha-Bêta d ≤ 4 avec E fait **10 nuls sur 10 contre un joueur aléatoire** sur `salle_fermee`. Avec E+, il gagne 10 fois sur 10 dès d = 2.
- Sur `porte_raccourci`, le même défaut ne fait que retarder la victoire (18 tours au lieu de 13).

Remèdes possibles :
1. une meilleure évaluation (E+) ;
2. une recherche plus profonde (l'approfondissement itératif atteint d ≥ 8 en quelques ms ici) ;
3. une extension de recherche quand un coup modifie fortement l'évaluation (recherche de quiescence, non implémentée).

## 5. Remarques diverses

- Les cartes sont symétriques : à force égale, le joueur qui commence gagne presque toujours. Il faudra alterner le premier joueur dans la campagne d'évaluation (Partie V).
- Sur `grand_labyrinthe_25x25`, chaque robot a besoin de plus de 60 pas : la limite de 80 tours (40 coups chacun) rend toute victoire impossible et toutes les parties sont nulles. Cette carte sert pour la Partie I, pas pour les confrontations.
- Pour l'ordre aléatoire, `hash()` ne convient pas pour la graine : il est randomisé d'une exécution Python à l'autre. On passe une chaîne à `random.Random`, qui est stable.
