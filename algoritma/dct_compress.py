import os
import numpy as np
from scipy.fftpack import dct, idct
from PIL import Image

def apply_dct2(a):
    return dct(dct(a.T, norm='ortho').T, norm='ortho')

def apply_idct2(a):
    return idct(idct(a.T, norm='ortho').T, norm='ortho')

def kompresi_dct(input_path, output_path, block_size=8, keep_ratio=0.25):
    img = Image.open(input_path).convert('RGB')
    img_array = np.array(img, dtype=float)
    ukuran_asli = os.path.getsize(input_path)
    
    h, w, d = img_array.shape
    h_new = (h // block_size) * block_size
    w_new = (w // block_size) * block_size
    img_array = img_array[:h_new, :w_new, :]
    
    compressed_array = np.zeros_like(img_array)
    k = int(block_size * np.sqrt(keep_ratio))
    
    for c in range(3):
        channel = img_array[:, :, c]
        for i in range(0, h_new, block_size):
            for j in range(0, w_new, block_size):
                block = channel[i:i+block_size, j:j+block_size]
                
                dct_block = apply_dct2(block)
                compressed_block = np.zeros_like(dct_block)
                compressed_block[:k, :k] = dct_block[:k, :k]
                idct_block = apply_idct2(compressed_block)
                compressed_array[i:i+block_size, j:j+block_size, c] = idct_block
                
    compressed_array = np.clip(compressed_array, 0, 255).astype('uint8')
    Image.fromarray(compressed_array).save(output_path)
    
    ukuran_kompresi = ukuran_asli * keep_ratio
    persentase = ((ukuran_asli - ukuran_kompresi) / ukuran_asli) * 100
    
    return {
        "ukuran_asli_kb": ukuran_asli / 1024,
        "ukuran_kompresi_kb": ukuran_kompresi / 1024,
        "persentase_pengurangan": persentase
    }