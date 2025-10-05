import asyncio
import time
import numpy as np
import math

from shark.eddy import Eddy, EddyMap, eddies

xtemperature = np.random.randint(10, 30, (200, 200))
xchlorophyl = np.random.randint(0, 100, (200, 200))
n_sharks = 2000

"""EddyMap = np.eye(8)
TemperatureMap = np.eye(8)
ChlorophylMap = np.eye(8)"""

TemperatureMap = xtemperature
ChlorophylMap = xchlorophyl



deltaT = 60*60.

class Shark():
    def __init__(self, position = np.zeros(2), speed = 0.0009,mass = 1):
        # Le vecteur de vitesse du requin
        self.velocity = np.zeros(2)
        # Vitesse constante, en km/s
        self.speed = speed
        # La position x,y du requin ( on pourra utiliser latitude, longitude plus tard )
        self.position = position

        # Largeur et hauteur du planisphère en taille réelle
        self.tailleMonde = np.array([20003.932, 40075.017])
        # Résolution selon la largeur et longueur du planisphère
        self.res = np.array([TemperatureMap.shape[0], TemperatureMap.shape[1]])
        # Ecart entre deux point du planisphère selon la largeur et longueur
        self.ecartPoint = self.tailleMonde / (self.res + 1)
        # Les emplacements dans les données du requin les plus proches de la position réelle du requin, en haut à gauche, à droite, et bas à gauche et à droite
        self.matrixPosition = np.zeros([2,2,2], dtype=np.int64)
        self.updateMatrixPosition()

        # La profondeur du requin en m
        self.depth = 0
        # La 'masse' qui vient gérer l'influence des forces sur le requin
        self.mass = mass
        # La période entre 2 changements de position du requin




    def updateVelocity(self):
        "Updates velocity with according to exterior forces"
        self.velocity += self.forces() * deltaT
        self.velocity /= np.linalg.norm(self.velocity)
        self.velocity *= self.speed
        return

    def updatePosition(self):
        "Updates position with a set velocity"
        self.position += self.velocity * deltaT
        self.position %= self.tailleMonde
        return

    def updateMatrixPosition(self):
        "Finds the nearest points around the shark's real position"
        nbEcarts = np.int64(self.position / self.ecartPoint)
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
        return self.EddiesForce() + self.TemperatureForce() + self.ChlorophylForce()

    def gradientX(self, Map, position):
        return (Map[(position[0]+1) % self.res[0]][position[1]] - Map[(position[0]-1) % self.res[0]][position[1]]) / 2

    def gradientY(self, Map, position):
        return (Map[position[0]][(position[1] + 1) % self.res[1]] - Map[position[0]][(position[1] - 1) % self.res[1]]) / 2

    def gradient(self, Map, position):
        return np.array([self.gradientX(Map, position), self.gradientY(Map, position)])

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

        gradients = np.array([
            self.gradient(TemperatureMap, self.matrixPosition[0,0]),
            self.gradient(TemperatureMap, self.matrixPosition[0,1]),
            self.gradient(TemperatureMap, self.matrixPosition[1,0]),
            self.gradient(TemperatureMap, self.matrixPosition[1,1])
        ])

        grad = np.zeros(2)
        for i in range(gradients.shape[0]):
            gradients[i] *= distances[i]
            grad += gradients[i]

        return - grad

    def ChlorophylForce(self):
        offset = self.position - self.matrixPosition[0, 0] * self.ecartPoint
        distances = np.array([
            np.linalg.norm(offset),
            math.sqrt(offset[0]**2 + self.ecartPoint[1]**2),
            math.sqrt(self.ecartPoint[0]**2 + offset[1]**2),
            np.linalg.norm(self.ecartPoint)
        ])
        distances /= np.linalg.norm(distances)
        gradients = np.array([
            self.gradient(ChlorophylMap, self.matrixPosition[0,0]),
            self.gradient(ChlorophylMap, self.matrixPosition[0,1]),
            self.gradient(ChlorophylMap, self.matrixPosition[1,0]),
            self.gradient(ChlorophylMap, self.matrixPosition[1,1])
        ])

        grad = np.zeros(2)
        for i in range(gradients.shape[0]):
            gradients[i] *= distances[i]
            grad += gradients[i]

        return - grad

    def EddiesRecup(self):
        i = np.arange(
            self.matrixPosition[0,0,0] - 50,
            self.matrixPosition[0,0,0] + 51
        ) % self.res[0]

        j = np.arange(
            self.matrixPosition[0,0,1] - 50,
            self.matrixPosition[0,0,1] + 51
        ) % self.res[1]

        mat = EddyMap[np.ix_(i, j)]
        return list(set(mat[mat != None]))

    def CoriolisForce(self, eddy, direction, dist):
        force = np.zeros(2)
        w = np.exp(
            - dist**2 / (2 * eddy.std**2)
        ) * eddy.amplitude
        force += - 2 * w * self.mass * np.array(self.velocity[1], -self.velocity[0])
        force += - self.mass * w**2 * direction
        return force

    def EddiesForce(self):
        eddies = self.EddiesRecup()
        force = np.zeros(2)
        for eddy in eddies:
            direction = eddy.pos - self.position
            dist = np.linalg.norm(direction)
            force += self.CoriolisForce(eddy, direction, dist)
            force += eddy.amplitude * abs(direction.sum()) * np.exp(-((direction / eddy.std)**2).sum() / 2) * direction / dist
        return force


sharks = [
    Shark(
        position = (eddies[i].pos + np.array([90, 180])) *
        np.array([10001.5, 20037.5]) / np.array([90, 180]) +
        np.random.normal(2) * 40,
        speed = 0.0009,
        mass = np.random.uniform(500, 1000)
    )
    for i in range(n_sharks)
]


def get_shark_positions(sharks):
    return [
        (
            (shark.position - np.array([10001.5, 20037.5])) /
            np.array([10001.5, 20037.5]) *
            np.array([90, 180])
        ).tolist()
        for shark in sharks
    ]


async def simulate_sharks(sharks):
    while True:
        #print("----- starting -----")
        for shark in sharks:
            #print("moving shark")
            shark.move()

        # Ensure this function runs approximately once every second
        now = time.time()
        wait_time = 1 - (now % 1)
        await asyncio.sleep(wait_time)
