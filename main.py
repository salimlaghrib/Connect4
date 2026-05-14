# ──────────────────────────────────────────────
#  TESTS RAPIDES  (lance ce fichier directement
#  pour vérifier que tout fonctionne)
# ──────────────────────────────────────────────
from board import IA, JOUEUR, afficher_plateau, creer_plateau, obtenir_ligne_libre, placer_jeton, score_plateau, verifier_victoire


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