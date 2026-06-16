import os
import numpy as np
from PIL import Image

def kompresi_svd(input_path, output_path, k=50):
    img = Image.open(input_path).convert('RGB')
    img_array = np.array(img, dtype=float)
    ukuran_asli = os.path.getsize(input_path)
    
    h, w, d = img_array.shape
    compressed_channels = []
    
    for i in range(3):
        channel = img_array[:, :, i]
        U, S, V = np.linalg.svd(channel, full_matrices=False)
        
        U_k = U[:, :k]
        S_k = np.diag(S[:k])
        V_k = V[:k, :]
        
        reconstructed = np.dot(U_k, np.dot(S_k, V_k))
        compressed_channels.append(reconstructed)
    
    compressed_array = np.stack(compressed_channels, axis=2)
    compressed_array = np.clip(compressed_array, 0, 255).astype('uint8')
    
    # Simpan hanya untuk keperluan tampilan di UI Streamlit
    compressed_img = Image.fromarray(compressed_array)
    compressed_img.save(output_path)
    
    # PERHITUNGAN UKURAN TEORETIS SVD
    # Elemen yang disimpan per channel: k*h (Matriks U) + k (Matriks S) + k*w (Matriks V)
    # Asumsi menggunakan tipe data Float32 (4 Byte per elemen angka)
    elemen_per_channel = (k * h) + k + (k * w)
    total_elemen = elemen_per_channel * 3  # Karena ada 3 channel (R, G, B)
    ukuran_kompresi_bytes = total_elemen * 4 
    
    persentase = ((ukuran_asli - ukuran_kompresi_bytes) / ukuran_asli) * 100
    
    return {
        "ukuran_asli_kb": ukuran_asli / 1024,
        "ukuran_kompresi_kb": ukuran_kompresi_bytes / 1024,
        "persentase_pengurangan": persentase
    }