import random
import time
from board import (
    ROWS, COLS, VIDE, JOUEUR, IA,
    creer_plateau, placer_jeton, obtenir_ligne_libre,
    colonne_valide, colonnes_valides,
    verifier_victoire, plateau_plein, score_plateau
)

# ══════════════════════════════════════════════════════════════
#
#   FICHIER : ai.py
#   CONTENU : L'intelligence artificielle du Puissance 4
#
#   PARTIE 1 — Minimax SANS élagage α-β  (version simple)
#   PARTIE 2 — Minimax AVEC élagage α-β  (version optimisée)
#   PARTIE 3 — Mesure et comparaison des performances
#
# ══════════════════════════════════════════════════════════════


# ──────────────────────────────────────────────────────────────
#  PARTIE 1 : MINIMAX SANS ÉLAGAGE α-β
#
#  Comment ça marche ?
#  - L'IA imagine TOUS les coups possibles
#  - Pour chaque coup, elle imagine la réponse du joueur
#  - Et ainsi de suite jusqu'à la profondeur demandée
#  - Elle choisit le coup qui mène au meilleur résultat
#
#  On appelle ça un "arbre de jeu" :
#       [Plateau actuel]
#       /    |    |    \
#    Col0  Col1  Col2  Col3  ← coups possibles de l'IA
#    /|\   /|\              ← réponses du joueur
#   ...  ...               ← et ainsi de suite
#
#  Complexité : O(b^d)  où b=7 colonnes, d=profondeur
#  À profondeur 5 : 7^5 = 16 807 états à explorer
# ──────────────────────────────────────────────────────────────

def minimax_simple(plateau, profondeur, ia_joue):
    """
    Minimax SANS élagage alpha-bêta.

    Paramètres :
      plateau    → l'état actuel du jeu (tableau 6×7)
      profondeur → combien de coups en avance on regarde
      ia_joue    → True si c'est au tour de l'IA de jouer
                   False si c'est au tour du joueur humain

    Retourne :
      (colonne, score) → la meilleure colonne et son score
    """

    # ── Cas d'arrêt (conditions terminales) ──
    # On s'arrête si quelqu'un a gagné OU si la profondeur est 0

    if verifier_victoire(plateau, IA):
        return (None, 100000)          # l'IA a gagné → très bon score

    if verifier_victoire(plateau, JOUEUR):
        return (None, -100000)         # le joueur a gagné → très mauvais score

    if plateau_plein(plateau):
        return (None, 0)               # match nul → score 0

    if profondeur == 0:
        # On a atteint la limite : on évalue le plateau tel quel
        return (None, score_plateau(plateau, IA))

    # ── Liste des colonnes où on peut jouer ──
    cols_disponibles = colonnes_valides(plateau)

    # ── Tour de l'IA : elle cherche le MAXIMUM ──
    if ia_joue:
        meilleur_score  = -999999       # commence très bas
        meilleure_col   = cols_disponibles[0]

        for col in cols_disponibles:
            # Simule ce coup dans une copie du plateau
            ligne = obtenir_ligne_libre(plateau, col)
            plateau_copie = plateau.copy()
            placer_jeton(plateau_copie, ligne, col, IA)

            # Appel récursif : maintenant c'est au joueur de répondre
            _, score = minimax_simple(plateau_copie, profondeur - 1, False)

            # Garde le coup avec le meilleur score
            if score > meilleur_score:
                meilleur_score = score
                meilleure_col  = col

        return (meilleure_col, meilleur_score)

    # ── Tour du JOUEUR : il cherche le MINIMUM (le pire pour l'IA) ──
    else:
        meilleur_score  = 999999        # commence très haut
        meilleure_col   = cols_disponibles[0]

        for col in cols_disponibles:
            ligne = obtenir_ligne_libre(plateau, col)
            plateau_copie = plateau.copy()
            placer_jeton(plateau_copie, ligne, col, JOUEUR)

            # Appel récursif : maintenant c'est à l'IA de répondre
            _, score = minimax_simple(plateau_copie, profondeur - 1, True)

            # Garde le coup avec le score le plus bas (pire pour l'IA)
            if score < meilleur_score:
                meilleur_score = score
                meilleure_col  = col

        return (meilleure_col, meilleur_score)


# ──────────────────────────────────────────────────────────────
#  PARTIE 2 : MINIMAX AVEC ÉLAGAGE α-β  (version optimisée)
#
#  Le problème de Minimax simple :
#  → Il explore TOUTES les branches, même celles inutiles.
#
#  L'élagage α-β coupe les branches qu'on n'a pas besoin
#  d'explorer car elles ne peuvent PAS changer le résultat.
#
#  Comment ?
#  → alpha = meilleur score garanti pour l'IA jusqu'ici
#  → beta  = meilleur score garanti pour le joueur jusqu'ici
#  → Si alpha >= beta → inutile de continuer cette branche !
#
#  Complexité : O(b^(d/2)) au lieu de O(b^d)
#  → À profondeur 5 : √(7^5) ≈ 130 états au lieu de 16 807 !
# ──────────────────────────────────────────────────────────────

def minimax_alphabeta(plateau, profondeur, alpha, beta, ia_joue):
    """
    Minimax AVEC élagage alpha-bêta.

    Paramètres supplémentaires vs minimax_simple :
      alpha → meilleur score que l'IA est sûre d'obtenir
              (commence à -infini, monte au fil de l'exploration)
      beta  → meilleur score que le joueur est sûr d'obtenir
              (commence à +infini, descend au fil de l'exploration)

    La règle d'élagage :
      Si alpha >= beta → on coupe (break) car cette branche
      ne sera jamais choisie par le joueur rationnel.
    """

    # ── Cas d'arrêt (identiques à minimax_simple) ──
    if verifier_victoire(plateau, IA):
        return (None, 100000)

    if verifier_victoire(plateau, JOUEUR):
        return (None, -100000)

    if plateau_plein(plateau):
        return (None, 0)

    if profondeur == 0:
        return (None, score_plateau(plateau, IA))

    cols_disponibles = colonnes_valides(plateau)

    # ── Tour de l'IA : cherche le MAXIMUM ──
    if ia_joue:
        meilleur_score = -999999
        meilleure_col  = cols_disponibles[0]

        for col in cols_disponibles:
            ligne = obtenir_ligne_libre(plateau, col)
            plateau_copie = plateau.copy()
            placer_jeton(plateau_copie, ligne, col, IA)

            _, score = minimax_alphabeta(
                plateau_copie, profondeur - 1,
                alpha, beta,
                False                          # tour du joueur après
            )

            if score > meilleur_score:
                meilleur_score = score
                meilleure_col  = col

            # Met à jour alpha
            alpha = max(alpha, score)

            # ★ ÉLAGAGE ★ : le joueur ne choisira jamais cette branche
            if alpha >= beta:
                break                          # coupe ! inutile de continuer

        return (meilleure_col, meilleur_score)

    # ── Tour du JOUEUR : cherche le MINIMUM ──
    else:
        meilleur_score = 999999
        meilleure_col  = cols_disponibles[0]

        for col in cols_disponibles:
            ligne = obtenir_ligne_libre(plateau, col)
            plateau_copie = plateau.copy()
            placer_jeton(plateau_copie, ligne, col, JOUEUR)

            _, score = minimax_alphabeta(
                plateau_copie, profondeur - 1,
                alpha, beta,
                True                           # tour de l'IA après
            )

            if score < meilleur_score:
                meilleur_score = score
                meilleure_col  = col

            # Met à jour beta
            beta = min(beta, score)

            # ★ ÉLAGAGE ★ : l'IA ne choisira jamais cette branche
            if alpha >= beta:
                break                          # coupe !

        return (meilleure_col, meilleur_score)


# ──────────────────────────────────────────────────────────────
#  FONCTIONS PRATIQUES pour appeler l'IA depuis le jeu
# ──────────────────────────────────────────────────────────────

def coup_ia_simple(plateau, profondeur=3):
    """
    Retourne la colonne choisie par l'IA (version sans α-β).
    Utilise profondeur 3 par défaut (va plus vite).
    """
    col, _ = minimax_simple(plateau, profondeur, True)
    return col


def coup_ia_alphabeta(plateau, profondeur=5):
    """
    Retourne la colonne choisie par l'IA (version avec α-β).
    Utilise profondeur 5 par défaut (plus fort et encore rapide).

    Niveaux de difficulté recommandés :
      Facile  → profondeur 2
      Moyen   → profondeur 4
      Expert  → profondeur 6
    """
    col, _ = minimax_alphabeta(plateau, profondeur, -999999, 999999, True)
    return col


def coup_ia_simple_ordinateur(plateau):
    """
    IA simple et rapide pour jouer contre l'ordinateur.

    Priorités :
      1. Gagner immédiatement si possible.
      2. Bloquer une victoire immédiate du joueur.
      3. Prendre le centre si disponible.
      4. Jouer une colonne proche du centre au hasard.
    """
    cols_disponibles = colonnes_valides(plateau)
    if not cols_disponibles:
        return None

    for col in cols_disponibles:
        ligne = obtenir_ligne_libre(plateau, col)
        plateau_copie = plateau.copy()
        placer_jeton(plateau_copie, ligne, col, IA)
        if verifier_victoire(plateau_copie, IA):
            return col

    for col in cols_disponibles:
        ligne = obtenir_ligne_libre(plateau, col)
        plateau_copie = plateau.copy()
        placer_jeton(plateau_copie, ligne, col, JOUEUR)
        if verifier_victoire(plateau_copie, JOUEUR):
            return col

    centre = COLS // 2
    if centre in cols_disponibles:
        return centre

    cols_disponibles.sort(key=lambda c: abs(c - centre))
    meilleures_cols = cols_disponibles[:3]
    return random.choice(meilleures_cols)


# ──────────────────────────────────────────────────────────────
#  PARTIE 3 : MESURE ET COMPARAISON DES PERFORMANCES
#
#  C'est la section la plus importante pour ton RAPPORT !
#  Elle prouve concrètement que α-β est bien plus rapide.
#  Copie les résultats dans ton rapport avec un tableau.
# ──────────────────────────────────────────────────────────────

def mesurer_performance():
    """
    Compare le temps d'exécution de Minimax avec et sans α-β
    pour différentes profondeurs. Produit un tableau de résultats
    à copier directement dans le rapport.
    """
    print("=" * 60)
    print("  COMPARAISON DE PERFORMANCE : Minimax vs Minimax + α-β")
    print("=" * 60)
    print(f"{'Profondeur':<12} {'Sans α-β (s)':<16} {'Avec α-β (s)':<16} {'Accélération'}")
    print("-" * 60)

    plateau_test = creer_plateau()
    # Plateau avec quelques jetons pour être réaliste
    placer_jeton(plateau_test, 5, 3, JOUEUR)
    placer_jeton(plateau_test, 5, 4, IA)
    placer_jeton(plateau_test, 4, 3, JOUEUR)
    placer_jeton(plateau_test, 5, 2, IA)

    resultats = []

    for profondeur in [2, 3, 4, 5]:
        # ── Mesure SANS α-β ──
        debut = time.time()
        minimax_simple(plateau_test, profondeur, True)
        temps_sans = time.time() - debut

        # ── Mesure AVEC α-β ──
        debut = time.time()
        minimax_alphabeta(plateau_test, profondeur, -999999, 999999, True)
        temps_avec = time.time() - debut

        # Calcul de l'accélération
        if temps_avec > 0:
            acceleration = temps_sans / temps_avec
        else:
            acceleration = float('inf')

        resultats.append((profondeur, temps_sans, temps_avec, acceleration))

        print(
            f"{profondeur:<12} "
            f"{temps_sans:<16.4f} "
            f"{temps_avec:<16.4f} "
            f"{acceleration:.1f}×  plus rapide"
        )

    print("=" * 60)
    print()
    print("📊 RÉSUMÉ POUR LE RAPPORT :")
    print()

    meilleur = max(resultats, key=lambda x: x[3])
    print(f"  Meilleur gain : profondeur {meilleur[0]}")
    print(f"  Sans α-β  : {meilleur[1]:.4f} secondes")
    print(f"  Avec α-β  : {meilleur[2]:.4f} secondes")
    print(f"  α-β est {meilleur[3]:.1f}× plus rapide !")
    print()
    print("  Complexité théorique :")
    print("  • Minimax seul   : O(b^d)    où b=7, d=profondeur")
    print("  • Minimax + α-β  : O(b^d/2)  soit la RACINE CARRÉE")
    print()
    print("  Exemple à profondeur 6 :")
    print("  • Sans α-β : 7^6 = 117 649 nœuds explorés")
    print("  • Avec α-β : 7^3 =     343 nœuds explorés")
    print("  → α-β réduit le travail de l'IA de 99.7% !")
    print("=" * 60)

    return resultats


# ──────────────────────────────────────────────────────────────
#  TEST RAPIDE : vérifie que l'IA joue correctement
# ──────────────────────────────────────────────────────────────

def tester_ia():
    """
    Scénario de test : l'IA doit voir qu'elle peut gagner
    et jouer un coup gagnant immédiatement.
    """
    from board import afficher_plateau

    print("=== TEST 1 : L'IA doit gagner (col 0 ou col 4 gagnent) ===\n")
    p = creer_plateau()

    # L'IA a 3 jetons en ligne [1,2,3] → col 0 ou col 4 gagnent
    placer_jeton(p, 5, 1, IA)
    placer_jeton(p, 5, 2, IA)
    placer_jeton(p, 5, 3, IA)

    afficher_plateau(p)
    col = coup_ia_alphabeta(p, profondeur=3)
    print(f"  L'IA choisit la colonne : {col}")
    # col 0 gagne (0,1,2,3 horizontalement) ou col 4 gagne (1,2,3,4)
    print(f"  Correct ? {'✅ OUI — coup gagnant !' if col in [0, 4] else '❌ NON — problème dans le code'}")
    print()

    print("=== TEST 2 : L'IA doit bloquer le joueur (col 5) ===\n")
    p2 = creer_plateau()

    # Le joueur a 3 jetons en [1,2,3], l'IA occupe col 0 → seule menace en col 4 ou 5
    # On bloque col 0 côté gauche avec un jeton IA → une seule issue pour le joueur
    placer_jeton(p2, 5, 0, IA)     # bloque le côté gauche
    placer_jeton(p2, 5, 1, JOUEUR)
    placer_jeton(p2, 5, 2, JOUEUR)
    placer_jeton(p2, 5, 3, JOUEUR)
    # Seule menace restante : col 4 (1,2,3,4 horizontalement)

    afficher_plateau(p2)
    col2 = coup_ia_alphabeta(p2, profondeur=3)
    print(f"  L'IA choisit la colonne : {col2}")
    print(f"  Correct ? {'✅ OUI — menace bloquée !' if col2 == 4 else '❌ NON — problème dans le code'}")


# ──────────────────────────────────────────────────────────────
#  POINT D'ENTRÉE : lance ce fichier pour tout tester
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tester_ia()
    print()
    mesurer_performance()
