"""Génère un grand labyrinthe reproductible (graine fixée) pour la Partie I.

Labyrinthe parfait par exploration en profondeur aléatoire, puis ouverture
d'une fraction des murs pour créer des cycles. La balise est au centre, dans
une salle fermée par deux portes ; deux clés sont placées dans le labyrinthe.
Une carte générée doit être vérifiée (les tests exigent un chemin vers G pour
chaque robot) : certaines graines placent les clés hors de portée.

Usage :
    uv run python outils/generer_labyrinthe.py --taille 25 --graine 27 > cartes/grand_labyrinthe_25x25.txt
"""

from __future__ import annotations

import argparse
import random


def generer(n: int, graine: int, cycles: float = 0.08) -> list[list[str]]:
    assert n % 2 == 1 and n >= 11, "taille impaire >= 11"
    rng = random.Random(graine)
    g = [["#"] * n for _ in range(n)]

    # Labyrinthe parfait sur les cases impaires.
    pile = [(1, 1)]
    g[1][1] = "."
    while pile:
        x, y = pile[-1]
        voisins = [(x + dx, y + dy, dx, dy) for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))
                   if 0 < x + dx < n - 1 and 0 < y + dy < n - 1 and g[y + dy][x + dx] == "#"]
        if not voisins:
            pile.pop()
            continue
        nx, ny, dx, dy = rng.choice(voisins)
        g[y + dy // 2][x + dx // 2] = "."
        g[ny][nx] = "."
        pile.append((nx, ny))

    # Cycles : on abat quelques murs séparant deux couloirs.
    for y in range(1, n - 1):
        for x in range(1, n - 1):
            if g[y][x] == "#" and rng.random() < cycles:
                if (g[y][x - 1] == g[y][x + 1] == ".") or (g[y - 1][x] == g[y + 1][x] == "."):
                    g[y][x] = "."

    # Salle centrale 3x3 entourée de murs, deux portes (haut et bas).
    c = n // 2
    for y in range(c - 2, c + 3):
        for x in range(c - 2, c + 3):
            g[y][x] = "." if abs(x - c) <= 1 and abs(y - c) <= 1 else "#"
    g[c][c] = "G"
    g[c - 2][c] = "D"
    g[c + 2][c] = "D"
    g[c - 3][c] = g[c + 3][c] = "."

    g[1][1] = "B"
    g[n - 2][n - 2] = "R"
    libres = [(x, y) for y in range(n) for x in range(n)
              if g[y][x] == "." and abs(x - c) > 3 and abs(y - c) > 3]
    for x, y in rng.sample(libres, 2):
        g[y][x] = "K"
    return g


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--taille", type=int, default=25)
    p.add_argument("--graine", type=int, default=27)
    a = p.parse_args()
    print(f"% Labyrinthe généré : outils/generer_labyrinthe.py --taille {a.taille} --graine {a.graine}")
    for ligne in generer(a.taille, a.graine):
        print("".join(ligne))


if __name__ == "__main__":
    main()
