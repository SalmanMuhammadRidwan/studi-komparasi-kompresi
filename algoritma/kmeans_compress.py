import os
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image

def kompresi_kmeans(input_path, output_path, n_colors=16):
    """
    Mengompresi gambar dengan mengurangi palet warna menggunakan K-Means.
    """
    # 1. Buka gambar dan hitung ukuran asli
    img = Image.open(input_path).convert('RGB')
    img_array = np.array(img)
    ukuran_asli = os.path.getsize(input_path)
    
    # 2. Reshape gambar 3D menjadi 2D (daftar piksel)
    h, w, d = img_array.shape
    pixels = img_array.reshape(-1, d)
    
    # 3. Terapkan K-Means
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # 4. Ganti piksel asli dengan warna dari cluster (centroid)
    compressed_pixels = kmeans.cluster_centers_[kmeans.labels_]
    compressed_array = compressed_pixels.reshape(h, w, d).astype('uint8')
    
    # 5. Simpan gambar hasil
    compressed_img = Image.fromarray(compressed_array)
    compressed_img.save(output_path)
    
    # 6. Hitung metrik
    ukuran_kompresi = os.path.getsize(output_path)
    persentase = ((ukuran_asli - ukuran_kompresi) / ukuran_asli) * 100
    
    return {
        "ukuran_asli_kb": ukuran_asli / 1024,
        "ukuran_kompresi_kb": ukuran_kompresi / 1024,
        "persentase_pengurangan": persentase
    }