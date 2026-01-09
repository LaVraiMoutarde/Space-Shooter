import pygame
import os
import random

class Ennemi:
    
    def __init__(self, largeur_ecran, difficulte=1.0, niveau_vague=1):
        # On a besoin de la largeur pour pas qu'il spawn hors de l'écran
        # La difficulté et la vague changent sa vitesse et son image
        
        # On choisis l'image selon la vague (y'a 4 (lié au vagues) types d'ennemis)
        dossier_vague = min(niveau_vague, 4)
        chemin_image = os.path.join('asssets', 'Enemies', f'Vague{dossier_vague}', 'Normal Ship.png')
        image_brute = pygame.image.load(chemin_image)
        
        # Taille du méchant
        self.largeur = 60
        self.hauteur = 60
        
        # On le mets à la bonne taille et on le retourne (il arrive d'en haut)
        self.image = pygame.transform.scale(image_brute, (self.largeur, self.hauteur))
        self.image = pygame.transform.rotate(self.image, 180)
        
        # Position de départ
        # Il apparaît n'importe où sur la largeur
        self.x = random.randint(0, largeur_ecran - self.largeur)
        self.y = -100  # Caché juste au-dessus de l'écran pour l'effet de surprise
        
        # Il est plus ou moins fort selon la difficulté
        vitesse_base = random.randint(8, 14) / 10.0
        # Plus le jeu avance, plus il descend vite
        self.vitesse = vitesse_base * (1 + (difficulte - 1) * 0.2)
        # Il devient plus résistant aussi
        self.vie = 1 + int((difficulte - 1) * 0.5)
    
    def deplacer(self):
        # Il tombe vers le bas
        self.y += self.vitesse
        
    def dessiner(self, ecran):
        # On l'affiche
        ecran.blit(self.image, (self.x, self.y))
        
    def hors_ecran(self, hauteur_ecran):
        # S'il est passé tout en bas,le joueur perd
        return self.y > hauteur_ecran

    def get_rect(self):
        # Pour savoir si on le touche
        return pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
