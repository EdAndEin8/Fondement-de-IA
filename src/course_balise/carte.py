"""Carte du jeu : paramètres immuables (dimensions, murs, portes initiales, clés initiales, balise).

Format texte d'une carte (une ligne par rangée y, un caractère par colonne x) :

    #  mur                 .  case libre
    B  départ du robot Bleu R  départ du robot Rouge
    K  clé                 D  porte verrouillée
    G  balise

Les lignes vides et celles commençant par ``%`` sont ignorées (commentaires).
L'origine (0, 0) est en haut à gauche ; x croît vers la droite, y vers le bas.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

type Pos = tuple[int, int]

#: Déplacements autorisés (R2) : nom de l'action -> (dx, dy).
DIRECTIONS: dict[str, Pos] = {
    "N": (0, -1),
    "S": (0, 1),
    "O": (-1, 0),
    "E": (1, 0),
}

SYMBOLES_VALIDES = set("#.BRKDG")


class CarteInvalide(ValueError):
    """Levée quand le texte d'une carte ne respecte pas le format attendu."""


@dataclass(frozen=True, slots=True)
class Carte:
    largeur: int
    hauteur: int
    murs: frozenset[Pos]
    portes: frozenset[Pos]
    cles: frozenset[Pos]
    balise: Pos
    depart_bleu: Pos
    depart_rouge: Pos
    nom: str = "sans_nom"

    # ------------------------------------------------------------------ requêtes
    def dans_grille(self, p: Pos) -> bool:
        x, y = p
        return 0 <= x < self.largeur and 0 <= y < self.hauteur

    def est_mur(self, p: Pos) -> bool:
        return p in self.murs

    def praticable(self, p: Pos) -> bool:
        """Case dans la grille et non murée (les portes sont gérées par les règles)."""
        return self.dans_grille(p) and p not in self.murs

    def voisins(self, p: Pos) -> list[tuple[str, Pos]]:
        """Voisins orthogonaux praticables, avec la direction qui y mène."""
        x, y = p
        res = []
        for nom, (dx, dy) in DIRECTIONS.items():
            q = (x + dx, y + dy)
            if self.praticable(q):
                res.append((nom, q))
        return res

    def cases(self):
        for y in range(self.hauteur):
            for x in range(self.largeur):
                yield (x, y)

    # ------------------------------------------------------------- construction
    @classmethod
    def depuis_texte(cls, texte: str, nom: str = "sans_nom") -> Carte:
        lignes = [
            l.rstrip("\n").rstrip()
            for l in texte.splitlines()
            if l.strip() and not l.lstrip().startswith("%")
        ]
        if not lignes:
            raise CarteInvalide("carte vide")
        largeur = len(lignes[0])
        if any(len(l) != largeur for l in lignes):
            raise CarteInvalide("toutes les lignes doivent avoir la même longueur")

        murs, portes, cles = set(), set(), set()
        bleu = rouge = balise = None
        for y, ligne in enumerate(lignes):
            for x, c in enumerate(ligne):
                if c not in SYMBOLES_VALIDES:
                    raise CarteInvalide(f"symbole inconnu {c!r} en ({x}, {y})")
                p = (x, y)
                match c:
                    case "#":
                        murs.add(p)
                    case "D":
                        portes.add(p)
                    case "K":
                        cles.add(p)
                    case "B":
                        if bleu is not None:
                            raise CarteInvalide("plusieurs départs Bleu")
                        bleu = p
                    case "R":
                        if rouge is not None:
                            raise CarteInvalide("plusieurs départs Rouge")
                        rouge = p
                    case "G":
                        if balise is not None:
                            raise CarteInvalide("plusieurs balises")
                        balise = p
        if bleu is None or rouge is None or balise is None:
            raise CarteInvalide("la carte doit contenir B, R et G")

        return cls(
            largeur=largeur,
            hauteur=len(lignes),
            murs=frozenset(murs),
            portes=frozenset(portes),
            cles=frozenset(cles),
            balise=balise,
            depart_bleu=bleu,
            depart_rouge=rouge,
            nom=nom,
        )

    @classmethod
    def depuis_fichier(cls, chemin: str | Path) -> Carte:
        chemin = Path(chemin)
        return cls.depuis_texte(chemin.read_text(encoding="utf-8"), nom=chemin.stem)


DOSSIER_CARTES = Path(__file__).resolve().parents[2] / "cartes"


def charger_carte(nom_ou_chemin: str | Path) -> Carte:
    """Charge une carte par chemin, ou par nom dans le dossier ``cartes/``."""
    p = Path(nom_ou_chemin)
    if p.exists():
        return Carte.depuis_fichier(p)
    candidat = DOSSIER_CARTES / (p.name if p.suffix else f"{p.name}.txt")
    if candidat.exists():
        return Carte.depuis_fichier(candidat)
    raise FileNotFoundError(f"carte introuvable : {nom_ou_chemin}")


def lister_cartes() -> list[str]:
    return sorted(f.stem for f in DOSSIER_CARTES.glob("*.txt"))
