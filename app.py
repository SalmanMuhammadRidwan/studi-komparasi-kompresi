import streamlit as st
import os
from PIL import Image
from algoritma.kmeans_compress import kompresi_kmeans
from algoritma.svd_compress import kompresi_svd
from algoritma.rle_compress import kompresi_rle

st.set_page_config(page_title="Uji Kompresi Gambar", layout="wide")

# ==========================================
# INISIALISASI SESSION STATE (MEMORY)
# ==========================================
# Ini berfungsi agar hasil kompresi sebelumnya tidak hilang
if 'riwayat' not in st.session_state:
    st.session_state.riwayat = []
if 'counter' not in st.session_state:
    st.session_state.counter = 0

st.title("Studi Komparasi Algoritma Kompresi Gambar")
st.write("Evaluasi efisiensi kompresi menggunakan K-Means, SVD, dan RLE pada format .bmp")

# ==========================================
# BAGIAN SIDEBAR (UI/UX KONTROL)
# ==========================================
with st.sidebar:
    st.header("⚙️ Pengaturan Kompresi")
    
    sumber_file = st.radio("Pilih Sumber Gambar:", ["Unggah Sendiri", "Pilih dari Dataset Uji"])
    
    file_gambar = None
    nama_file_asli = ""
    
    if sumber_file == "Unggah Sendiri":
        uploaded_file = st.file_uploader("Pilih gambar (JPG/PNG/BMP)", type=['bmp', 'jpg', 'jpeg', 'png'])
        if uploaded_file is not None:
            file_gambar = Image.open(uploaded_file)
            nama_file_asli = uploaded_file.name
    else:
        # Logika untuk membaca otomatis folder 'dataset'
        folder_dataset = "dataset"
        
        # Buat folder jika belum ada agar program tidak error
        if not os.path.exists(folder_dataset):
            os.makedirs(folder_dataset)
            
        # Cari semua file gambar di dalam folder dataset
        daftar_file = [f for f in os.listdir(folder_dataset) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        
        if len(daftar_file) > 0:
            pilihan = st.selectbox("Pilih gambar uji:", daftar_file)
            file_gambar = Image.open(os.path.join(folder_dataset, pilihan))
            nama_file_asli = pilihan
        else:
            st.warning("⚠️ Folder 'dataset' masih kosong. Silakan buat folder bernama 'dataset' di dalam folder proyekmu dan masukkan 10 gambar uji ke sana.")
            
    st.divider()
    algoritma = st.selectbox("Pilih Metode Kompresi:", [
        "K-Means Quantization", 
        "Singular Value Decomposition (SVD)", 
        "Run-Length Encoding (RLE)"
    ])
    
    tombol_proses = st.button("🚀 Mulai Kompresi", use_container_width=True, type="primary")
    
    # Tambahan UX: Tombol untuk mengosongkan riwayat layar
    if len(st.session_state.riwayat) > 0:
        if st.button("🗑️ Hapus Riwayat Layar", use_container_width=True):
            st.session_state.riwayat = []
            st.session_state.counter = 0
            st.rerun()

# ==========================================
# BAGIAN UTAMA (PROSES & VISUALISASI)
# ==========================================
if file_gambar is not None and tombol_proses:
    # Naikkan counter untuk membuat nama file sementara (temp) yang unik
    st.session_state.counter += 1
    id_unik = st.session_state.counter
    
    # File tidak akan saling tertimpa karena id_unik
    input_path = f"temp_input_{id_unik}.bmp"
    output_path = f"temp_output_{id_unik}.bmp"
    
    file_gambar.convert('RGB').save(input_path, format="BMP")
    
    with st.spinner(f'Memproses {nama_file_asli} dengan {algoritma}...'):
        try:
            if algoritma == "K-Means Quantization":
                hasil = kompresi_kmeans(input_path, output_path, n_colors=16)
            elif algoritma == "Singular Value Decomposition (SVD)":
                hasil = kompresi_svd(input_path, output_path, k=50)
            elif algoritma == "Run-Length Encoding (RLE)":
                hasil = kompresi_rle(input_path, output_path)
            
            # Simpan data metrik dan path gambar ke dalam Session State (di posisi index teratas agar terbaru muncul di atas)
            st.session_state.riwayat.insert(0, {
                "nama_file": nama_file_asli,
                "algoritma": algoritma,
                "input_path": input_path,
                "output_path": output_path,
                "metrik": hasil
            })
        except Exception as e:
            st.error(f"Terjadi kesalahan saat pemrosesan: {e}")

# ==========================================
# MENAMPILKAN RIWAYAT KOMPRESI (10 GAMBAR)
# ==========================================
if len(st.session_state.riwayat) == 0:
    st.info("👈 Silakan pilih/unggah gambar dan klik 'Mulai Kompresi' di panel sebelah kiri.")
else:
    st.success(f"Berhasil memproses {len(st.session_state.riwayat)} gambar sejauh ini. (Terbaru di paling atas)")
    
    # Looping untuk menampilkan semua gambar yang pernah dikompresi
    for item in st.session_state.riwayat:
        # Menggunakan st.container agar setiap riwayat memiliki batas kotak yang rapi
        with st.container(border=True):
            st.subheader(f"📄 {item['nama_file']}  |  {item['algoritma']}")
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Ukuran Asli (.bmp)", f"{item['metrik']['ukuran_asli_kb']:.2f} KB")
            col_m2.metric("Ukuran Kompresi", f"{item['metrik']['ukuran_kompresi_kb']:.2f} KB", f"-{item['metrik']['persentase_pengurangan']:.2f}%", delta_color="inverse")
            col_m3.metric("Persentase Pengurangan", f"{item['metrik']['persentase_pengurangan']:.2f}%")
            
            col1, col2 = st.columns(2)
            with col1:
                st.image(item['input_path'], caption=f"Gambar Asli ({item['nama_file']})")
            with col2:
                st.image(item['output_path'], caption=f"Hasil: {item['algoritma']}")