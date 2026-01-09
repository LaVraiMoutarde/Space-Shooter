import pygame
import sys
import random
import os
from player import Joueur
from enemy import Ennemi
from boss import Boss

# Faut bien avoir pygame pour que ça marche
pygame.init()

# Un peu d'ambiance avec la musique
chemin_musique = os.path.join('asssets', 'BG Music.mp3')
pygame.mixer.music.load(chemin_musique)
pygame.mixer.music.play(-1)

# La taille de la fenêtre
LARGEUR_ECRAN = 1280
HAUTEUR_ECRAN = 830
ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN))
pygame.display.set_caption("Space Shooter")

# Pour gérer la vitesse du jeu et les FPS
horloge = pygame.time.Clock()
FPS = 60

# Les couleurs que j'utilise
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
ROUGE = (255, 50, 50)
JAUNE = (255, 255, 0)
CYAN = (0, 255, 255)
VERT = (50, 255, 50)
ORANGE = (255, 150, 50)

# On charge la police d'écriture dans mon dossier
chemin_police = os.path.join('police_artonex-fintech-font', 'Artonex-Trial-BF6937bdad87a0a.ttf')
police_titre_gros = pygame.font.Font(chemin_police, 80)
police_titre = pygame.font.Font(chemin_police, 50)
police_titre_petit = pygame.font.Font(chemin_police, 35)
police_ui = pygame.font.SysFont('Arial', 28, bold=True)
police_info = pygame.font.SysFont('Arial', 22)

# Le fond qui bouge
chemin_fond = os.path.join('asssets', 'Backgound', '2D space BG.png')
fond_original = pygame.image.load(chemin_fond)
fond = pygame.transform.scale(fond_original, (LARGEUR_ECRAN, HAUTEUR_ECRAN))
# Pour faire l'effet de défilement infini
fond_y1 = 0
fond_y2 = -HAUTEUR_ECRAN
vitesse_fond = 2

# On save le score ici pour le réutiliser si on perd
dernier_score = 0

#Classe pour gérer les explosions (utilisation de IA pour créer l'effet d'explosion)
class Explosion:
    def __init__(self, x, y, taille=1.0):
        self.x = x
        self.y = y
        self.rayon = 5
        self.rayon_max = int(40 * taille)
        self.vitesse_expansion = int(3 * taille)
        self.alpha = 255
        
    def mettre_a_jour(self):
        self.rayon += self.vitesse_expansion
        self.alpha = max(0, int(255 * (1 - self.rayon / self.rayon_max)))
        return self.rayon < self.rayon_max
    
    def dessiner(self, ecran):
        surface = pygame.Surface((self.rayon * 2, self.rayon * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, (255, 100, 0, self.alpha), (self.rayon, self.rayon), self.rayon)
        ecran.blit(surface, (self.x - self.rayon, self.y - self.rayon))

explosions = []

def creer_explosion(x, y, taille=1.0):
    #explosion à afficher
    explosions.append(Explosion(x, y, taille))

# Le menu principal avant de commencer
def afficher_menu():
    global dernier_score
    en_attente = True
    animation_timer = 0
    
    while en_attente:
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_SPACE:
                    en_attente = False 
                if evenement.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        # Faire bouger le fond pour que ce soit joli
        global fond_y1, fond_y2
        fond_y1 += vitesse_fond
        fond_y2 += vitesse_fond
        if fond_y1 >= HAUTEUR_ECRAN:
            fond_y1 = -HAUTEUR_ECRAN
        if fond_y2 >= HAUTEUR_ECRAN:
            fond_y2 = -HAUTEUR_ECRAN
        
        animation_timer += 1
        
        # On affiche tout
        ecran.blit(fond, (0, fond_y1))
        ecran.blit(fond, (0, fond_y2))
        
        # Le gros titre du jeu
        titre = police_titre_gros.render("Space Shooter", True, CYAN)
        rect_titre = titre.get_rect(center=(LARGEUR_ECRAN // 2, 280))
        ecran.blit(titre, rect_titre)
        
        # Si on a déjà joué, on montre le score d'avant
        if dernier_score > 0:
            texte_dernier = police_ui.render(f"Dernier score: {dernier_score}", True, JAUNE)
            rect_dernier = texte_dernier.get_rect(center=(LARGEUR_ECRAN // 2, 380))
            ecran.blit(texte_dernier, rect_dernier)
        
        # Petit message pour dire quoi faire
        sous_titre = police_ui.render("Appuyez sur ESPACE pour jouer", True, BLANC)
        rect_sous = sous_titre.get_rect(center=(LARGEUR_ECRAN // 2, 450))
        ecran.blit(sous_titre, rect_sous)
        
        # Les règles du jeu
        instructions = ["survivez le plus longtemps possible !", "Tuez tous les ennemis !"]
        for i, instruction in enumerate(instructions):
            texte = police_info.render(instruction, True, (180, 180, 180))
            rect = texte.get_rect(center=(LARGEUR_ECRAN // 2, 520 + i * 30))
            ecran.blit(texte, rect)
        
        pygame.display.flip()
        horloge.tick(FPS)

# La boucle du jeu
def lancer_partie():
    global dernier_score, fond_y1, fond_y2, explosions
    
    # On remet tout à zéro pour une nouvelle partie
    joueur = Joueur(LARGEUR_ECRAN // 2 - 40, HAUTEUR_ECRAN - 100)
    ennemis = []
    boss = None
    score = 0
    ennemis_tues = 0
    explosions = []
    probabilite_apparition = 60
    compteur_apparition = 0
    
    niveau = 1
    vague = 1
    OBJECTIF_BOSS = 15
    
    # Plus on avance, plus la difficulté augmente
    def calculer_difficulte():
        return niveau + (vague - 1) * 0.3
    
    difficulte = calculer_difficulte()
    
    en_cours = True
    
    while en_cours:
        
        # On regarde si le joueur appuie sur des touches
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    dernier_score = score
                    return  # On retourne au menu
        
        # Refresh de tous les éléments du jeu
        
        # On fait bouger le fond
        fond_y1 += vitesse_fond
        fond_y2 += vitesse_fond
        if fond_y1 >= HAUTEUR_ECRAN:
            fond_y1 = -HAUTEUR_ECRAN
        if fond_y2 >= HAUTEUR_ECRAN:
            fond_y2 = -HAUTEUR_ECRAN
        
        # On met à jour le joueur
        joueur.gerer_commandes(pygame.key.get_pressed())
        joueur.mettre_a_jour(LARGEUR_ECRAN, HAUTEUR_ECRAN)
        
        # On fait apparaître des méchants
        max_ennemis = 10 if boss is None else 3
        
        if len(ennemis) < max_ennemis:
            # On continue tant que c'est pas le boss
            if boss is not None or ennemis_tues < OBJECTIF_BOSS:
                compteur_apparition += 1
                if compteur_apparition >= probabilite_apparition:
                    compteur_apparition = 0
                    ennemis.append(Ennemi(LARGEUR_ECRAN, difficulte, vague))
                    # On change un peu le temps d'apparition pour varier
                    base_time = 30 if boss is None else 90
                    probabilite_apparition = random.randint(base_time, base_time + 60)

        if boss is None:
            if ennemis_tues >= OBJECTIF_BOSS and len(ennemis) == 0:
                boss = Boss(LARGEUR_ECRAN, difficulte, vague)
        else:
            boss.mettre_a_jour(LARGEUR_ECRAN, HAUTEUR_ECRAN)
                
        # On bouge les ennemis
        game_over = False
        for ennemi in ennemis[:]:
            ennemi.deplacer()
            if ennemi.hors_ecran(HAUTEUR_ECRAN):
                ennemis.remove(ennemi)
                game_over = True 
        
        # On met à jour les effets d'explosion
        for explosion in explosions[:]:
            if not explosion.mettre_a_jour():
                explosions.remove(explosion)
                
                
        #les collisions
        
        # Lazer/ Ennemi
        for laser in joueur.lasers[:]:
            laser_rect = laser.get_rect()
            touche = False
            
            for ennemi in ennemis[:]:
                if laser_rect.colliderect(ennemi.get_rect()):
                    creer_explosion(ennemi.x + ennemi.largeur // 2, ennemi.y + ennemi.hauteur // 2)
                    ennemis.remove(ennemi)
                    score += 10
                    ennemis_tues += 1
                    touche = True
                    break
            
            # Lazer/ Boss
            if boss and not touche:
                if laser_rect.colliderect(boss.get_rect()):
                    boss.vie -= laser.degats
                    touche = True
                    
                    if boss.vie <= 0:
                        creer_explosion(
                            boss.x + boss.largeur // 2,
                            boss.y + boss.hauteur // 2,
                            taille=4.0
                        )
                        
                        vague += 1
                        if vague > 5:
                            vague = 1
                            niveau += 1
                        
                        difficulte = calculer_difficulte()
                        
                        if joueur.niveau_vaisseau < 6:
                            joueur.ameliorer()
                        
                        boss = None
                        ennemis_tues = 0
                        OBJECTIF_BOSS = 20 + (niveau - 1) * 5
                        score += 500 * niveau
                        
            if touche:
                joueur.lasers.remove(laser)

        # verification des collisions joueur/enemis
        joueur_rect = joueur.get_rect()
        
        for ennemi in ennemis[:]:
            if joueur_rect.colliderect(ennemi.get_rect()):
                joueur.subir_degats(20)
                creer_explosion(ennemi.x + ennemi.largeur // 2, ennemi.y + ennemi.hauteur // 2)
                ennemis.remove(ennemi) # Il explose aussi
                
        if boss:
            if joueur_rect.colliderect(boss.get_rect()):
                joueur.subir_degats(30)
                
            for laser_boss in boss.lasers[:]:
                if joueur_rect.colliderect(laser_boss.get_rect()):
                    joueur.subir_degats(15)
                    boss.lasers.remove(laser_boss)
    
        # verification des collisions joueur/enemis
        if joueur.est_mort():
            creer_explosion(joueur.x + joueur.largeur // 2, joueur.y + joueur.hauteur // 2)
            creer_explosion(joueur.x + joueur.largeur // 2, joueur.y + joueur.hauteur // 2)
            game_over = True

        #On draw tout à l'écran 
        
        ecran.blit(fond, (0, fond_y1))
        ecran.blit(fond, (0, fond_y2))
        
        for explosion in explosions:
            explosion.dessiner(ecran)
        
        for ennemi in ennemis:
            ennemi.dessiner(ecran)
        
        if boss:
            boss.dessiner(ecran)
        
        if not game_over and en_cours:
            joueur.dessiner(ecran)
        
        # Les textes en haut
        texte_score = police_ui.render(f"Score: {score}", True, BLANC)
        ecran.blit(texte_score, (10, 10))
        
        texte_vague = police_info.render(f"Ennemis: {ennemis_tues}/{OBJECTIF_BOSS}", True, BLANC)
        ecran.blit(texte_vague, (10, 45))
        
        texte_niveau = police_info.render(f"Niveau: {niveau} - Vague: {vague}/5", True, CYAN)
        ecran.blit(texte_niveau, (10, 75))
        
        texte_vaisseau = police_info.render(f"Vaisseau: Niv.{joueur.niveau_vaisseau}", True, VERT)
        ecran.blit(texte_vaisseau, (LARGEUR_ECRAN - 150, 10))
        
        joueur.dessiner_barre_vie(ecran, LARGEUR_ECRAN)
        
        pygame.display.flip()
        horloge.tick(FPS)
        
        # Si c'est perdu : 
        if game_over:
            
            # On attend un peu pour voir l'explosion
            for _ in range(120):
                for evenement in pygame.event.get():
                    if evenement.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                
                # Le fond bouge encore
                fond_y1 += vitesse_fond
                fond_y2 += vitesse_fond
                if fond_y1 >= HAUTEUR_ECRAN:
                    fond_y1 = -HAUTEUR_ECRAN
                if fond_y2 >= HAUTEUR_ECRAN:
                    fond_y2 = -HAUTEUR_ECRAN
                
                # Les explosions finissent
                for explosion in explosions[:]:
                    if not explosion.mettre_a_jour():
                        explosions.remove(explosion)
                
                # On refresh une dernière fois
                ecran.blit(fond, (0, fond_y1))
                ecran.blit(fond, (0, fond_y2))
                for explosion in explosions:
                    explosion.dessiner(ecran)
                for ennemi in ennemis:
                    ennemi.dessiner(ecran)
                if boss:
                    boss.dessiner(ecran)
                texte_score = police_ui.render(f"Score: {score}", True, BLANC)
                ecran.blit(texte_score, (10, 10))
                pygame.display.flip()
                horloge.tick(FPS)
            
            dernier_score = score
            return  # Retour au menu

# On recommence la boucle
while True:
    afficher_menu()
    lancer_partie()
