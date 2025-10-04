import os
import numpy as np
from torch.utils.data import Dataset
from torchvision.transforms import ToTensor
import torch
from PIL import Image


class CycloneDataset(Dataset):
    def __init__(self, test: bool, inputs_transform=None, targets_transform=None):
        self.path = f"dataset/{'test' if test else 'train'}"
        self.inputs_transform = inputs_transform
        self.targets_transform = targets_transform

    def __len__(self):
        return len(os.listdir(self.path))

    def __getitem__(self, idx: int):
        inputs = Image.open(f"{self.path}/inputs/{idx}.png")
        targets = Image.open(f"{self.path}/targets/{idx}.png")

        if self.inputs_transform:
            inputs = self.inputs_transform(inputs)

        if self.targets_transform:
            targets = self.targets_transform(targets)

        return inputs, targets


if __name__ == "__main__":
    data = CycloneDataset(
        test=True,
        transform=ToTensor()
    )

    x, y = data[5]

    print(x.dtype, x.shape)
    print(y.dtype, y.shape)
    print(len(data))