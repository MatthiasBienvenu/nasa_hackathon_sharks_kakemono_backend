import numpy as np
import pandas as pd
from matplotlib import cm
from PIL import Image

# 1. Load CSV
arr = np.rot90(pd.read_csv("sla.csv", header=None).to_numpy().T)
np.save("array.npy", arr)

# 2. Normalize values (ignore NaN)
valid_mask = ~np.isnan(arr)
min_val, max_val = np.nanmin(arr), np.nanmax(arr)
norm_arr = (arr - min_val) / (max_val - min_val)
norm_arr[~valid_mask] = 0  # placeholder for NaN

# 3. Map to RGBA using a matplotlib colormap
cmap = cm.get_cmap('bwr')  # or 'viridis', 'bwr'
rgba_arr = cmap(norm_arr)  # float32 0..1, shape: HxWx4

# 4. Convert to 0-255
rgba_arr = (rgba_arr * 255).astype(np.uint8)
rgba_arr[~valid_mask] = [0, 0, 0, 0]  # fully transparent for NaN

# 5. Save PNG
img = Image.fromarray(rgba_arr, mode='RGBA')
img.save("heatmap.png")
