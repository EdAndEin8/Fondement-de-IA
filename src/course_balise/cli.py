"""Interface en ligne de commande.

Exemples :
    uv run fondement-de-ia cartes
    uv run fondement-de-ia afficher exemple_7x7
    uv run fondement-de-ia chemin porte_raccourci --algo astar --heuristique cles
    uv run fondement-de-ia jouer exemple_7x7 --bleu astar --rouge aleatoire --animation
    uv run fondement-de-ia jouer salle_fermee --bleu alphabeta-d6 --rouge minmax-d4
    uv run fondement-de-ia decider exemple_7x7 --profondeur 6
    uv run fondement-de-ia raisonner salle_fermee
    uv run fondement-de-ia decouvrir labyrinthe_11x11 --rayon 1
    uv run fondement-de-ia jouer arene_9x9 --bleu explorateur --rouge astar

Agents : aleatoire, astar, astar-manhattan, minmax-dN, alphabeta-dN,
alphabeta+-dN (évaluation améliorée), iteratif-Nms (Alpha-Bêta itératif,
budget de N millisecondes par coup).
Information partielle (Partie IV) : explorateur, optimiste-dN, avec les
suffixes facultatifs -rN (rayon de vue N, 1 par défaut) et -g (position de
la balise connue dès le départ), par exemple explorateur-r2-g.
"""

from __future__ import annotations

import argparse
import re

from .affichage import afficher, legende_symboles
from .agents import (AgentAleatoire, AgentAlphaBeta, AgentAlphaBetaAmeliore,
                     AgentAlphaBetaIteratif, AgentAlphaBetaOptimiste, AgentAStar,
                     AgentExplorateur, AgentMinMax)
from .carte import charger_carte, lister_cartes
from .etat import BLEU, ROUGE
from .jeu import jouer

AGENTS = {
    "aleatoire": AgentAleatoire,
    "astar": AgentAStar,
    "astar-manhattan": lambda: AgentAStar("manhattan"),
}


def creer_agent(nom: str):
    if nom in AGENTS:
        return AGENTS[nom]()
    if m := re.fullmatch(r"minmax-d(\d+)", nom):
        return AgentMinMax(int(m[1]))
    if m := re.fullmatch(r"alphabeta-d(\d+)", nom):
        return AgentAlphaBeta(int(m[1]))
    if m := re.fullmatch(r"alphabeta\+-d(\d+)", nom):
        return AgentAlphaBetaAmeliore(int(m[1]))
    if m := re.fullmatch(r"iteratif-(\d+)ms", nom):
        return AgentAlphaBetaIteratif(int(m[1]) / 1000)
    if m := re.fullmatch(r"(explorateur|optimiste-d(\d+))(?:-r(\d+))?(-g)?", nom):
        rayon = int(m[3]) if m[3] else 1
        if m[2]:
            return AgentAlphaBetaOptimiste(int(m[2]), rayon, bool(m[4]))
        return AgentExplorateur(rayon, bool(m[4]))
    raise SystemExit(f"agent inconnu : {nom} (voir --help)")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="fondement-de-ia", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="commande", required=True)

    sub.add_parser("cartes", help="lister les cartes disponibles")

    p_aff = sub.add_parser("afficher", help="afficher une carte")
    p_aff.add_argument("carte")

    p_ch = sub.add_parser("chemin", help="chercher un chemin vers la balise (Partie I)")
    p_ch.add_argument("carte")
    p_ch.add_argument("--algo", choices=["bfs", "ucs", "dfs", "astar"], default="astar")
    p_ch.add_argument("--heuristique", choices=["nulle", "manhattan", "relaxee", "cles"],
                      default="manhattan")
    p_ch.add_argument("--robot", choices=["B", "R"], default="B")

    p_dec = sub.add_parser("decider", help="détail d'une décision Min-Max / Alpha-Bêta")
    p_dec.add_argument("carte")
    p_dec.add_argument("--profondeur", type=int, default=4)
    p_dec.add_argument("--ameliore", action="store_true", help="évaluation E+")
    p_dec.add_argument("--rouge-commence", action="store_true")

    p_rai = sub.add_parser("raisonner", help="base de faits et conclusions déduites (Partie II)")
    p_rai.add_argument("carte")
    p_rai.add_argument("--rouge-commence", action="store_true")

    p_dec2 = sub.add_parser("decouvrir",
                            help="course d'un robot seul qui découvre la carte (Partie IV)")
    p_dec2.add_argument("carte")
    p_dec2.add_argument("--rayon", type=int, default=1)
    p_dec2.add_argument("--balise-connue", action="store_true")
    p_dec2.add_argument("--robot", choices=["B", "R"], default="B")

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
    elif args.commande == "chemin":
        from .etat import etat_initial
        from .recherche import HEURISTIQUES, ProblemeChemin, astar, bfs, dfs, ucs
        carte = charger_carte(args.carte)
        etat = etat_initial(carte)
        pb = ProblemeChemin.depuis_etat(carte, etat, args.robot)
        if args.algo == "astar":
            r = astar(pb, HEURISTIQUES[args.heuristique](carte), f"A* {args.heuristique}")
        else:
            r = {"bfs": bfs, "ucs": ucs, "dfs": dfs}[args.algo](pb)
        print(afficher(etat, carte, entete=False, chemin=r.positions()[1:-1]))
        if r.trouve:
            print(f"{r.algorithme} : {r.longueur} coups : {' '.join(r.actions)}")
        else:
            print(f"{r.algorithme} : aucun chemin")
        print(f"nœuds développés : {r.noeuds_developpes}, générés : {r.noeuds_generes}, "
              f"temps : {r.temps * 1000:.3f} ms")
    elif args.commande == "decider":
        from .adversarial.evaluation import POIDS_AMELIORES, POIDS_BASE, Evaluation
        from .adversarial.minimax import alphabeta, minimax
        from .regles import Jeu
        jeu = Jeu(charger_carte(args.carte))
        etat = jeu.etat_initial(ROUGE if args.rouge_commence else BLEU)
        ev = Evaluation(jeu.carte, POIDS_AMELIORES if args.ameliore else POIDS_BASE)
        print(afficher(etat, jeu.carte))
        print(f"E(s) = {ev(etat):.0f}  {ev.termes(etat)}")
        for nom, f in (("Min-Max", minimax), ("Alpha-Bêta", alphabeta)):
            d = f(jeu, etat, args.profondeur, ev)
            print(f"{nom:<10} d={args.profondeur} : action {d.action}, valeur {d.valeur:.0f}, "
                  f"{d.stats.noeuds} nœuds, {d.stats.temps * 1000:.1f} ms")
    elif args.commande == "raisonner":
        from .etat import NOMS
        from .raisonnement import ROBOT, BaseConnaissances, format_fait
        carte = charger_carte(args.carte)
        from .etat import etat_initial
        etat = etat_initial(carte, ROUGE if args.rouge_commence else BLEU)
        bc = BaseConnaissances(carte, etat)
        r = ROBOT[etat.joueur]
        print(afficher(etat, carte))
        print(f"Trait à {NOMS[etat.joueur]} ({r}).")
        print(f"\nFaits observés : {len(bc.faits_base)} ; "
              f"faits déduits : {len(bc.faits_deduits())}.")
        for predicat in ("deplacement_possible", "peut_ouvrir", "peut_ramasser",
                         "coup_gagnant", "interdit"):
            conclusions = [f for f in bc.requete(predicat) if f[1] == r]
            if conclusions:
                print(f"\n{predicat} :")
                for f in conclusions:
                    print(f"  {format_fait(f)}")
        deplacements = [f for f in bc.requete("deplacement_possible") if f[1] == r]
        if deplacements:
            print(f"\nJustification de {format_fait(deplacements[0])} :")
            print(bc.expliquer(deplacements[0]))
    elif args.commande == "decouvrir":
        from .partiel.solo import course_solo
        carte = charger_carte(args.carte)
        agent = AgentExplorateur(args.rayon, args.balise_connue)
        complet = course_solo(AgentAStar(), carte, args.robot)
        r = course_solo(agent, carte, args.robot)
        print(f"Carte connue par {agent} à la fin de la course :")
        print(agent.memoire.afficher(r.positions[-1]))
        total = carte.largeur * carte.hauteur
        print(f"\n{'arrivé' if r.arrive else 'non arrivé'} en {r.pas} pas "
              f"(carte complète : {complet.pas}), cases connues : "
              f"{agent.memoire.nb_connues()}/{total}, décisions : {agent.modes}")
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
