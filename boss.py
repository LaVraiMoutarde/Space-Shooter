import pygame
import os
import random
from laser import Laser

# Le boss (c'est moi le boss)
class Boss:
    
    def __init__(self, largeur_ecran, difficulte=1.0, niveau_vague=1):

        # ON choisis son image
        dossier_vague = min(niveau_vague, 4)
        chemin_image = os.path.join('asssets', 'Enemies', f'Vague{dossier_vague}', 'Boss Ship.png')
        image_brute = pygame.image.load(chemin_image)
        
        self.largeur = 200
        self.hauteur = 200
        self.image = pygame.transform.scale(image_brute, (self.largeur, self.hauteur))
        self.image = pygame.transform.rotate(self.image, 180) # Il regarde vers le bas
        
        # Il arrive au milieu
        self.x = largeur_ecran // 2 - self.largeur // 2
        self.y = -250 # Il est caché là pour l'instant
        
        # Fonctionnement de la vie
        self.vie_max = int(40 * (1 + (difficulte - 1) * 0.4))  # Beaucoup de vie
        self.vie = self.vie_max
        self.vitesse = 2 + (difficulte - 1) * 0.3
        self.difficulte = difficulte
        
        # Arrivé du boss
        self.entree_en_scene = True # Au début il descend
        self.direction_x = 1 # Après il va aller à droite
        
        # Tir
        self.lasers = []
        self.cooldown_tir = 0
        self.cadence_tir = max(40, int(100 / (1 + (difficulte - 1) * 0.1)))  # Il mitraille !
        
    def deplacer(self, largeur_ecran):
        # Comment il bouge
        
        if self.entree_en_scene:
            # D'abord il fait son entrée
            self.y += self.vitesse
            if self.y >= 50:
                self.entree_en_scene = False
        else:
            # Maintenant il fait des allers-retours
            self.x += self.vitesse * self.direction_x
            
            if self.x <= 0 or self.x + self.largeur >= largeur_ecran:
                self.direction_x *= -1
        
    def tirer(self):
        if self.cooldown_tir > 0:
            self.cooldown_tir -= 1
        else:
            laser_g = Laser(self.x + 20, self.y + self.hauteur, direction=1, couleur=(255, 0, 0), vitesse=6)
            laser_d = Laser(self.x + self.largeur - 20, self.y + self.hauteur, direction=1, couleur=(255, 0, 0), vitesse=6)
            
            self.lasers.append(laser_g)
            self.lasers.append(laser_d)
            
            self.cooldown_tir = self.cadence_tir
            
    def mettre_a_jour(self, largeur_ecran, hauteur_ecran):
        # On refresh tout ce qui se passe pour le boss
        self.deplacer(largeur_ecran)
        self.tirer()
        
        # On s'occupe de ses lasers
        for laser in self.lasers[:]:
            laser.deplacer()
            if laser.hors_ecran(hauteur_ecran):
                self.lasers.remove(laser)

    def dessiner(self, ecran):
        # On l'affiche
        ecran.blit(self.image, (self.x, self.y))
        
        #Et ses lasers
        for laser in self.lasers:
            laser.dessiner(ecran)
            
        # On montre sa vie pour savoir quand il va mourir
        self.dessiner_barre_vie(ecran)
        
    def dessiner_barre_vie(self, ecran):
        # Une barre de vie juste au dessus de sa tête
        pygame.draw.rect(ecran, (255, 0, 0), (self.x, self.y - 20, self.largeur, 10))
        ratio_vie = self.vie / self.vie_max
        pygame.draw.rect(ecran, (0, 255, 0), (self.x, self.y - 20, self.largeur * ratio_vie, 10))
        
    def get_rect(self):
        # La hitbox du boss
        return pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
