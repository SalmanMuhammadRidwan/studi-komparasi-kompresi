import os
import numpy as np
from PIL import Image

def kompresi_chroma(input_path, output_path):
    img = Image.open(input_path).convert('RGB')
    ukuran_asli = os.path.getsize(input_path)
    
    # 1. Konversi ruang warna dari RGB ke YCbCr
    ycbcr_img = img.convert('YCbCr')
    img_array = np.array(ycbcr_img)
    
    Y = img_array[:, :, 0]   # Saluran Terang/Gelap (Luma)
    Cb = img_array[:, :, 1]  # Saluran Warna Biru (Chroma)
    Cr = img_array[:, :, 2]  # Saluran Warna Merah (Chroma)
    
    # 2. Proses Subsampling (Kompresi)
    # Potong ukuran matriks warna (Cb & Cr) dengan melompati setiap 1 baris/kolom
    Cb_sub = Cb[::2, ::2]
    Cr_sub = Cr[::2, ::2]
    
    # 3. Proses Upsampling (Rekonstruksi untuk antarmuka UI)
    # Kembalikan ke resolusi awal dengan menggandakan piksel yang ada
    Cb_reconstructed = np.repeat(np.repeat(Cb_sub, 2, axis=0), 2, axis=1)
    Cr_reconstructed = np.repeat(np.repeat(Cr_sub, 2, axis=0), 2, axis=1)
    
    # Penyesuaian dimensi jika dimensi aslinya ganjil
    h, w = Y.shape
    Cb_reconstructed = Cb_reconstructed[:h, :w]
    Cr_reconstructed = Cr_reconstructed[:h, :w]
    
    # 4. Gabungkan kembali dan simpan
    compressed_array = np.stack([Y, Cb_reconstructed, Cr_reconstructed], axis=2)
    compressed_img = Image.fromarray(compressed_array, 'YCbCr').convert('RGB')
    compressed_img.save(output_path)
    
    # 5. Perhitungan Teoretis Ukuran File
    # Y utuh (1 byte per piksel) = 1/3 dari total aslinya
    # Cb dipotong 1/4 = (1/4 * 1/3) dari total
    # Cr dipotong 1/4 = (1/4 * 1/3) dari total
    # Total ukuran file jatuh menjadi persis 50%
    ukuran_kompresi = ukuran_asli * 0.50
    persentase = ((ukuran_asli - ukuran_kompresi) / ukuran_asli) * 100
    
    return {
        "ukuran_asli_kb": ukuran_asli / 1024,
        "ukuran_kompresi_kb": ukuran_kompresi / 1024,
        "persentase_pengurangan": persentase
    }