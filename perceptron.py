import random

# Classe simple pour l'intelligence artificielle
class Perceptron:
    
    def __init__(self, nombre_entrees):
        # On crée une liste pour stocker l'importance de chaque info (les poids)
        self.poids = []
        
        # - On remplit la liste avec des nombres au hasard
        for i in range(nombre_entrees):
            # on choiisit un nombre entre -1 et 1
            nombre_au_pif = random.uniform(-1, 1)
            self.poids.append(nombre_au_pif)
            
        # Le biais c'est pour ajuster la sensibilité
        self.bias = 0

    def predire(self, informations):
        # Reflexion du boss
        
        # On commence le calcul à 0
        somme_totale = 0
        
        # On ajoute le biais
        somme_totale = somme_totale + self.bias
        
        #On regarde chaque information une par une
        # len(informations) nous donne combien il y a d'infos
        taille_liste = len(informations)
        
        for i in range(taille_liste):
            valeur = informations[i]       # Le type d'info (ex: la vie)
            importance = self.poids[i]     # Son importance
            
            # On multiplie et on ajoute au total
            somme_totale = somme_totale + (valeur * importance)
        
        # Maintenant on décide : Oui ou Non ?
        if somme_totale > 0:
            return 1
        else:
            return 0
