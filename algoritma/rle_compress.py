import os
import itertools
import numpy as np
from PIL import Image

def kompresi_rle(input_path, output_path):
    img = Image.open(input_path).convert('RGB')
    img_array = np.array(img)
    ukuran_asli = os.path.getsize(input_path)
    
    flat_pixels = img_array.reshape(-1, 3)
    pixels_tuple = [tuple(p) for p in flat_pixels]
    
    compressed_size_bytes = 0
    
    for color, group in itertools.groupby(pixels_tuple):
        count = sum(1 for _ in group)
        
        # Logika RLE yang akurat: 
        # RLE menyimpan kelompok dalam blok maksimum 255 piksel.
        # Setiap blok butuh 4 Byte: [Jumlah (1 byte)] + [R (1 byte)] + [G (1 byte)] + [B (1 byte)]
        # Jika ada 300 piksel berderet, akan dibagi menjadi blok 255 dan blok 45.
        jumlah_blok = (count // 255) + 1 if count % 255 != 0 else (count // 255)
        compressed_size_bytes += (jumlah_blok * 4) 
        
    img.save(output_path)
    
    ukuran_kompresi = compressed_size_bytes
    persentase = ((ukuran_asli - ukuran_kompresi) / ukuran_asli) * 100
    
    return {
        "ukuran_asli_kb": ukuran_asli / 1024,
        "ukuran_kompresi_kb": ukuran_kompresi / 1024,
        "persentase_pengurangan": persentase
    }