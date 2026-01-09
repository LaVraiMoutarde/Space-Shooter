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
