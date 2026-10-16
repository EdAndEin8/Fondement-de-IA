"""Interface en ligne de commande.

Exemples :
    uv run course-balise cartes
    uv run course-balise afficher exemple_7x7
    uv run course-balise jouer exemple_7x7 --bleu aleatoire --rouge aleatoire --animation
"""

from __future__ import annotations

import argparse

from .affichage import afficher, legende_symboles
from .agents import AgentAleatoire
from .carte import charger_carte, lister_cartes
from .etat import BLEU, ROUGE
from .jeu import jouer

AGENTS = {
    "aleatoire": AgentAleatoire,
}


def creer_agent(nom: str):
    try:
        return AGENTS[nom]()
    except KeyError:
        raise SystemExit(f"agent inconnu : {nom} (choix : {', '.join(AGENTS)})")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="course-balise", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="commande", required=True)

    sub.add_parser("cartes", help="lister les cartes disponibles")

    p_aff = sub.add_parser("afficher", help="afficher une carte")
    p_aff.add_argument("carte")

    p_jeu = sub.add_parser("jouer", help="simuler une partie")
    p_jeu.add_argument("carte")
    p_jeu.add_argument("--bleu", default="aleatoire")
    p_jeu.add_argument("--rouge", default="aleatoire")
    p_jeu.add_argument("--graine", type=int, default=0)
    p_jeu.add_argument("--rouge-commence", action="store_true")
    p_jeu.add_argument("--animation", action="store_true", help="animation ASCII en place")
    p_jeu.add_argument("--delai", type=float, default=0.3)

    args = parser.parse_args(argv)

    if args.commande == "cartes":
        print("\n".join(lister_cartes()))
    elif args.commande == "afficher":
        carte = charger_carte(args.carte)
        from .etat import etat_initial
        print(afficher(etat_initial(carte), carte, entete=False))
        print(legende_symboles())
    elif args.commande == "jouer":
        carte = charger_carte(args.carte)
        r = jouer(
            creer_agent(args.bleu),
            creer_agent(args.rouge),
            carte,
            graine=args.graine,
            premier=ROUGE if args.rouge_commence else BLEU,
            affichage=not args.animation,
            animation=args.animation,
            delai=args.delai,
        )
        print(f"Temps moyen de décision : Bleu {r.temps_moyen(BLEU) * 1000:.2f} ms, "
              f"Rouge {r.temps_moyen(ROUGE) * 1000:.2f} ms")


if __name__ == "__main__":
    main()
