import pygame

class Laser:
    def __init__(self, x, y, direction=-1, couleur=(255, 255, 0), vitesse=10):
        # direction : -1 ça monte (joueur), 1 ça descend (ennemis)
        # vitesse = vitesse du laser
        self.x = x
        self.y = y
        self.largeur = 5
        self.hauteur = 20
        self.vitesse = vitesse * direction  # Hop on inverse si besoin
        self.couleur = couleur
        self.direction = direction
        self.degats = 1  # Pour faire mal
        
    def deplacer(self):
        # Le laser avance tout droit
        self.y += self.vitesse
        
    def dessiner(self, ecran):
        pygame.draw.rect(ecran, self.couleur, (self.x, self.y, self.largeur, self.hauteur))
        
    def hors_ecran(self, hauteur_ecran):
        # Si on le voit plus, on l'enlève
        if self.direction == -1: # Il est parti en haut
            return self.y + self.hauteur < 0
        else: # Il est parti en bas
            return self.y > hauteur_ecran

    def get_rect(self):
        # La hitbox du laser
        return pygame.Rect(self.x, self.y, self.largeur, self.hauteur)


class MegaLaser:
    def __init__(self, x, y, joueur_ref):
        # Implementation de A* pour consigne donné pour cours de IA
        self.x = x
        self.y = y
        self.largeur = 15  
        self.hauteur = 60  
        self.vitesse = 6   # ON rends le laser un peu plus lent pour laisser le temps d'esquiver
        self.couleur = (217, 0, 255) 
        self.degats = 3    # Fait plus de degarts que les lazer normaux
        
        # Référence au joueur comme cible que on track
        self.joueur = joueur_ref
        self.distance_arret_tracking = 100  # On arrete la tracking à 100px du joueur pour rendre le laser evitable
        
    def deplacer(self):
        # Desccente du lazer
        self.y += self.vitesse
        
        # Calcul de la distance avec le joueur
        # On calcule la différence en X
        centre_laser = self.x + self.largeur // 2
        centre_joueur = self.joueur.x + self.joueur.largeur // 2
        dx = centre_joueur - centre_laser
        
        # On calcule la différence en Y
        dy = self.joueur.y - self.y
        
        # Formule de la distance (on utilise Pythagore)
        dx_carre = dx * dx
        dy_carre = dy * dy
        distance = (dx_carre + dy_carre) ** 0.5
        
        # Si on est assez loin, on traque le joueur (on suit sa position X)
        if distance > self.distance_arret_tracking:
            # Le laser se déplace vers la position X du joueur
            cible_x = self.joueur.x + self.joueur.largeur // 2 - self.largeur // 2
            if self.x < cible_x:
                self.x += 3  # vitesse de tracking horizontale
            elif self.x > cible_x:
                self.x -= 3
        # Sinon le laser continue tout droit (fin du tracking)
        
    def dessiner(self, ecran):
        # stylisation du lazer
        pygame.draw.rect(ecran, self.couleur, (self.x, self.y, self.largeur, self.hauteur))
        pygame.draw.rect(ecran, (255, 0, 0), (self.x, self.y, self.largeur, self.hauteur), 2)
        
    def hors_ecran(self, hauteur_ecran):
        return self.y > hauteur_ecran

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
