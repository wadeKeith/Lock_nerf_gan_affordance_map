import argparse
import math
import glob
from matplotlib import pyplot as plt
import numpy as np
import sys
import os

import torch
from torchvision.utils import save_image
from tqdm import tqdm

import curriculums as curriculums

import pandas as pd

from torch_ema import ExponentialMovingAverage
import datasets as datasets

import torchvision.transforms as transforms
import PIL
import skvideo.io
from PIL import Image

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def show(tensor_img):
    if len(tensor_img.shape) > 3:
        tensor_img = tensor_img.squeeze(0)
    tensor_img = tensor_img.permute(1, 2, 0).squeeze().cpu().numpy()
    plt.imshow(tensor_img)
    plt.show()

def generate_img(gen, z, **kwargs):

    with torch.no_grad():
        img = generator.staged_forward(z, None, None, max_batch_size=opt.max_batch_size, **kwargs)[0].to(device)
        tensor_img = img.detach()

        img_min = img.min()
        img_max = img.max()
        img = (img - img_min)/(img_max-img_min)
        img = img.permute(0, 2, 3, 1).squeeze().cpu().numpy()
    return img, tensor_img

def generate_img_recon(gen, z, pos_z, **kwargs):

    with torch.no_grad():
        img = generator.staged_forward(z, pos_z[:, 0], pos_z[:, 1], mode='recon', **kwargs)[0].to(device)
        tensor_img = img.detach()

        img_min = img.min()
        img_max = img.max()
        img = (img - img_min)/(img_max-img_min)
        img = img.permute(0, 2, 3, 1).squeeze().cpu().numpy()
    return img, tensor_img

def tensor_to_PIL(img):
    img = img.squeeze() * 0.5 + 0.5
    return Image.fromarray(img.mul(255).add_(0.5).clamp_(0, 255).permute(1, 2, 0).to('cpu', torch.uint8).numpy())

inv_normalize = transforms.Normalize(
   mean=[-0.5/0.5],
   std=[1/0.5]
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, default='')
    parser.add_argument('--output_dir', type=str, default='')
    parser.add_argument('--max_batch_size', type=int, default=2400000)
    parser.add_argument('--lock_view_dependence', action='store_true')
    parser.add_argument('--image_size', type=int, default=64)
    parser.add_argument('--ray_steps', type=int, default=96)
    parser.add_argument('--curriculum', type=str, default='celeba')
    parser.add_argument('--img_1', type=str, default='')
    parser.add_argument('--img_2', type=str, default='')
    opt = parser.parse_args()

    curriculum = getattr(curriculums, opt.curriculum)
    curriculum['num_steps'] = opt.ray_steps
    curriculum['img_size'] = opt.image_size
    curriculum['v_stddev'] = 0
    curriculum['h_stddev'] = 0
    curriculum['lock_view_dependence'] = opt.lock_view_dependence
    curriculum['last_back'] = True
    curriculum['nerf_noise'] = 0
    curriculum = {key: value for key, value in curriculum.items() if type(key) is str}

    os.makedirs(opt.output_dir, exist_ok=True)

    checkpoint = torch.load(opt.path, map_location=torch.device(device))
    generator = checkpoint['generator.pth'].to(device)
    encoder = checkpoint['encoder.pth'].to(device)
    ema = ExponentialMovingAverage(generator.parameters(), decay=0.999)
    ema_encoder = ExponentialMovingAverage(encoder.parameters(), decay=0.999)
    ema.load_state_dict(checkpoint['ema.pth'])
    ema_encoder.load_state_dict(checkpoint['ema_encoder.pth'])
    ema.copy_to(generator.parameters())
    ema_encoder.copy_to(encoder.parameters())
    generator.set_device(device)
    generator.eval()
    encoder.eval()

    list_objects = []
    transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5]),
            transforms.Resize((64, 64), interpolation=0)
        ])
    img1 = PIL.Image.open(opt.img_1)
    img1 = transform(img1)[:3]
    img2 = PIL.Image.open(opt.img_2)
    img2 = transform(img2)[:3]
    z1, pos1 = encoder(img1.unsqueeze(0).to(device), alpha=1.0)
    z2, pos2 = encoder(img2.unsqueeze(0).to(device), alpha=1.0)
    recon_images = []
    recon_PIL = []
    output_name = f'interp.mp4'
    writer = skvideo.io.FFmpegWriter(os.path.join(opt.output_dir, output_name), outputdict={'-pix_fmt': 'yuv420p', '-crf': '21'})
    for weight in tqdm(range(101)):
        images = []
        z = torch.lerp(z1, z2, weight/101.0)
        pos = torch.lerp(pos1, pos2, weight/101.0)
        img_recon, tensor_img_recon = generate_img_recon(generator, z, pos, **curriculum)
        recon_images.append(tensor_img_recon)
        recon_PIL.append(tensor_to_PIL(tensor_img_recon))
    recon_images = torch.cat(recon_images)
    save_image(tensor_to_PIL(recon_images), os.path.join(opt.output_dir, f'grid_{weight}_recon.png'), nrow=11, normalize=False)
    for frame in recon_PIL:
        writer.writeFrame(np.array(frame))