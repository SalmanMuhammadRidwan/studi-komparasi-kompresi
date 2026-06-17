import os
import numpy as np
import pywt
from PIL import Image

def kompresi_dwt(input_path, output_path):
    # 1. Buka gambar menjadi array
    img = Image.open(input_path).convert('RGB')
    img_array = np.array(img, dtype=float)
    ukuran_asli = os.path.getsize(input_path)
    
    h, w, d = img_array.shape
    compressed_channels = []
    
    # 2. Proses DWT untuk setiap channel warna (R, G, B)
    for i in range(3):
        # Terapkan Transformasi Wavelet 2 Dimensi (tipe Haar)
        coeffs2 = pywt.dwt2(img_array[:, :, i], 'haar')
        LL, (LH, HL, HH) = coeffs2
        
        # Kompresi: Nol-kan matriks frekuensi tinggi (detail dibuang)
        LH = np.zeros_like(LH)
        HL = np.zeros_like(HL)
        HH = np.zeros_like(HH)
        
        # Rekonstruksi gambar menggunakan matriks frekuensi rendah saja (LL)
        reconstructed = pywt.idwt2((LL, (LH, HL, HH)), 'haar')
        
        # Pastikan dimensi sesuai gambar asli (mengatasi isu piksel ganjil)
        reconstructed = reconstructed[:h, :w]
        compressed_channels.append(reconstructed)
        
    # 3. Gabungkan dan simpan gambar hasil untuk UI Streamlit
    compressed_array = np.stack(compressed_channels, axis=2)
    compressed_array = np.clip(compressed_array, 0, 255).astype('uint8')
    Image.fromarray(compressed_array).save(output_path)
    
    # 4. Perhitungan Teoretis Ukuran File
    # Dalam DWT, jika kita hanya menyimpan LL, data menjadi 1/4 (25%) dari aslinya
    ukuran_kompresi = ukuran_asli * 0.25
    persentase = ((ukuran_asli - ukuran_kompresi) / ukuran_asli) * 100
    
    return {
        "ukuran_asli_kb": ukuran_asli / 1024,
        "ukuran_kompresi_kb": ukuran_kompresi / 1024,
        "persentase_pengurangan": persentase
    }