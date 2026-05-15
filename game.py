import sys
import time
import math

import pygame

from board import (
    ROWS, COLS, VIDE, JOUEUR, IA,
    creer_plateau, placer_jeton, obtenir_ligne_libre,
    colonne_valide, colonnes_valides,
    verifier_victoire, plateau_plein
)
from ai import coup_ia_alphabeta, coup_ia_simple_ordinateur


pygame.init()

# ─── Fenêtre ───────────────────────────────────────────────────
CELL    = 82
RAYON   = CELL // 2 - 8          # jetons plus grands
BOARD_X = 52
BOARD_Y = 140
BOARD_W = COLS * CELL
BOARD_H = ROWS * CELL
PANEL_X = BOARD_X + BOARD_W + 36
LARGEUR = 960
HAUTEUR = 720
FPS     = 60

# ─── Palette image : gris perle / teal / marine ───────────────
FOND           = (232, 234, 240)   # fond gris perle
FOND_PANNEAU   = (245, 246, 250)

GRILLE_FOND    = (255, 255, 255)
GRILLE_BORD    = (210, 214, 224)
CASE_VIDE      = (210, 214, 222)   # gris légèrement bleuté
CASE_VIDE_OMB  = (190, 195, 207)

# Joueur : teal vert menthe
TEAL           = ( 46, 196, 160)   # #2EC4A0
TEAL_CLAIR     = ( 90, 220, 190)
TEAL_HL        = (160, 240, 220)
TEAL_FONCE     = ( 28, 155, 125)

# IA : bleu marine
MARINE         = ( 52,  68, 100)   # #344464
MARINE_CLAIR   = ( 75,  95, 135)
MARINE_HL      = (120, 145, 190)
MARINE_FONCE   = ( 35,  48,  75)

# Accents
ROSE_TITRE     = (237,  55, 155)   # rose bubbly "You Won!"
ROSE_OMBRE     = (180,  20, 110)
BLANC          = (255, 255, 255)
TEXTE_TITRE    = ( 40,  48,  70)
TEXTE_CORPS    = ( 80,  92, 115)
TEXTE_DOUX     = (150, 160, 180)
VERT_BOUTON    = ( 46, 196, 160)
ROUGE_BOUTON   = (220,  65,  65)

# ─── Polices ──────────────────────────────────────────────────
def _police(noms, taille, gras=False):
    for n in (noms if isinstance(noms, list) else [noms]):
        try:
            return pygame.font.SysFont(n, taille, bold=gras)
        except Exception:
            pass
    return pygame.font.Font(None, taille)

POLICE_TITRE = _police(["Georgia", "Arial"], 54, gras=True)
POLICE_SOUS_TITRE = _police(["Georgia", "Arial"], 22, gras=True)
POLICE_TEXTE      = _police("Arial", 20)
POLICE_TEXTE_GRAS = _police("Arial", 20, gras=True)
POLICE_PETIT      = _police("Arial", 16)
POLICE_BOUTON     = _police("Arial", 22, gras=True)
POLICE_STAT       = _police(["Georgia", "Arial"], 30, gras=True)
POLICE_CHIFFRE    = _police(["Georgia", "Arial"], 17)
POLICE_YOUWIN = _police(["Georgia", "Arial"], 72, gras=True)
POLICE_STAR       = _police(["Segoe UI Symbol", "DejaVu Sans", "Arial"], 28, gras=True)

NIVEAUX = {
    "Simple": {
        "profondeur": 1,
        "mode": "simple",
        "couleur":  TEAL,
        "couleur2": (220, 248, 242),
        "description": "Logique de base, idéal pour commencer."
    },
    "Moyen": {
        "profondeur": 4,
        "mode": "alphabeta",
        "couleur":  (195, 140, 30),
        "couleur2": (255, 248, 220),
        "description": "Minimax équilibré avec élagage α-β."
    },
    "Expert": {
        "profondeur": 6,
        "mode": "alphabeta",
        "couleur":  ROUGE_BOUTON,
        "couleur2": (255, 235, 235),
        "description": "Profondeur maximale, adversaire redoutable."
    },
}


# ═══════════════════════════════════════════════════════════════
#  UTILITAIRES
# ═══════════════════════════════════════════════════════════════

def dessiner_fond(ecran):
    ecran.fill(FOND)
    # Petite grille de points discrets
    for x in range(0, LARGEUR, 32):
        for y in range(0, HAUTEUR, 32):
            pygame.draw.circle(ecran, GRILLE_BORD, (x, y), 1)


def dessiner_texte(ecran, texte, police, couleur, pos, centre=False):
    surf = police.render(texte, True, couleur)
    rect = surf.get_rect()
    if centre:
        rect.center = pos
    else:
        rect.topleft = pos
    ecran.blit(surf, rect)
    return rect


def eclaircir(c, a): return tuple(min(255, v + a) for v in c)
def assombrir(c, a):  return tuple(max(0,   v - a) for v in c)


def ombre_rect(ecran, rect, rayon=14, decal=5, alpha=38):
    s = pygame.Surface((rect.w + decal * 2, rect.h + decal * 2), pygame.SRCALPHA)
    pygame.draw.rect(s, (0, 0, 0, alpha), s.get_rect(), border_radius=rayon + decal)
    ecran.blit(s, (rect.x - decal, rect.y + decal // 2))


def carte(ecran, rect, fond=BLANC, bord=GRILLE_BORD, rayon=16):
    ombre_rect(ecran, rect, rayon=rayon)
    pygame.draw.rect(ecran, fond, rect, border_radius=rayon)
    pygame.draw.rect(ecran, bord, rect, 1, border_radius=rayon)


def bouton(ecran, rect, texte, couleur, texte_c=BLANC, hover=False, rayon=12):
    fond = eclaircir(couleur, 20) if hover else couleur
    ombre_rect(ecran, rect, rayon=rayon, decal=3, alpha=28)
    pygame.draw.rect(ecran, fond, rect, border_radius=rayon)
    hl = pygame.Rect(rect.x + 3, rect.y + 3, rect.w - 6, 3)
    pygame.draw.rect(ecran, eclaircir(fond, 50), hl, border_radius=2)
    dessiner_texte(ecran, texte, POLICE_BOUTON, texte_c, rect.center, centre=True)


# ═══════════════════════════════════════════════════════════════
#  JETONS
# ═══════════════════════════════════════════════════════════════

def centre_case(ligne, col):
    return (
        BOARD_X + col * CELL + CELL // 2,
        BOARD_Y + ligne * CELL + CELL // 2
    )


def couleurs_piece(piece):
    if piece == JOUEUR:
        return TEAL, TEAL_CLAIR, TEAL_HL, TEAL_FONCE
    if piece == IA:
        return MARINE, MARINE_CLAIR, MARINE_HL, MARINE_FONCE
    return CASE_VIDE, CASE_VIDE, CASE_VIDE, CASE_VIDE_OMB


def dessiner_jeton(ecran, x, y, piece, rayon=RAYON, etoile=False, alpha_scale=1.0):
    """Dessine un jeton avec effet 3D sphérique et optionnellement une étoile."""
    couleur, lumiere, highlight, fonce = couleurs_piece(piece)

    # Ombre portée douce
    s = pygame.Surface((rayon * 2 + 16, rayon * 2 + 16), pygame.SRCALPHA)
    pygame.draw.circle(s, (0, 0, 0, 50), (rayon + 8, rayon + 10), rayon + 1)
    ecran.blit(s, (x - rayon - 4, y - rayon - 2))

    # Bord sombre (contour profond)
    pygame.draw.circle(ecran, fonce, (x, y + 2), rayon)

    # Corps principal
    pygame.draw.circle(ecran, couleur, (x, y), rayon)

    # Reflet latéral (dégradé simulé)
    refl = pygame.Surface((rayon * 2, rayon * 2), pygame.SRCALPHA)
    pygame.draw.circle(refl, (*lumiere, 60), (rayon, rayon - rayon // 3), rayon - 2)
    ecran.blit(refl, (x - rayon, y - rayon))

    # Point spéculaire
    pygame.draw.circle(ecran, highlight,
                       (x - rayon // 3, y - rayon // 3),
                       max(5, rayon // 5))

    # Bordure fine sur les jetons IA (distinction visuelle)
    if piece == IA:
        pygame.draw.circle(ecran, (100, 120, 155), (x, y), rayon, 1)

    # Étoile gagnante
    if etoile:
        _dessiner_etoile(ecran, x, y, rayon, piece)


def _dessiner_etoile(ecran, cx, cy, rayon, piece):
    """Dessine une étoile à 5 branches centrée sur le jeton."""
    n = 5
    ext_r = rayon * 0.52
    int_r = rayon * 0.22
    pts = []
    for i in range(n * 2):
        angle = math.pi / n * i - math.pi / 2
        r = ext_r if i % 2 == 0 else int_r
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))

    # Couleur de l'étoile : claire sur le jeton
    star_col = TEAL_CLAIR if piece == IA else MARINE
    pygame.draw.polygon(ecran, star_col, pts)
    pygame.draw.polygon(ecran, eclaircir(star_col, 40), pts, 1)


# ═══════════════════════════════════════════════════════════════
#  PLATEAU
# ═══════════════════════════════════════════════════════════════

def trouver_cases_gagnantes(plateau, joueur):
    """Retourne la liste des (ligne, col) formant la série gagnante."""
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for r in range(ROWS):
        for c in range(COLS):
            if plateau[r][c] != joueur:
                continue
            for dr, dc in directions:
                cases = [(r + dr * k, c + dc * k) for k in range(4)]
                if all(0 <= rr < ROWS and 0 <= cc < COLS and plateau[rr][cc] == joueur
                       for rr, cc in cases):
                    return cases
    return []


def dessiner_plateau(ecran, plateau, col_survol=None, piece_temp=None, cases_gagnantes=None):
    if cases_gagnantes is None:
        cases_gagnantes = []
    gagnantes_set = set(cases_gagnantes)

    # Ombre planche
    ombre = pygame.Surface((BOARD_W + 20, BOARD_H + 20), pygame.SRCALPHA)
    pygame.draw.rect(ombre, (0, 0, 0, 30), ombre.get_rect(), border_radius=24)
    ecran.blit(ombre, (BOARD_X - 4, BOARD_Y + 10))

    # Fond planche blanc arrondi
    rect_g = pygame.Rect(BOARD_X, BOARD_Y, BOARD_W, BOARD_H)
    pygame.draw.rect(ecran, BLANC, rect_g, border_radius=20)
    pygame.draw.rect(ecran, GRILLE_BORD, rect_g, 2, border_radius=20)

    # Surbrillance colonne
    if col_survol is not None:
        x = BOARD_X + col_survol * CELL
        sv = pygame.Surface((CELL, BOARD_H), pygame.SRCALPHA)
        sv.fill((46, 196, 160, 22))
        ecran.blit(sv, (x, BOARD_Y))

    # Cases et jetons
    for ligne in range(ROWS):
        for col in range(COLS):
            x, y = centre_case(ligne, col)
            piece = plateau[ligne][col]

            # Creux (inset)
            pygame.draw.circle(ecran, CASE_VIDE_OMB, (x + 2, y + 3), RAYON + 4)
            pygame.draw.circle(ecran, CASE_VIDE,     (x, y), RAYON + 2)

            if piece != VIDE:
                est_gagnante = (ligne, col) in gagnantes_set
                dessiner_jeton(ecran, x, y, piece, etoile=est_gagnante)

    # Numéros de colonnes
    for col in range(COLS):
        x = BOARD_X + col * CELL + CELL // 2
        dessiner_texte(ecran, str(col + 1), POLICE_CHIFFRE, TEXTE_DOUX,
                       (x, BOARD_Y + BOARD_H + 14), centre=True)

    # Jeton en animation
    if piece_temp is not None:
        x, y, piece = piece_temp
        dessiner_jeton(ecran, x, int(y), piece)


# ═══════════════════════════════════════════════════════════════
#  HUD PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def dessiner_hud(ecran, plateau, niveau_nom, tour_joueur, message,
                 col_survol=None, piece_temp=None, cases_gagnantes=None):
    dessiner_fond(ecran)

    # ── Titre ──
    dessiner_texte(ecran, "Puissance 4", POLICE_TITRE, TEXTE_TITRE, (BOARD_X, 20))
    pygame.draw.line(ecran, TEAL, (BOARD_X, 80), (BOARD_X + 300, 80), 3)
    dessiner_texte(ecran, "Joueur  vs  Ordinateur", POLICE_PETIT, TEXTE_DOUX, (BOARD_X, 88))

    # ── Panneau latéral ──
    panneau = pygame.Rect(PANEL_X, 50, 262, 610)
    carte(ecran, panneau, fond=FOND_PANNEAU, bord=GRILLE_BORD, rayon=18)

    entete = pygame.Rect(PANEL_X, 50, 262, 46)
    pygame.draw.rect(ecran, TEAL, entete, border_radius=18)
    pygame.draw.rect(ecran, TEAL, pygame.Rect(PANEL_X, 72, 262, 24))
    dessiner_texte(ecran, "Tableau de bord", POLICE_TEXTE_GRAS, BLANC, (PANEL_X + 18, 62))

    # ── Bloc Tour ──
    t_rect = pygame.Rect(PANEL_X + 14, 112, 234, 120)
    fond_t = (220, 248, 244) if tour_joueur else (240, 240, 250)
    carte(ecran, t_rect, fond=fond_t, bord=GRILLE_BORD, rayon=12)
    dessiner_texte(ecran, "TOUR ACTUEL", POLICE_PETIT, TEXTE_DOUX, (PANEL_X + 28, 130))

    if tour_joueur:
        pygame.draw.circle(ecran, TEAL, (PANEL_X + 36, 172), 10)
        dessiner_texte(ecran, "Joueur", POLICE_STAT, TEAL, (PANEL_X + 54, 170))
    else:
        pygame.draw.circle(ecran, MARINE, (PANEL_X + 36, 172), 10)
        dessiner_texte(ecran, "Ordinateur", POLICE_SOUS_TITRE, TEXTE_CORPS, (PANEL_X + 54, 170))

    dessiner_texte(ecran, "● Teal = Toi  ● Marine = IA",
                   POLICE_PETIT, TEXTE_DOUX, (PANEL_X + 28, 212))

    # ── Bloc Niveau ──
    niveau = NIVEAUX[niveau_nom]
    n_rect = pygame.Rect(PANEL_X + 14, 232, 234, 108)
    carte(ecran, n_rect, fond=niveau["couleur2"], bord=GRILLE_BORD, rayon=12)
    dessiner_texte(ecran, "NIVEAU", POLICE_PETIT, TEXTE_DOUX, (PANEL_X + 28, 244))
    dessiner_texte(ecran, niveau_nom, POLICE_STAT, niveau["couleur"], (PANEL_X + 28, 264))
    mode_txt = ("IA simple" if niveau["mode"] == "simple"
                else f"Alpha-bêta prof. {niveau['profondeur']}")
    dessiner_texte(ecran, mode_txt, POLICE_PETIT, TEXTE_CORPS, (PANEL_X + 28, 308))

    # ── Bloc Stats ──
    s_rect = pygame.Rect(PANEL_X + 14, 358, 234, 92)
    carte(ecran, s_rect, fond=BLANC, bord=GRILLE_BORD, rayon=12)
    dessiner_texte(ecran, "STATISTIQUES", POLICE_PETIT, TEXTE_DOUX, (PANEL_X + 28, 370))
    nb_libres = len(colonnes_valides(plateau))
    coups     = int((plateau != VIDE).sum())
    dessiner_texte(ecran, f"{nb_libres} col. libres",
                   POLICE_TEXTE_GRAS, TEXTE_CORPS, (PANEL_X + 28, 394))
    dessiner_texte(ecran, f"{coups} coups joués",
                   POLICE_TEXTE, TEXTE_DOUX, (PANEL_X + 28, 422))

    # ── Bloc Message ──
    m_rect = pygame.Rect(PANEL_X + 14, 468, 234, 74)
    carte(ecran, m_rect, fond=(230, 248, 244), bord=TEAL, rayon=12)
    pygame.draw.rect(ecran, TEAL,
                     pygame.Rect(PANEL_X + 14, 468, 5, 74), border_radius=4)
    dessiner_texte(ecran, message, POLICE_TEXTE_GRAS, TEXTE_TITRE, (PANEL_X + 28, 482))
    dessiner_texte(ecran, "Clique une colonne", POLICE_PETIT, TEXTE_DOUX, (PANEL_X + 28, 512))

    # Légende couleurs
    lg = PANEL_X + 14
    ly = 562
    pygame.draw.circle(ecran, TEAL, (lg + 8, ly + 8), 8)
    dessiner_texte(ecran, "Joueur", POLICE_PETIT, TEXTE_CORPS, (lg + 22, ly))
    pygame.draw.circle(ecran, MARINE, (lg + 130, ly + 8), 8)
    dessiner_texte(ecran, "Ordinateur", POLICE_PETIT, TEXTE_CORPS, (lg + 144, ly))

    dessiner_texte(ecran, "[Échap] Menu principal",
                   POLICE_PETIT, TEXTE_DOUX, (PANEL_X + 14, 594))

    # ── Prévisualisation ──
    if tour_joueur and col_survol is not None:
        x = BOARD_X + col_survol * CELL + CELL // 2
        dessiner_jeton(ecran, x, 96, JOUEUR, rayon=22)
        pygame.draw.polygon(ecran, TEAL,
                            [(x - 8, 124), (x + 8, 124), (x, 136)])

    dessiner_plateau(ecran, plateau, col_survol, piece_temp, cases_gagnantes)
    pygame.display.flip()


# ═══════════════════════════════════════════════════════════════
#  ANIMATION CHUTE (physique avec rebond)
# ═══════════════════════════════════════════════════════════════

def animer_chute(ecran, plateau, col, ligne, piece, niveau_nom,
                 tour_joueur, message, col_survol):
    clock   = pygame.time.Clock()
    x, cible_y = centre_case(ligne, col)
    y       = float(96)
    vy      = 0.0
    g       = 2.6          # gravité
    rebond  = 0.38         # coefficient de rebond
    seuil   = 2.0          # vitesse minimale pour stopper

    while True:
        vy += g
        y  += vy

        if y >= cible_y:
            y  = cible_y
            vy = -vy * rebond
            if abs(vy) < seuil:
                break

        dessiner_hud(ecran, plateau, niveau_nom, tour_joueur, message,
                     col_survol, (x, y, piece))
        clock.tick(FPS)

    # Frame finale bien posée
    dessiner_hud(ecran, plateau, niveau_nom, tour_joueur, message,
                 col_survol, (x, cible_y, piece))


# ═══════════════════════════════════════════════════════════════
#  ÉCRAN VICTOIRE : style "You Won!"
# ═══════════════════════════════════════════════════════════════

def ecran_victoire(ecran, gagnant, plateau, niveau_nom):
    # Trouver les cases gagnantes pour les étoiles
    cases_gagnantes = []
    if gagnant == JOUEUR:
        cases_gagnantes = trouver_cases_gagnantes(plateau, JOUEUR)
    elif gagnant == IA:
        cases_gagnantes = trouver_cases_gagnantes(plateau, IA)

    clock = pygame.time.Clock()
    t0    = time.time()

    if gagnant == JOUEUR:
        titre_txt  = "You Won!"
        sous_txt   = "Bravo, tu as battu l'ordinateur !"
        coul_titre = ROSE_TITRE
        coul_ombre = ROSE_OMBRE
        accent     = TEAL
    elif gagnant == IA:
        titre_txt  = "IA gagne..."
        sous_txt   = "L'IA l'emporte. Retente, tu peux le battre !"
        coul_titre = MARINE
        coul_ombre = MARINE_FONCE
        accent     = ROUGE_BOUTON
    else:
        titre_txt  = "Match nul"
        sous_txt   = "Plateau complet. Personne ne l'emporte."
        coul_titre = TEXTE_TITRE
        coul_ombre = TEXTE_CORPS
        accent     = TEXTE_DOUX

    btn_rejouer = pygame.Rect(260, 510, 170, 54)
    btn_quitter = pygame.Rect(460, 510, 170, 54)

    while True:
        elapsed = time.time() - t0
        souris  = pygame.mouse.get_pos()

        # Redessiner le plateau avec étoiles
        dessiner_fond(ecran)
        dessiner_plateau(ecran, plateau, cases_gagnantes=cases_gagnantes)

        # Overlay semi-transparent
        overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        overlay.fill((232, 234, 240, 185))
        ecran.blit(overlay, (0, 0))

        # Carte centrale
        carte_r = pygame.Rect(210, 165, 540, 390)
        ombre_rect(ecran, carte_r, rayon=22, decal=10, alpha=55)
        pygame.draw.rect(ecran, BLANC, carte_r, border_radius=22)
        pygame.draw.rect(ecran, GRILLE_BORD, carte_r, 2, border_radius=22)

        # Barre accent en haut
        pygame.draw.rect(ecran, accent,
                         pygame.Rect(carte_r.x, carte_r.y, carte_r.w, 10),
                         border_radius=22)

        # Titre animé (léger effet pulse)
        scale_t = 1.0 + 0.03 * math.sin(elapsed * 4)

        # Ombre portée du titre
        _draw_bubbly_text(ecran, titre_txt, POLICE_YOUWIN, coul_titre, coul_ombre,
                          (carte_r.centerx, carte_r.y + 90))

        # Sous-titre
        dessiner_texte(ecran, sous_txt, POLICE_TEXTE, TEXTE_CORPS,
                       (carte_r.centerx, carte_r.y + 155), centre=True)

        # Ligne déco
        pygame.draw.line(ecran, GRILLE_BORD,
                         (carte_r.x + 70, carte_r.y + 182),
                         (carte_r.x + carte_r.w - 70, carte_r.y + 182), 1)

        dessiner_texte(ecran, f"Niveau joué : {niveau_nom}",
                       POLICE_TEXTE_GRAS, TEXTE_DOUX,
                       (carte_r.centerx, carte_r.y + 208), centre=True)

        # Petites prévisualisations des jetons gagnants avec étoiles
        if cases_gagnantes:
            px_start = carte_r.centerx - 100
            for i in range(4):
                px = px_start + i * 66
                py = carte_r.y + 295
                dessiner_jeton(ecran, px, py, gagnant, rayon=26, etoile=True)

        # Boutons
        bouton(ecran, btn_rejouer, "Rejouer", VERT_BOUTON,
               hover=btn_rejouer.collidepoint(souris))
        bouton(ecran, btn_quitter, "Quitter", ROUGE_BOUTON,
               hover=btn_quitter.collidepoint(souris))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rejouer.collidepoint(event.pos):
                    return "rejouer"
                if btn_quitter.collidepoint(event.pos):
                    return "quitter"


def _draw_bubbly_text(ecran, texte, police, couleur, ombre_c, centre_pos):
    """Texte bubbly style avec ombre décalée (comme l'image)."""
    cx, cy = centre_pos
    surf = police.render(texte, True, couleur)
    # Ombre
    s_omb = police.render(texte, True, ombre_c)
    ecran.blit(s_omb, s_omb.get_rect(center=(cx + 4, cy + 5)))
    ecran.blit(surf, surf.get_rect(center=(cx, cy)))


# ═══════════════════════════════════════════════════════════════
#  ÉCRAN CHOIX NIVEAU
# ═══════════════════════════════════════════════════════════════

def ecran_choix_niveau(ecran):
    clock   = pygame.time.Clock()
    boutons = {}

    while True:
        souris = pygame.mouse.get_pos()
        dessiner_fond(ecran)

        # Titre bubbly
        _draw_bubbly_text(ecran, "Puissance 4", POLICE_TITRE, TEAL, TEAL_FONCE,
                          (LARGEUR // 2, 62))
        pygame.draw.line(ecran, TEAL,
                         (LARGEUR // 2 - 130, 98), (LARGEUR // 2 + 130, 98), 3)
        dessiner_texte(ecran, "Choisis ton niveau de difficulté",
                       POLICE_TEXTE, TEXTE_DOUX, (LARGEUR // 2, 112), centre=True)

        # Aperçu plateau
        prev = pygame.Rect(55, 168, 310, 280)
        carte(ecran, prev, fond=BLANC, bord=GRILLE_BORD, rayon=18)

        rayon_p = 22
        for r in range(4):
            for c in range(5):
                px = prev.x + 44 + c * 56
                py = prev.y + 44 + r * 56
                pygame.draw.circle(ecran, CASE_VIDE_OMB, (px + 2, py + 3), rayon_p + 3)
                pygame.draw.circle(ecran, CASE_VIDE, (px, py), rayon_p + 2)

        exemples = [
            (prev.x + 44,  prev.y + 220, JOUEUR),
            (prev.x + 100, prev.y + 220, IA),
            (prev.x + 156, prev.y + 220, JOUEUR),
            (prev.x + 156, prev.y + 164, IA),
            (prev.x + 212, prev.y + 220, JOUEUR),
        ]
        for px, py, piece in exemples:
            dessiner_jeton(ecran, px, py, piece, rayon=rayon_p)

        dessiner_texte(ecran, "● Joueur (Teal)", POLICE_PETIT, TEAL,
                       (prev.x + 16, prev.y + 260))
        dessiner_texte(ecran, "● Ordinateur (Marine)", POLICE_PETIT, MARINE,
                       (prev.x + 16, prev.y + 282))

        # Règle rapide
        regle_r = pygame.Rect(55, 472, 310, 118)
        carte(ecran, regle_r, fond=(220, 248, 244), bord=TEAL, rayon=14)
        dessiner_texte(ecran, "Comment jouer ?", POLICE_TEXTE_GRAS, TEAL,
                       (regle_r.x + 16, regle_r.y + 14))
        for i, ligne in enumerate([
            "Clique sur une colonne (1–7)",
            "Aligne 4 jetons en ligne,",
            "en colonne ou en diagonale.",
        ]):
            dessiner_texte(ecran, ligne, POLICE_PETIT, TEXTE_CORPS,
                           (regle_r.x + 16, regle_r.y + 40 + i * 24))

        # Boutons de niveau
        dessiner_texte(ecran, "Choisir le niveau :",
                       POLICE_SOUS_TITRE, TEXTE_TITRE, (408, 170))
        pygame.draw.line(ecran, GRILLE_BORD, (408, 198), (885, 198), 1)

        for i, (nom, data) in enumerate(NIVEAUX.items()):
            rect = pygame.Rect(408, 214 + i * 122, 477, 104)
            boutons[nom] = rect
            hover = rect.collidepoint(souris)
            fond_btn = eclaircir(data["couleur2"], 8) if hover else data["couleur2"]
            carte(ecran, rect, fond=fond_btn, bord=data["couleur"], rayon=14)

            pygame.draw.circle(ecran, data["couleur"], (rect.x + 34, rect.centery), 13)

            dessiner_texte(ecran, nom, POLICE_SOUS_TITRE, data["couleur"],
                           (rect.x + 58, rect.y + 16))
            dessiner_texte(ecran, data["description"], POLICE_TEXTE, TEXTE_CORPS,
                           (rect.x + 58, rect.y + 44))
            mode_txt = ("IA simple" if data["mode"] == "simple"
                        else f"Minimax α-β, profondeur {data['profondeur']}")
            dessiner_texte(ecran, mode_txt, POLICE_PETIT, TEXTE_DOUX,
                           (rect.x + 58, rect.y + 74))

            if hover:
                pts = [(rect.right - 32, rect.centery),
                       (rect.right - 18, rect.centery - 8),
                       (rect.right - 18, rect.centery + 8)]
                pygame.draw.polygon(ecran, data["couleur"], pts)

        dessiner_texte(ecran, "Échap pour quitter",
                       POLICE_PETIT, TEXTE_DOUX, (LARGEUR // 2, 668), centre=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for nom, rect in boutons.items():
                    if rect.collidepoint(event.pos):
                        return nom
        clock.tick(FPS)


# ═══════════════════════════════════════════════════════════════
#  BOUCLE DE JEU
# ═══════════════════════════════════════════════════════════════

def choisir_coup_ia(plateau, niveau_nom):
    niveau = NIVEAUX[niveau_nom]
    if niveau["mode"] == "simple":
        return coup_ia_simple_ordinateur(plateau)
    return coup_ia_alphabeta(plateau, niveau["profondeur"])


def jouer(niveau_nom):
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Puissance 4")
    clock = pygame.time.Clock()

    plateau      = creer_plateau()
    jeu_en_cours = True
    tour_joueur  = True
    col_survol   = COLS // 2
    gagnant      = None
    message      = "À toi de jouer !"

    dessiner_hud(ecran, plateau, niveau_nom, tour_joueur, message, col_survol)

    while jeu_en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "quitter"

            if event.type == pygame.MOUSEMOTION and tour_joueur:
                col = colonne_depuis_position(event.pos)
                if col is not None:
                    col_survol = col
                    message = ("À toi de jouer !"
                               if colonne_valide(plateau, col)
                               else "Colonne pleine !")
                    dessiner_hud(ecran, plateau, niveau_nom, tour_joueur,
                                 message, col_survol)

            if event.type == pygame.MOUSEBUTTONDOWN and tour_joueur:
                col = colonne_depuis_position(event.pos)
                if col is None:
                    continue
                if not colonne_valide(plateau, col):
                    message = "Colonne pleine !"
                    dessiner_hud(ecran, plateau, niveau_nom, tour_joueur,
                                 message, col_survol)
                    continue

                ligne = obtenir_ligne_libre(plateau, col)
                animer_chute(ecran, plateau, col, ligne, JOUEUR,
                             niveau_nom, tour_joueur, "Jeton en chute…", col_survol)
                placer_jeton(plateau, ligne, col, JOUEUR)

                if verifier_victoire(plateau, JOUEUR):
                    gagnant = JOUEUR; jeu_en_cours = False
                elif plateau_plein(plateau):
                    gagnant = None;  jeu_en_cours = False
                else:
                    tour_joueur = False
                    message = "L'IA réfléchit…"
                dessiner_hud(ecran, plateau, niveau_nom, tour_joueur,
                             message, col_survol)

        if not tour_joueur and jeu_en_cours:
            pygame.time.wait(240)
            debut  = time.time()
            col_ia = choisir_coup_ia(plateau, niveau_nom)
            print(f"IA {niveau_nom} → col {col_ia} en {time.time()-debut:.3f}s")

            if col_ia is not None and colonne_valide(plateau, col_ia):
                ligne = obtenir_ligne_libre(plateau, col_ia)
                animer_chute(ecran, plateau, col_ia, ligne, IA,
                             niveau_nom, tour_joueur, "L'IA joue…", col_survol)
                placer_jeton(plateau, ligne, col_ia, IA)

            if verifier_victoire(plateau, IA):
                gagnant = IA;   jeu_en_cours = False
            elif plateau_plein(plateau):
                gagnant = None; jeu_en_cours = False
            else:
                tour_joueur = True
                message = "À toi de jouer !"
            dessiner_hud(ecran, plateau, niveau_nom, tour_joueur,
                         message, col_survol)

        clock.tick(FPS)

    pygame.time.wait(400)
    dessiner_hud(ecran, plateau, niveau_nom, tour_joueur, "Partie terminée !", col_survol)
    return ecran_victoire(ecran, gagnant, plateau, niveau_nom)


def colonne_depuis_position(pos):
    x, y = pos
    if not (BOARD_X <= x < BOARD_X + BOARD_W):
        return None
    if not (55 <= y <= BOARD_Y + BOARD_H + 40):
        return None
    return min(COLS - 1, max(0, (x - BOARD_X) // CELL))


# ═══════════════════════════════════════════════════════════════
#  POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════

def main():
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Puissance 4")

    while True:
        niveau   = ecran_choix_niveau(ecran)
        print(f"Niveau : {niveau}")
        resultat = jouer(niveau)
        if resultat == "quitter":
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()