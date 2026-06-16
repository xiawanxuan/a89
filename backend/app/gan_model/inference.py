import os
from typing import Optional

import torch
import numpy as np
from PIL import Image
from torchvision import transforms

from app.gan_model.network import Autoencoder, Discriminator, DamageDetector
from app.config import settings

_device = None
_autoencoder = None
_detector = None


def get_device() -> torch.device:
    global _device
    if _device is None:
        if torch.cuda.is_available():
            _device = torch.device(settings.GPU_DEVICE)
        else:
            _device = torch.device("cpu")
    return _device


def load_autoencoder() -> Autoencoder:
    global _autoencoder
    if _autoencoder is not None:
        return _autoencoder

    device = get_device()
    _autoencoder = Autoencoder(in_channels=4, base_filters=64, n_residual=6)

    if os.path.exists(settings.MODEL_PATH):
        state_dict = torch.load(settings.MODEL_PATH, map_location=device, weights_only=True)
        if "autoencoder" in state_dict:
            _autoencoder.load_state_dict(state_dict["autoencoder"])
        else:
            _autoencoder.load_state_dict(state_dict)
    else:
        _autoencoder.apply(_init_weights)

    _autoencoder = _autoencoder.to(device)
    _autoencoder.eval()
    return _autoencoder


def load_detector() -> DamageDetector:
    global _detector
    if _detector is not None:
        return _detector

    device = get_device()
    _detector = DamageDetector(in_channels=3, base_filters=32)

    if os.path.exists(settings.MODEL_PATH):
        state_dict = torch.load(settings.MODEL_PATH, map_location=device, weights_only=True)
        if "detector" in state_dict:
            _detector.load_state_dict(state_dict["detector"])
    else:
        _detector.apply(_init_weights)

    _detector = _detector.to(device)
    _detector.eval()
    return _detector


def _init_weights(m):
    if isinstance(m, (torch.nn.Conv2d, torch.nn.ConvTranspose2d)):
        torch.nn.init.normal_(m.weight, 0.0, 0.02)
        if m.bias is not None:
            torch.nn.init.constant_(m.bias, 0)
    elif isinstance(m, torch.nn.InstanceNorm2d):
        if m.weight is not None:
            torch.nn.init.constant_(m.weight, 1)
        if m.bias is not None:
            torch.nn.init.constant_(m.bias, 0)


_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
])


def repair_region(image: Image.Image, x: int, y: int, w: int, h: int) -> Image.Image:
    device = get_device()
    model = load_autoencoder()

    img_w, img_h = image.size
    region = image.crop((x, y, x + w, y + h))

    region_tensor = _transform(region).unsqueeze(0).to(device)

    mask = torch.ones(1, 1, region_tensor.shape[2], region_tensor.shape[3], device=device)
    input_tensor = torch.cat([region_tensor, mask], dim=1)

    with torch.no_grad():
        output = model(input_tensor)

    output = output.squeeze(0).cpu()
    output = output * 0.5 + 0.5
    output = torch.clamp(output, 0, 1)

    repaired = transforms.ToPILImage()(output)
    repaired = repaired.resize((w, h), Image.LANCZOS)

    result = image.copy()
    result.paste(repaired, (x, y))
    return result


def detect_damage_regions(image: Image.Image, threshold: float = 0.5) -> list[dict]:
    device = get_device()
    model = load_detector()

    orig_w, orig_h = image.size
    input_tensor = _transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        mask = model(input_tensor)

    mask = mask.squeeze(0).squeeze(0).cpu().numpy()
    mask = (mask > threshold).astype(np.uint8)

    mask_pil = Image.fromarray(mask * 255).resize((orig_w, orig_h), Image.NEAREST)
    mask_arr = np.array(mask_pil)

    regions = _find_connected_regions(mask_arr)
    return regions


def _find_connected_regions(mask: np.ndarray) -> list[dict]:
    regions = []
    visited = np.zeros_like(mask, dtype=bool)
    h, w = mask.shape

    for row in range(h):
        for col in range(w):
            if mask[row, col] > 0 and not visited[row, col]:
                min_r, max_r = row, row
                min_c, max_c = col, col
                stack = [(row, col)]
                visited[row, col] = True

                while stack:
                    r, c = stack.pop()
                    min_r = min(min_r, r)
                    max_r = max(max_r, r)
                    min_c = min(min_c, c)
                    max_c = max(max_c, c)

                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < h and 0 <= nc < w and mask[nr, nc] > 0 and not visited[nr, nc]:
                            visited[nr, nc] = True
                            stack.append((nr, nc))

                bbox_w = max_c - min_c + 1
                bbox_h = max_r - min_r + 1
                if bbox_w >= 10 and bbox_h >= 10:
                    padding = 5
                    regions.append({
                        "x": max(0, min_c - padding),
                        "y": max(0, min_r - padding),
                        "width": min(w, max_c - min_c + 1 + 2 * padding),
                        "height": min(h, max_r - min_r + 1 + 2 * padding),
                    })

    if not regions:
        regions.append({"x": 0, "y": 0, "width": w, "height": h})

    return regions
