import sys
import time

import pygame

from board import (
    ROWS, COLS, VIDE, JOUEUR, IA,
    creer_plateau, placer_jeton, obtenir_ligne_libre,
    colonne_valide, colonnes_valides,
    verifier_victoire, plateau_plein
)
from ai import coup_ia_alphabeta, coup_ia_simple_ordinateur


pygame.init()

# Fenetre
CELL = 82
GAP = 10
RAYON = CELL // 2 - 11
BOARD_X = 64
BOARD_Y = 132
BOARD_W = COLS * CELL
BOARD_H = ROWS * CELL
PANEL_X = BOARD_X + BOARD_W + 34
LARGEUR = 960
HAUTEUR = 720
FPS = 60

# Palette
FOND_HAUT = (18, 24, 42)
FOND_BAS = (30, 34, 58)
SURFACE = (246, 248, 252)
SURFACE_2 = (232, 236, 245)
TEXTE = (24, 31, 48)
TEXTE_DOUX = (93, 102, 121)
BLANC = (255, 255, 255)
BLEU_GRILLE = (31, 98, 203)
BLEU_GRILLE_2 = (24, 78, 170)
BLEU_ACCENT = (70, 139, 255)
TROU = (14, 22, 39)
JAUNE = (255, 205, 56)
JAUNE_CLAIR = (255, 232, 122)
ROUGE = (236, 67, 71)
ROUGE_CLAIR = (255, 135, 124)
VERT = (52, 190, 121)
OMBRE = (8, 13, 28)

POLICE_TITRE = pygame.font.SysFont("arial", 48, bold=True)
POLICE_SOUS_TITRE = pygame.font.SysFont("arial", 25, bold=True)
POLICE_TEXTE = pygame.font.SysFont("arial", 22)
POLICE_TEXTE_GRAS = pygame.font.SysFont("arial", 22, bold=True)
POLICE_PETIT = pygame.font.SysFont("arial", 17)
POLICE_BOUTON = pygame.font.SysFont("arial", 24, bold=True)
POLICE_STAT = pygame.font.SysFont("arial", 34, bold=True)

NIVEAUX = {
    "Simple": {
        "profondeur": 1,
        "mode": "simple",
        "couleur": (48, 170, 111),
        "description": "Rapide, lisible, parfait pour debuter."
    },
    "Moyen": {
        "profondeur": 4,
        "mode": "alphabeta",
        "couleur": (235, 153, 42),
        "description": "Minimax equilibre avec alpha-beta."
    },
    "Expert": {
        "profondeur": 6,
        "mode": "alphabeta",
        "couleur": (220, 68, 84),
        "description": "Plus profond, plus patient, plus dur."
    },
}


def dessiner_degrade(ecran):
    for y in range(HAUTEUR):
        ratio = y / HAUTEUR
        couleur = tuple(
            int(FOND_HAUT[i] * (1 - ratio) + FOND_BAS[i] * ratio)
            for i in range(3)
        )
        pygame.draw.line(ecran, couleur, (0, y), (LARGEUR, y))


def dessiner_texte(ecran, texte, police, couleur, pos, centre=False):
    surface = police.render(texte, True, couleur)
    rect = surface.get_rect()
    if centre:
        rect.center = pos
    else:
        rect.topleft = pos
    ecran.blit(surface, rect)
    return rect


def dessiner_bouton(ecran, rect, texte, couleur, texte_couleur=BLANC, hover=False):
    fond = eclaircir(couleur, 18) if hover else couleur
    pygame.draw.rect(ecran, fond, rect, border_radius=8)
    pygame.draw.rect(ecran, (255, 255, 255, 80), rect, 2, border_radius=8)
    dessiner_texte(ecran, texte, POLICE_BOUTON, texte_couleur, rect.center, centre=True)


def eclaircir(couleur, amount):
    return tuple(min(255, c + amount) for c in couleur)


def assombrir(couleur, amount):
    return tuple(max(0, c - amount) for c in couleur)


def centre_case(ligne, col):
    return (
        BOARD_X + col * CELL + CELL // 2,
        BOARD_Y + ligne * CELL + CELL // 2
    )


def couleur_piece(piece):
    if piece == JOUEUR:
        return JAUNE, JAUNE_CLAIR
    if piece == IA:
        return ROUGE, ROUGE_CLAIR
    return TROU, TROU


def dessiner_jeton(ecran, x, y, piece, rayon=RAYON):
    couleur, lumiere = couleur_piece(piece)
    pygame.draw.circle(ecran, (0, 0, 0, 90), (x + 4, y + 6), rayon)
    pygame.draw.circle(ecran, assombrir(couleur, 24), (x, y), rayon)
    pygame.draw.circle(ecran, couleur, (x, y - 2), rayon - 2)
    pygame.draw.circle(ecran, lumiere, (x - rayon // 3, y - rayon // 3), max(5, rayon // 5))


def dessiner_plateau(ecran, plateau, col_survol=None, piece_temp=None):
    ombre_rect = pygame.Rect(BOARD_X + 9, BOARD_Y + 12, BOARD_W, BOARD_H)
    pygame.draw.rect(ecran, (0, 0, 0, 70), ombre_rect, border_radius=24)

    grille = pygame.Rect(BOARD_X, BOARD_Y, BOARD_W, BOARD_H)
    pygame.draw.rect(ecran, BLEU_GRILLE_2, grille, border_radius=24)
    pygame.draw.rect(ecran, BLEU_GRILLE, grille.inflate(-8, -8), border_radius=20)

    if col_survol is not None:
        x = BOARD_X + col_survol * CELL + GAP // 2
        pygame.draw.rect(
            ecran,
            (255, 255, 255, 34),
            (x, BOARD_Y + GAP // 2, CELL - GAP, BOARD_H - GAP),
            border_radius=18
        )

    for ligne in range(ROWS):
        for col in range(COLS):
            x, y = centre_case(ligne, col)
            piece = plateau[ligne][col]
            pygame.draw.circle(ecran, OMBRE, (x + 3, y + 4), RAYON + 3)
            pygame.draw.circle(ecran, TROU, (x, y), RAYON + 2)
            if piece != VIDE:
                dessiner_jeton(ecran, x, y, piece)

    for col in range(COLS):
        x = BOARD_X + col * CELL + CELL // 2
        dessiner_texte(ecran, str(col + 1), POLICE_PETIT, (185, 198, 229), (x, BOARD_Y + BOARD_H + 22), centre=True)

    if piece_temp is not None:
        x, y, piece = piece_temp
        dessiner_jeton(ecran, x, y, piece)


def dessiner_hud(ecran, plateau, niveau_nom, tour_joueur, message, col_survol=None, piece_temp=None):
    dessiner_degrade(ecran)

    dessiner_texte(ecran, "Puissance 4", POLICE_TITRE, BLANC, (BOARD_X, 38))
    dessiner_texte(ecran, "Joueur contre ordinateur", POLICE_TEXTE, (190, 201, 224), (BOARD_X + 4, 92))

    panneau = pygame.Rect(PANEL_X, 72, 250, 555)
    pygame.draw.rect(ecran, SURFACE, panneau, border_radius=18)
    pygame.draw.rect(ecran, (255, 255, 255), panneau, 2, border_radius=18)

    dessiner_texte(ecran, "Partie", POLICE_SOUS_TITRE, TEXTE, (PANEL_X + 24, 100))

    tour_rect = pygame.Rect(PANEL_X + 24, 145, 202, 92)
    tour_couleur = (255, 247, 214) if tour_joueur else (255, 232, 232)
    pygame.draw.rect(ecran, tour_couleur, tour_rect, border_radius=12)
    pygame.draw.rect(ecran, (218, 224, 238), tour_rect, 1, border_radius=12)
    dessiner_texte(ecran, "Tour actuel", POLICE_PETIT, TEXTE_DOUX, (tour_rect.x + 18, tour_rect.y + 15))
    joueur_txt = "Joueur" if tour_joueur else "Ordinateur"
    joueur_col = JAUNE if tour_joueur else ROUGE
    dessiner_texte(ecran, joueur_txt, POLICE_STAT, joueur_col, (tour_rect.x + 18, tour_rect.y + 42))

    niveau = NIVEAUX[niveau_nom]
    diff_rect = pygame.Rect(PANEL_X + 24, 260, 202, 116)
    pygame.draw.rect(ecran, SURFACE_2, diff_rect, border_radius=12)
    dessiner_texte(ecran, "Niveau IA", POLICE_PETIT, TEXTE_DOUX, (diff_rect.x + 18, diff_rect.y + 16))
    dessiner_texte(ecran, niveau_nom, POLICE_SOUS_TITRE, niveau["couleur"], (diff_rect.x + 18, diff_rect.y + 42))
    detail = "IA simple" if niveau["mode"] == "simple" else f"Profondeur {niveau['profondeur']}"
    dessiner_texte(ecran, detail, POLICE_TEXTE, TEXTE, (diff_rect.x + 18, diff_rect.y + 76))

    nb_colonnes_libres = len(colonnes_valides(plateau))
    coups = int((plateau != VIDE).sum())
    stat_rect = pygame.Rect(PANEL_X + 24, 402, 202, 78)
    pygame.draw.rect(ecran, (238, 242, 250), stat_rect, border_radius=12)
    dessiner_texte(ecran, "Colonnes libres", POLICE_PETIT, TEXTE_DOUX, (stat_rect.x + 18, stat_rect.y + 12))
    dessiner_texte(ecran, str(nb_colonnes_libres), POLICE_STAT, TEXTE, (stat_rect.x + 18, stat_rect.y + 34))
    dessiner_texte(ecran, f"{coups} coups", POLICE_PETIT, TEXTE_DOUX, (stat_rect.x + 112, stat_rect.y + 42))

    aide_rect = pygame.Rect(PANEL_X + 24, 505, 202, 76)
    pygame.draw.rect(ecran, (26, 35, 57), aide_rect, border_radius=12)
    dessiner_texte(ecran, message, POLICE_PETIT, BLANC, (aide_rect.x + 16, aide_rect.y + 17))
    dessiner_texte(ecran, "Clique une colonne", POLICE_PETIT, (185, 198, 229), (aide_rect.x + 16, aide_rect.y + 42))

    if tour_joueur and col_survol is not None:
        x = BOARD_X + col_survol * CELL + CELL // 2
        dessiner_jeton(ecran, x, 88, JOUEUR, rayon=28)
        pygame.draw.polygon(ecran, JAUNE, [(x - 8, 116), (x + 8, 116), (x, 126)])

    dessiner_plateau(ecran, plateau, col_survol, piece_temp)
    pygame.display.flip()


def colonne_depuis_position(pos):
    x, y = pos
    if not (BOARD_X <= x < BOARD_X + BOARD_W):
        return None
    if not (60 <= y <= BOARD_Y + BOARD_H + 42):
        return None
    return min(COLS - 1, max(0, (x - BOARD_X) // CELL))


def animer_chute(ecran, plateau, col, ligne, piece, niveau_nom, tour_joueur, message, col_survol):
    clock = pygame.time.Clock()
    x, cible_y = centre_case(ligne, col)
    y = 82
    vitesse = 0

    while y < cible_y:
        vitesse += 2.2
        y = min(cible_y, y + vitesse)
        dessiner_hud(ecran, plateau, niveau_nom, tour_joueur, message, col_survol, (x, int(y), piece))
        clock.tick(FPS)


def ecran_victoire(ecran, gagnant, plateau, niveau_nom):
    overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    overlay.fill((8, 12, 24, 185))
    ecran.blit(overlay, (0, 0))

    carte = pygame.Rect(250, 178, 460, 330)
    pygame.draw.rect(ecran, SURFACE, carte, border_radius=18)
    pygame.draw.rect(ecran, BLANC, carte, 2, border_radius=18)

    if gagnant == JOUEUR:
        titre = "Victoire !"
        sous = "Bien joue, tu as battu l'ordinateur."
        couleur = JAUNE
    elif gagnant == IA:
        titre = "L'ordinateur gagne"
        sous = "Retente une partie, le centre aide beaucoup."
        couleur = ROUGE
    else:
        titre = "Match nul"
        sous = "Plateau rempli, personne ne prend l'avantage."
        couleur = BLEU_ACCENT

    dessiner_texte(ecran, titre, POLICE_TITRE, couleur, (carte.centerx, carte.y + 76), centre=True)
    dessiner_texte(ecran, sous, POLICE_TEXTE, TEXTE_DOUX, (carte.centerx, carte.y + 132), centre=True)
    dessiner_texte(ecran, f"Niveau : {niveau_nom}", POLICE_TEXTE_GRAS, TEXTE, (carte.centerx, carte.y + 176), centre=True)

    btn_rejouer = pygame.Rect(carte.x + 70, carte.y + 235, 145, 56)
    btn_quitter = pygame.Rect(carte.x + 245, carte.y + 235, 145, 56)

    pygame.display.flip()

    while True:
        souris = pygame.mouse.get_pos()
        dessiner_bouton(ecran, btn_rejouer, "Rejouer", VERT, hover=btn_rejouer.collidepoint(souris))
        dessiner_bouton(ecran, btn_quitter, "Quitter", ROUGE, hover=btn_quitter.collidepoint(souris))
        pygame.display.update([btn_rejouer, btn_quitter])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rejouer.collidepoint(event.pos):
                    return "rejouer"
                if btn_quitter.collidepoint(event.pos):
                    return "quitter"


def ecran_choix_niveau(ecran):
    clock = pygame.time.Clock()
    boutons = {}

    while True:
        souris = pygame.mouse.get_pos()
        dessiner_degrade(ecran)
        dessiner_texte(ecran, "Puissance 4", POLICE_TITRE, BLANC, (LARGEUR // 2, 82), centre=True)
        dessiner_texte(ecran, "Affronte une IA simple ou minimax, avec un plateau plus fluide.", POLICE_TEXTE, (194, 205, 226), (LARGEUR // 2, 136), centre=True)

        preview = pygame.Rect(86, 214, 320, 290)
        pygame.draw.rect(ecran, BLEU_GRILLE_2, preview, border_radius=22)
        pygame.draw.rect(ecran, BLEU_GRILLE, preview.inflate(-8, -8), border_radius=18)
        for r in range(4):
            for c in range(5):
                x = preview.x + 45 + c * 58
                y = preview.y + 45 + r * 58
                pygame.draw.circle(ecran, TROU, (x, y), 22)
        for x, y, piece in [
            (preview.x + 45, preview.y + 219, JOUEUR),
            (preview.x + 103, preview.y + 219, IA),
            (preview.x + 161, preview.y + 219, JOUEUR),
            (preview.x + 161, preview.y + 161, IA),
            (preview.x + 219, preview.y + 219, JOUEUR),
        ]:
            dessiner_jeton(ecran, x, y, piece, rayon=22)

        dessiner_texte(ecran, "Choisis ton adversaire", POLICE_SOUS_TITRE, BLANC, (470, 214))
        dessiner_texte(ecran, "Le gameplay reste le meme : clique une colonne, aligne 4 jetons.", POLICE_TEXTE, (194, 205, 226), (470, 252))

        for i, (nom, data) in enumerate(NIVEAUX.items()):
            rect = pygame.Rect(470, 310 + i * 88, 360, 68)
            boutons[nom] = rect
            hover = rect.collidepoint(souris)
            couleur = eclaircir(data["couleur"], 16) if hover else data["couleur"]
            pygame.draw.rect(ecran, couleur, rect, border_radius=10)
            pygame.draw.rect(ecran, (255, 255, 255, 95), rect, 2, border_radius=10)
            dessiner_texte(ecran, nom, POLICE_BOUTON, BLANC, (rect.x + 20, rect.y + 10))
            dessiner_texte(ecran, data["description"], POLICE_PETIT, BLANC, (rect.x + 20, rect.y + 39))

        dessiner_texte(ecran, "Echap pour quitter", POLICE_PETIT, (157, 170, 197), (LARGEUR // 2, 650), centre=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for nom, rect in boutons.items():
                    if rect.collidepoint(event.pos):
                        return nom
        clock.tick(FPS)


def choisir_coup_ia(plateau, niveau_nom):
    niveau = NIVEAUX[niveau_nom]
    if niveau["mode"] == "simple":
        return coup_ia_simple_ordinateur(plateau)
    return coup_ia_alphabeta(plateau, niveau["profondeur"])


def jouer(niveau_nom):
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Puissance 4 - Joueur contre ordinateur")
    clock = pygame.time.Clock()

    plateau = creer_plateau()
    jeu_en_cours = True
    tour_joueur = True
    col_survol = COLS // 2
    gagnant = None
    message = "A toi de jouer"

    dessiner_hud(ecran, plateau, niveau_nom, tour_joueur, message, col_survol)

    while jeu_en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "quitter"
            if event.type == pygame.MOUSEMOTION and tour_joueur:
                col = colonne_depuis_position(event.pos)
                if col is not None:
                    col_survol = col
                    message = "A toi de jouer" if colonne_valide(plateau, col) else "Colonne pleine"
                    dessiner_hud(ecran, plateau, niveau_nom, tour_joueur, message, col_survol)
            if event.type == pygame.MOUSEBUTTONDOWN and tour_joueur:
                col = colonne_depuis_position(event.pos)
                if col is None:
                    continue
                if not colonne_valide(plateau, col):
                    message = "Colonne pleine"
                    dessiner_hud(ecran, plateau, niveau_nom, tour_joueur, message, col_survol)
                    continue

                ligne = obtenir_ligne_libre(plateau, col)
                animer_chute(ecran, plateau, col, ligne, JOUEUR, niveau_nom, tour_joueur, "Jeton en chute", col_survol)
                placer_jeton(plateau, ligne, col, JOUEUR)

                if verifier_victoire(plateau, JOUEUR):
                    gagnant = JOUEUR
                    jeu_en_cours = False
                elif plateau_plein(plateau):
                    gagnant = None
                    jeu_en_cours = False
                else:
                    tour_joueur = False
                    message = "L'IA reflechit"
                dessiner_hud(ecran, plateau, niveau_nom, tour_joueur, message, col_survol)

        if not tour_joueur and jeu_en_cours:
            pygame.time.wait(250)
            debut = time.time()
            col_ia = choisir_coup_ia(plateau, niveau_nom)
            duree = time.time() - debut
            niveau = NIVEAUX[niveau_nom]
            print(f"IA {niveau_nom} a joue col {col_ia} en {duree:.3f}s ({niveau['mode']})")

            if col_ia is not None and colonne_valide(plateau, col_ia):
                ligne = obtenir_ligne_libre(plateau, col_ia)
                animer_chute(ecran, plateau, col_ia, ligne, IA, niveau_nom, tour_joueur, "L'IA joue", col_survol)
                placer_jeton(plateau, ligne, col_ia, IA)

            if verifier_victoire(plateau, IA):
                gagnant = IA
                jeu_en_cours = False
            elif plateau_plein(plateau):
                gagnant = None
                jeu_en_cours = False
            else:
                tour_joueur = True
                message = "A toi de jouer"
            dessiner_hud(ecran, plateau, niveau_nom, tour_joueur, message, col_survol)

        clock.tick(FPS)

    pygame.time.wait(350)
    dessiner_hud(ecran, plateau, niveau_nom, tour_joueur, "Partie terminee", col_survol)
    return ecran_victoire(ecran, gagnant, plateau, niveau_nom)


def main():
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Puissance 4 - Joueur contre ordinateur")

    while True:
        niveau = ecran_choix_niveau(ecran)
        print(f"Niveau choisi : {niveau}")
        resultat = jouer(niveau)
        if resultat == "quitter":
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
