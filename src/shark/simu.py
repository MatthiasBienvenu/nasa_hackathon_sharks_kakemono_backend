import numpy as np
import math

EddyMap = np.eye(8)
TemperatureMap = np.eye(8)
ChlorophylMap = np.eye(8)
deltaT = 60*60

class Shark():

    def __init__(self, timeScale):
        # Le vecteur de vitesse du requin
        self.velocity = np.zeros(2)
        # La position x,y du requin ( on pourra utiliser latitude, longitude plus tard )
        self.position = np.zeros(2)

        # Largeur et hauteur du planisphère en taille réelle
        self.tailleMonde = np.array([20003.932, 40075.017])
        # Résolution selon la largeur et longueur du planisphère
        self.res = np.array([TemperatureMap.shape[0], TemperatureMap.shape[1]])
        # Ecart entre deux point du planisphère selon la largeur et longueur
        self.ecartPoint = self.tailleMonde / (self.res + 1)
        # Les emplacements dans les données du requin les plus proches de la position réelle du requin, en haut à gauche, à droite, et bas à gauche et à droite
        self.matrixPosition = np.zeros([2,2,2])
        self.updateMatrixPosition()

        # La profondeur du requin en m
        self.depth = 0
        # La 'masse' qui vient gérer l'influence des forces sur le requin
        self.mass = 1
        # La période entre 2 changements de position du requin
        

    



    def updateVelocity(self):
        "Updates velocity with according to exterior forces"
        self.velocity += self.forces() * deltaT
        return

    def updatePosition(self):
        "Updates position with a set velocity"
        self.position += self.velocity * deltaT
        self.position %= self.tailleMonde
        return
    
    def updateMatrixPosition(self):
        "Finds the nearest points around the shark's real position"
        nbEcarts = np.floor(self.position / self.ecartPoint)
        self.matrixPosition[0, 0] = nbEcarts % self.res
        self.matrixPosition[0, 1] = (nbEcarts + np.array([0, 1])) % self.res
        self.matrixPosition[1, 0] = (nbEcarts + np.array([1, 0])) % self.res
        self.matrixPosition[1, 1] = (nbEcarts + np.array([1, 1])) % self.res
        return
    
    def move(self):
        "Moves the shark"
        self.updateVelocity()
        self.updatePosition()
        self.updateMatrixPosition()
        return
    
    def forces(self):
        return self.CoriolisForce() + self.TemperatureForce() + self.ChlorophylForce() + self.EddiesForce()

    def gradientX(self, Map, position):
        return (Map[(position[0]+1) % self.resX][position[1]] - Map[(position[0]-1) % self.resX][position[1]]) / 2

    def gradientY(self, Map, position):
        return (Map[position[0]][(position[1] + 1) % self.resY] - Map[position[0]][(position[1] - 1) % self.resY]) / 2
    
    def gradient(self, Map, x, y):
        return np.array([self.gradientX(Map, x, y), self.gradientY(Map, x, y)])

    def TemperatureForce(self):
        # Offset to closest point
        offset = self.position - self.matrixPosition[0, 0] * self.ecartPoint
        # Distance to points surrounding the shark
        distances = np.array([
            np.linalg.norm(offset),
            math.sqrt(offset[0]**2 + self.ecartPoint[1]**2),
            math.sqrt(self.ecartPoint[0]**2 + offset[1]**2),
            np.linalg.norm(self.ecartPoint)
        ])
        distances /= np.linalg.norm(distances)

        gradients = np.array([self.gradient(TemperatureMap, self.matrixPosition[0][0]), self.gradient(TemperatureMap, self.matrixPosition[0][1]), self.gradient(TemperatureMap, self.matrixPosition[1][0]), self.gradient(TemperatureMap, self.matrixPosition[1][1])])
        return - distances * gradients
    
    def ChlorophylForce(self):
        offset = self.position - self.matrixPosition[0, 0] * self.ecartPoint
        distances = np.array([
            np.linalg.norm(offset),
            math.sqrt(offset[0]**2 + self.ecartPoint[1]**2),
            math.sqrt(self.ecartPoint[0]**2 + offset[1]**2),
            np.linalg.norm(self.ecartPoint)
        ])
        distances /= np.linalg.norm(distances)
        gradients = np.array([self.gradient(ChlorophylMap, self.matrixPosition[0][0]), self.gradient(ChlorophylMap, self.matrixPosition[0][1]), self.gradient(ChlorophylMap, self.matrixPosition[1][0]), self.gradient(ChlorophylMap, self.matrixPosition[1][1])])
        return - distances * gradients
    
    