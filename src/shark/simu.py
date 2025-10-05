import numpy as np
import math

class Eddy():
    def __init__(self, pos = np.zeros(2), amplitude = 1, radius = 400):
        self.pos = pos
        self.amplitude = amplitude
        self.radius = radius
        self.std = radius / 2

    def updateRadius(self, radius):
        self.radius = radius
        self.std = self.rayon / 2

    def updateAmplitude(self, amplitude):
        self.amplitude = amplitude
    
    def updatePosition(self, pos):
        self.pos = pos

eddy1 = Eddy(pos = np.array([4064., 1224.]), amplitude = 2)
eddy2 = Eddy(pos = np.array([1064., 8224.]))
eddy3 = Eddy(pos = np.array([3800., 1222.]), radius = 80)

xeddy1 = np.array([[eddy1 for _ in range(200)] for _ in range(200)])
xeddy2 = np.array([[eddy2 for _ in range(200)] for _ in range(200)])
xeddy3 = np.array([[eddy1 for _ in range(40)] for _ in range(40)])

xnone1 = np.array([[None for _ in range(40)] for _ in range(40)])
xnone = np.array([[None for _ in range(200)] for _ in range(200)])
"""xeddy3 = np.concatenate(
    np.repeat(
        np.repeat(
            xnone1,
             4,
             axis = 0
        ),
        4,
        axis = 1
    ),
    np.concatenate(
        xeddy3,
        np.repeat(
            xnone1,
            4,
            axis=1
        ),
        axis=1
    ),
    axis=0
)
xeddies = np.concatenate(
    np.concatenate(
        np.repeat(
            xnone,
            2,
            axis=0
        ),
        xeddy2,
        axis=0
    ),
    xnone,
    axis=0
)
xeddies = np.concatenate(
    xeddies,
    np.repeat(
        xnone,
        4,
        axis=0
    ),
    axis=1
)
xeddies = np.concatenate(
    xeddies,
    np.concatenate(
        xeddy3,
        np.repeat(
            xnone,
            3,
            axis=0
        ),
        axis=0
    ),
    axis=1
)
xeddies = np.concatenate(
    xeddies,
    np.concatenate(
        xeddy1,
        np.repeat(
            xnone,
            3,
            axis=0
        ),
        axis=0
    ),
    axis=1
)"""

xtemperature = np.random.randint(10, 30, (200, 200))
xchlorophyl = np.random.randint(0, 100, (200, 200))

"""EddyMap = np.eye(8)
TemperatureMap = np.eye(8)
ChlorophylMap = np.eye(8)"""

EddyMap = xeddy1
TemperatureMap = xtemperature
ChlorophylMap = xchlorophyl



deltaT = 60*60

class Shark():

    def __init__(self, position = np.zeros(2), SPEED = 0.0003,mass = 1):
        # Le vecteur de vitesse du requin
        self.velocity = np.zeros(2)
        # Vitesse constante, en km/s
        self.SPEED = SPEED
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
        self.velocity *= self.SPEED
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
            
shark = Shark(position = np.array([15000., 10000.]))

for i in range(40):
    shark.move()
    print(shark.position, shark.velocity)