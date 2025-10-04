import torch
import torch.nn as nn
import torch.nn.functional as F

import numpy as np
import matplotlib.pyplot as plt




class DoubleConv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.double_conv(x)




class UNet(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, features: list):
        super().__init__()

        # Down part
        self.downs = nn.ModuleList()
        for f in features:
            self.downs.append(DoubleConv(in_channels, f))
            in_channels = f

        # DownSample
        self.down_sample = nn.MaxPool2d(kernel_size=2, stride=2)

        # Bottleneck
        self.bottleneck = DoubleConv(features[-1], features[-1]*2)

        # Up part
        self.ups = nn.ModuleList([
            DoubleConv(f*2, f)
            for f in reversed(features)
        ])

        # UpSample
        self.up_samples = nn.ModuleList([
            nn.ConvTranspose2d(f*2, f, kernel_size=2, stride=2)
            for f in reversed(features)
        ])

        # Final conv
        self.final_conv = nn.Conv2d(features[0], out_channels, kernel_size=1)


    def forward(self, x):
        skip_connections = []
        cur = x

        # Encoder
        for down in self.downs:
            cur = down(cur)
            skip_connections.append(cur)
            cur = self.down_sample(cur)

        # Bottleneck
        cur = self.bottleneck(cur)

        # Decoder
        skip_connections = skip_connections[::-1]
        for up, up_sample, skip in zip(self.ups, self.up_samples, skip_connections):
            cur = up_sample(cur)
            cur = torch.cat((skip, cur), dim=1) # Concatenate the channels
            cur = up(cur)

        return self.final_conv(cur)  # raw logits (no activation)





if __name__ == "__main__":
    pass
