import pygame
import os
import random
from laser import Laser, MegaLaser
from perceptron import Perceptron

# Le boss (c'est moi le boss)
class Boss:
    
    def __init__(self, largeur_ecran, joueur_ref, difficulte=1.0, niveau_vague=1, poids_memoire=None):

        # On choisis son image
        dossier_vague = niveau_vague
        if dossier_vague > 4:
            dossier_vague = 4
        chemin_image = os.path.join('asssets', 'Enemies', f'Vague{dossier_vague}', 'Boss Ship.png')
        image_brute = pygame.image.load(chemin_image)
        
        self.largeur = 200
        self.hauteur = 200
        self.image = pygame.transform.scale(image_brute, (self.largeur, self.hauteur))
        self.image = pygame.transform.rotate(self.image, 180) # Il regarde vers le bas
        
        # Il arrive au milieu
        self.x = largeur_ecran // 2 - self.largeur // 2
        self.y = -250 # Il est caché là (-250en y) pour l'instant
        
        # Fonctionnement de la vie
        # Plus la difficulté augmente, plus le boss a de vie
        bonus_vie = (difficulte - 1) * 0.6
        self.vie_max = int(40 * (1 + bonus_vie))
        self.vie = self.vie_max
        self.vitesse = 2 + (difficulte - 1) * 0.3
        self.difficulte = difficulte
        
        # Référence au joueur pour le mega laser traqueur
        self.joueur = joueur_ref
        
        # Arrivé du boss
        self.entree_en_scene = True # Au début il descend
        self.direction_x = 1 # Après il va aller à droite
        
        # Tir
        self.lasers = []
        self.cooldown_tir = 0
        
        # Calcul de la cadence de tir (plus c'est difficile, plus il tire vite)
        bonus_cadence = (difficulte - 1) * 0.1
        cadence_calculee = int(100 / (1 + bonus_cadence))
        if cadence_calculee < 40:
            self.cadence_tir = 40
        else:
            self.cadence_tir = cadence_calculee
        
        # Mega laser spécial (tire à 50% et 5% de vie)
        self.a_tire_50_pourcent = False
        self.a_tire_5_pourcent = False
        
        # Le Cerveau du Boss : (3 entrées : Vie, distance X, distance Y)
        # Il va décider s'il doit accélérer ou ralentir
        self.cerveau = Perceptron(3)
        
        # SI on a une mémoire des anciens boss, on l'utilise
        if poids_memoire is not None:
            self.cerveau.poids = poids_memoire
        else:
            # Sinon on met les valeurs de base
            self.cerveau.poids = [0.8, -0.5, 0.2] 
        
    def deplacer(self, largeur_ecran):
        # Comment il bouge
        
        if self.entree_en_scene:
            # il fait son entrée
            self.y += self.vitesse
            if self.y >= 50:
                self.entree_en_scene = False
        else:
            # Calcul des infos pour le cerveau
            vie_perdue = 1.0 - (self.vie / self.vie_max)
            
            difference_x = self.joueur.x - self.x
            distance_cote = abs(difference_x) / largeur_ecran
            
            proche = 0
            if abs(self.joueur.y - self.y) < 300:
                proche = 1
            
            # On demande au cerveau
            infos = [vie_perdue, distance_cote, proche]
            decision = self.cerveau.predire(infos)
            
            # On applique la décision
            vitesse_actuelle = self.vitesse
            
            if decision == 1:
                vitesse_actuelle = self.vitesse * 2.5
            
            self.x += vitesse_actuelle * self.direction_x
            
            if self.x <= 0:
                self.direction_x = 1
            if self.x + self.largeur >= largeur_ecran:
                self.direction_x = -1
        
    def tirer(self):
        if self.cooldown_tir > 0:
            self.cooldown_tir -= 1
        else: # sinon on tire (avec le design du laser)
            laser_g = Laser(self.x + 20, self.y + self.hauteur, direction=1, couleur=(255, 0, 0), vitesse=6)
            laser_d = Laser(self.x + self.largeur - 20, self.y + self.hauteur, direction=1, couleur=(255, 0, 0), vitesse=6)
            
            self.lasers.append(laser_g)
            self.lasers.append(laser_d)
            
            self.cooldown_tir = self.cadence_tir
    
    def tirer_mega_laser(self):
        # On tire un gros laser traqueur depuis le centre du boss
        x_tir = self.x + self.largeur // 2 - 7  # on repère le centre du boss (15/2 = 7)
        y_tir = self.y + self.hauteur
        mega = MegaLaser(x_tir, y_tir, self.joueur)
        self.lasers.append(mega)
            
    def mettre_a_jour(self, largeur_ecran, hauteur_ecran):
        # On refresh tout ce qui se passe pour le boss
        self.deplacer(largeur_ecran)
        self.tirer()
        
        # Vérification des seuils pour le mega laser
        ratio_vie = self.vie / self.vie_max
        
        # à 50% de vie, on tire le mega laser
        if ratio_vie <= 0.5 and not self.a_tire_50_pourcent:
            self.tirer_mega_laser()
            self.a_tire_50_pourcent = True
        
        # à 5% de vie, on tire le dernier mega laser
        if ratio_vie <= 0.05 and not self.a_tire_5_pourcent:
            self.tirer_mega_laser()
            self.a_tire_5_pourcent = True
        
        #On s'occupe de ses lasers
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
