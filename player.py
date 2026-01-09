import pygame
import os
from laser import Laser

#Classe du vaisseau du joueur
class Joueur:
    
    def __init__(self, x, y):
        # Poition centre pour le depart
        self.x = x
        self.y = y
        
        # taille
        self.largeur = 80
        self.hauteur = 80
        
        # On commence au niveau 1
        self.niveau_vaisseau = 1
        
        # Stats de base (ça s'améliore après)
        self.vitesse = 5
        self.degats = 1
        
        #Barre de vie (100 PV)
        self.vie_max = 100
        self.vie = self.vie_max
        
        # Gestion des tirs
        self.lasers = []
        self.cooldown_tir = 0
        self.delai_entre_tirs = 30  # Plus le chiffre est petit, plus on tire vite
        
        # On charge l'image du vaisseau
        self.charger_image()
    
    def charger_image(self):
        # On prend l'image qui correspond à mon niveau
        chemin_image = os.path.join('asssets', 'Space ships', f'Level {self.niveau_vaisseau}.png')
        image_brute = pygame.image.load(chemin_image)
        image_scaled = pygame.transform.scale(image_brute, (self.largeur, self.hauteur))
        
        #petite fix : à partir du niveau 2 les images sont penchées, donc on les redresse
        if self.niveau_vaisseau >= 2:
            self.image = pygame.transform.rotate(image_scaled, 90)
        else:
            self.image = image_scaled
    
    def ameliorer(self):
        #amélioration du vaisseau
        if self.niveau_vaisseau < 6:
            self.niveau_vaisseau += 1
            
            # + vitesse, + degats, + vitesse de tir
            self.vitesse += 0.5
            self.delai_entre_tirs = max(15, self.delai_entre_tirs - 3)
            if self.niveau_vaisseau in [3, 5]:
                self.degats += 1
            
            # nouveau asset
            self.charger_image()
            return True
        return False
    
    def subir_degats(self, degats):
        # degats reçus
        self.vie -= degats
        if self.vie < 0:
            self.vie = 0
    
    def est_mort(self):
        # plus de vie = fin de partie
        return self.vie <= 0
    
    def gerer_commandes(self, touches):
        # commande de déplacement
        if touches[pygame.K_LEFT] or touches[pygame.K_q]:
            self.x -= self.vitesse
        if touches[pygame.K_RIGHT] or touches[pygame.K_d]:
            self.x += self.vitesse
        if touches[pygame.K_UP] or touches[pygame.K_z]:
            self.y -= self.vitesse
        if touches[pygame.K_DOWN] or touches[pygame.K_s]:
            self.y += self.vitesse
    
    def tirer(self):
        # tir de laser
        if self.cooldown_tir == 0:
            largeur_laser = 5
            x_tir = self.x + self.largeur // 2 - largeur_laser // 2
            y_tir = self.y
            
            nouveau_laser = Laser(x_tir, y_tir)
            nouveau_laser.degats = self.degats
            self.lasers.append(nouveau_laser)
            
            self.cooldown_tir = self.delai_entre_tirs
 
    def mettre_a_jour(self, largeur_ecran, hauteur_ecran):
        # on refresh tout
        
        # tir
        self.tirer()
        
        # limite de position
        self.limiter_position(largeur_ecran, hauteur_ecran)
        
        # Le cooldown diminue toujours plus
        if self.cooldown_tir > 0:
            self.cooldown_tir -= 1
            
        # on fait avancer mes lasers
        for laser in self.lasers[:]: 
            laser.deplacer()
            if laser.hors_ecran(hauteur_ecran):
                self.lasers.remove(laser)
    
    def limiter_position(self, largeur_ecran, hauteur_ecran):
        # Si on tape contre les murs, on se fait bloquer
        if self.x < 0: self.x = 0
        if self.x + self.largeur > largeur_ecran: self.x = largeur_ecran - self.largeur
        if self.y < 0: self.y = 0
        if self.y + self.hauteur > hauteur_ecran: self.y = hauteur_ecran - self.hauteur
        
    def get_rect(self):
        # Savoir où on est (pour les collisions)
        return pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
    
    def dessiner(self, ecran):
        # On affiche à l'écran
        ecran.blit(self.image, (self.x, self.y))
        
        # + les lasers
        for laser in self.lasers:
            laser.dessiner(ecran)
    
    def dessiner_barre_vie(self, ecran, largeur_ecran):
        # Barre de vie du vaisseau 
        largeur_barre = 150
        hauteur_barre = 10
        x = largeur_ecran - 170
        y = 35
        
        # Le fond rouge
        pygame.draw.rect(ecran, (100, 0, 0), (x, y, largeur_barre, hauteur_barre))
        
        # La vie verte
        ratio_vie = self.vie / self.vie_max
        pygame.draw.rect(ecran, (0, 200, 0), (x, y, largeur_barre * ratio_vie, hauteur_barre))
        
        # Un petit cadre blanc autour
        pygame.draw.rect(ecran, (255, 255, 255), (x, y, largeur_barre, hauteur_barre), 1)
