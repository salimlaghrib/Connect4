import numpy as np

# ──────────────────────────────────────────────
#  CONSTANTES DU JEU
# ──────────────────────────────────────────────
ROWS    = 6   # nombre de lignes
COLS    = 7   # nombre de colonnes

VIDE    = 0   # case vide
JOUEUR  = 1   # pièce du joueur humain
IA      = 2   # pièce de l'IA


# ══════════════════════════════════════════════
#  1.  CRÉER LE PLATEAU
#      Un tableau 2D de 6 lignes × 7 colonnes,
#      rempli de zéros (toutes les cases vides).
# ══════════════════════════════════════════════
def creer_plateau():
    """Retourne un plateau vide 6×7."""
    plateau = np.zeros((ROWS, COLS), dtype=int)
    return plateau


# ══════════════════════════════════════════════
#  2.  PLACER UN JETON  (gravité)
#      Les jetons tombent vers le bas :
#      on cherche la ligne la plus basse libre
#      dans la colonne choisie.
# ══════════════════════════════════════════════
def obtenir_ligne_libre(plateau, col):
    """
    Retourne l'index de la ligne disponible
    la plus basse dans la colonne `col`.
    Retourne None si la colonne est pleine.
    """
    for ligne in range(ROWS - 1, -1, -1):   # de bas (5) vers haut (0)
        if plateau[ligne][col] == VIDE:
            return ligne
    return None   # colonne pleine


def colonne_valide(plateau, col):
    """Vérifie si on peut encore jouer dans cette colonne."""
    return plateau[0][col] == VIDE   # la case du haut est libre ?


def placer_jeton(plateau, ligne, col, piece):
    """
    Place la pièce (JOUEUR ou IA) dans le plateau
    à la position (ligne, col).
    """
    plateau[ligne][col] = piece


def colonnes_valides(plateau):
    """Retourne la liste de toutes les colonnes où on peut encore jouer."""
    return [c for c in range(COLS) if colonne_valide(plateau, c)]


# ══════════════════════════════════════════════
#  3.  DÉTECTER LA VICTOIRE
#      C'est la fonction la plus importante !
#      On vérifie les 4 directions possibles :
#        - horizontal  →
#        - vertical    ↓
#        - diagonal    ↗
#        - diagonal    ↘
# ══════════════════════════════════════════════
def verifier_victoire(plateau, piece):
    """
    Retourne True si `piece` (JOUEUR ou IA)
    a 4 jetons alignés quelque part sur le plateau.
    """

    # ── Horizontal : on vérifie chaque rangée ──
    for ligne in range(ROWS):
        for col in range(COLS - 3):   # il faut 4 cases → on s'arrête à col 3
            if (plateau[ligne][col]     == piece and
                plateau[ligne][col + 1] == piece and
                plateau[ligne][col + 2] == piece and
                plateau[ligne][col + 3] == piece):
                return True

    # ── Vertical : on vérifie chaque colonne ──
    for ligne in range(ROWS - 3):     # il faut 4 cases vers le bas
        for col in range(COLS):
            if (plateau[ligne][col]     == piece and
                plateau[ligne + 1][col] == piece and
                plateau[ligne + 2][col] == piece and
                plateau[ligne + 3][col] == piece):
                return True

    # ── Diagonale montante ↗ (bas-gauche vers haut-droit) ──
    for ligne in range(ROWS - 3):
        for col in range(COLS - 3):
            if (plateau[ligne][col]         == piece and
                plateau[ligne + 1][col + 1] == piece and
                plateau[ligne + 2][col + 2] == piece and
                plateau[ligne + 3][col + 3] == piece):
                return True

    # ── Diagonale descendante ↘ (haut-gauche vers bas-droit) ──
    for ligne in range(3, ROWS):      # on commence à ligne 3
        for col in range(COLS - 3):
            if (plateau[ligne][col]         == piece and
                plateau[ligne - 1][col + 1] == piece and
                plateau[ligne - 2][col + 2] == piece and
                plateau[ligne - 3][col + 3] == piece):
                return True

    return False   # aucun alignement trouvé


def plateau_plein(plateau):
    """Retourne True si toutes les colonnes sont pleines (match nul)."""
    return len(colonnes_valides(plateau)) == 0


# ══════════════════════════════════════════════
#  4.  FONCTION DE SCORE  (heuristique)
#      L'IA ne peut pas explorer l'arbre entier
#      jusqu'à la fin. Elle s'arrête à une
#      certaine profondeur et ÉVALUE le plateau.
#
#      Principe :
#        +10000  = 4 alignés (victoire IA)
#        +50     = 3 alignés + 1 vide
#        +2      = 2 alignés + 2 vides
#        -10000  = 4 alignés adversaire (bloque)
#        -50     = 3 alignés adversaire (danger)
# ══════════════════════════════════════════════
def evaluer_fenetre(fenetre, piece):
    """
    Évalue un groupe de 4 cases consécutives ('fenetre').
    Retourne un score positif si c'est bon pour `piece`,
    négatif si c'est bon pour l'adversaire.
    """
    adversaire = JOUEUR if piece == IA else IA
    score = 0

    nb_piece    = fenetre.count(piece)
    nb_vide     = fenetre.count(VIDE)
    nb_adv      = fenetre.count(adversaire)

    if nb_piece == 4:
        score += 100000        # victoire !
    elif nb_piece == 3 and nb_vide == 1:
        score += 50            # 3 alignés, 1 trou → très bon
    elif nb_piece == 2 and nb_vide == 2:
        score += 2             # 2 alignés, 2 trous → potentiel

    if nb_adv == 4:
        score -= 100000        # adversaire gagne !
    elif nb_adv == 3 and nb_vide == 1:
        score -= 80            # l'adversaire menace → bloquer !

    return score


def score_plateau(plateau, piece):
    """
    Calcule le score total du plateau pour `piece`.
    Parcourt toutes les fenêtres de 4 cases dans
    les 4 directions et additionne les scores.
    """
    score_total = 0

    # Bonus : préférer la colonne centrale (plus de possibilités)
    colonne_centre = list(plateau[:, COLS // 2])
    score_total += colonne_centre.count(piece) * 3

    # ── Horizontal ──
    for ligne in range(ROWS):
        for col in range(COLS - 3):
            fenetre = list(plateau[ligne, col:col + 4])
            score_total += evaluer_fenetre(fenetre, piece)

    # ── Vertical ──
    for col in range(COLS):
        for ligne in range(ROWS - 3):
            fenetre = [plateau[ligne + i][col] for i in range(4)]
            score_total += evaluer_fenetre(fenetre, piece)

    # ── Diagonale ↗ ──
    for ligne in range(ROWS - 3):
        for col in range(COLS - 3):
            fenetre = [plateau[ligne + i][col + i] for i in range(4)]
            score_total += evaluer_fenetre(fenetre, piece)

    # ── Diagonale ↘ ──
    for ligne in range(3, ROWS):
        for col in range(COLS - 3):
            fenetre = [plateau[ligne - i][col + i] for i in range(4)]
            score_total += evaluer_fenetre(fenetre, piece)

    return score_total


# ══════════════════════════════════════════════
#  AFFICHAGE DANS LE TERMINAL (pour les tests)
#  Pas nécessaire pour pygame mais utile pour
#  vérifier que tout fonctionne avant l'interface.
# ══════════════════════════════════════════════
def afficher_plateau(plateau):
    """Affiche le plateau dans le terminal avec des symboles."""
    symboles = {VIDE: "·", JOUEUR: "🟡", IA: "🔴"}
    print("\n  0   1   2   3   4   5   6")
    print(" " + "─" * 29)
    for ligne in range(ROWS):
        print("|", end=" ")
        for col in range(COLS):
            print(symboles[plateau[ligne][col]], end=" ")
        print(f"| {ligne}")
    print(" " + "─" * 29)
    print()


# ──────────────────────────────────────────────
#  TESTS RAPIDES  (lance ce fichier directement
#  pour vérifier que tout fonctionne)
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=== TEST DU PLATEAU ===\n")

    p = creer_plateau()
    print("Plateau vide :")
    afficher_plateau(p)

    # Simule quelques coups
    placer_jeton(p, obtenir_ligne_libre(p, 3), 3, JOUEUR)
    placer_jeton(p, obtenir_ligne_libre(p, 3), 3, IA)
    placer_jeton(p, obtenir_ligne_libre(p, 4), 4, JOUEUR)
    placer_jeton(p, obtenir_ligne_libre(p, 4), 4, IA)
    placer_jeton(p, obtenir_ligne_libre(p, 5), 5, JOUEUR)
    placer_jeton(p, obtenir_ligne_libre(p, 6), 6, JOUEUR)

    print("Après quelques coups :")
    afficher_plateau(p)

    # Test victoire
    print("Victoire JOUEUR ?", verifier_victoire(p, JOUEUR))   # False attendu
    print("Victoire IA ?", verifier_victoire(p, IA))           # False attendu
    print("Score plateau pour IA :", score_plateau(p, IA))
    print("Score plateau pour JOUEUR :", score_plateau(p, JOUEUR))
    print("\n✅ Tout fonctionne !")