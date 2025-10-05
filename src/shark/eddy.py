import numpy as np
import csv
from scipy.spatial import cKDTree

class Eddy:
    def __init__(self, pos=np.zeros(2), amplitude=1, radius=400):
        self.pos = pos
        self.amplitude = amplitude
        self.radius = radius
        self.std = radius / 2

    def updateRadius(self, radius):
        self.radius = radius
        self.std = radius / 2  # fixed typo from your code (was self.rayon)

    def updateAmplitude(self, amplitude):
        self.amplitude = amplitude

    def updatePosition(self, pos):
        self.pos = pos


# --- Load cyclone and anticyclone data ---
def load_csv(path):
    with open(path) as f:
        return [[float(x) for x in row] for row in csv.reader(f)]


data_cyclones = load_csv("shark/data_cyclones.csv")
data_anticyclones = load_csv("shark/data_anticyclones.csv")

print(data_cyclones, type(data_cyclones))

# --- Create Eddy objects ---
eddies = []
for lat, lon, amp, _ in np.concatenate([data_cyclones, data_anticyclones]):
    eddies.append(Eddy(pos=np.array([lat, lon]), amplitude=amp, radius=400))
eddies = np.array(eddies)

def generate_eddy_matrix_fast(eddies, size=512):
    H = W = size
    coords = np.array([e.pos for e in eddies])
    min_vals = coords.min(axis=0)
    max_vals = coords.max(axis=0)
    ranges = np.maximum(max_vals - min_vals, 1e-9)
    coords = (coords - min_vals) / ranges

    tree = cKDTree(coords)

    xs = (np.arange(W) + 0.5) / W
    ys = (np.arange(H) + 0.5) / H
    X, Y = np.meshgrid(xs, ys)
    pts = np.stack([X.ravel(), Y.ravel()], axis=-1)

    _, nearest = tree.query(pts)
    nearest = nearest.reshape((H, W))
    return eddies[nearest]

EddyMap = generate_eddy_matrix_fast(eddies, size=512)
