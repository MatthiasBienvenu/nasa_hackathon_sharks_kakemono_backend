import numpy as np
import os
from PIL import Image

# === Configuration ===
input_path = "test/inputs.npy"       # path to your .npy file
output_dir = "test/inputs"    # directory to store the images

arr = np.load(input_path)   # shape: (4750, 300, 150)

print(arr.shape, arr.dtype, arr.min(), arr.max())

for i, img in enumerate(arr):
    img = np.clip(img, 0, 255).astype(np.uint8)
    im = Image.fromarray(img)
    im.save(os.path.join(output_dir, f"{i}.png"))

print(f"Saved {len(arr)} images to {output_dir}")