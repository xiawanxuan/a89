import torch
import torch.nn as nn


class ResidualBlock(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(channels, channels, 3, padding=1),
            nn.InstanceNorm2d(channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(channels, channels, 3, padding=1),
            nn.InstanceNorm2d(channels),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.block(x)


class Autoencoder(nn.Module):
    def __init__(self, in_channels: int = 4, base_filters: int = 64, n_residual: int = 6):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(in_channels, base_filters, 7, padding=3),
            nn.InstanceNorm2d(base_filters),
            nn.ReLU(inplace=True),
            nn.Conv2d(base_filters, base_filters * 2, 4, stride=2, padding=1),
            nn.InstanceNorm2d(base_filters * 2),
            nn.ReLU(inplace=True),
            nn.Conv2d(base_filters * 2, base_filters * 4, 4, stride=2, padding=1),
            nn.InstanceNorm2d(base_filters * 4),
            nn.ReLU(inplace=True),
        )
        self.residual = nn.Sequential(*[ResidualBlock(base_filters * 4) for _ in range(n_residual)])
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(base_filters * 4, base_filters * 2, 4, stride=2, padding=1),
            nn.InstanceNorm2d(base_filters * 2),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(base_filters * 2, base_filters, 4, stride=2, padding=1),
            nn.InstanceNorm2d(base_filters),
            nn.ReLU(inplace=True),
            nn.Conv2d(base_filters, 3, 7, padding=3),
            nn.Tanh(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        enc = self.encoder(x)
        res = self.residual(enc)
        return self.decoder(res)


class Discriminator(nn.Module):
    def __init__(self, in_channels: int = 3, base_filters: int = 64):
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv2d(in_channels, base_filters, 4, stride=2, padding=1),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(base_filters, base_filters * 2, 4, stride=2, padding=1),
            nn.InstanceNorm2d(base_filters * 2),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(base_filters * 2, base_filters * 4, 4, stride=2, padding=1),
            nn.InstanceNorm2d(base_filters * 4),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(base_filters * 4, base_filters * 8, 4, stride=2, padding=1),
            nn.InstanceNorm2d(base_filters * 8),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(base_filters * 8, 1, 4, padding=1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)


class DamageDetector(nn.Module):
    def __init__(self, in_channels: int = 3, base_filters: int = 32):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(in_channels, base_filters, 4, stride=2, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(base_filters, base_filters * 2, 4, stride=2, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(base_filters * 2, base_filters * 4, 4, stride=2, padding=1),
            nn.ReLU(inplace=True),
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(base_filters * 4, base_filters * 2, 4, stride=2, padding=1),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(base_filters * 2, base_filters, 4, stride=2, padding=1),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(base_filters, 1, 4, stride=2, padding=1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.decoder(self.encoder(x))
