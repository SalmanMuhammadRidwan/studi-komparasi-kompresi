import streamlit as st
import os
import time
import pandas as pd
from PIL import Image

# Import Modul Algoritma
from algoritma.dwt_compress import kompresi_dwt
from algoritma.dct_compress import kompresi_dct
from algoritma.chroma_compress import kompresi_chroma

st.set_page_config(page_title="Uji Kompresi Citra", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# INISIALISASI SESSION STATE
# ==========================================
if 'riwayat' not in st.session_state:
    st.session_state.riwayat = []
if 'counter' not in st.session_state:
    st.session_state.counter = 0

# ==========================================
# HEADER & DESKRIPSI (Gaya Objektif & Profesional)
# ==========================================
st.title("📊 Platform Evaluasi Kompresi Citra Digital")
st.markdown("""
Sistem ini dirancang untuk melakukan studi komparasi terhadap efisiensi, performa, dan hasil visual dari tiga metode transformasi citra: **Discrete Wavelet Transform (DWT)**, **Discrete Cosine Transform (DCT)**, dan **Chroma Subsampling**.
""")

# ==========================================
# BAGIAN SIDEBAR (KONTROL PARAMETER)
# ==========================================
with st.sidebar:
    st.header("⚙️ Parameter Pengujian")
    
    sumber_file = st.radio("Sumber Citra Uji:", ["Unggah Mandiri", "Pilih dari Dataset"])
    file_gambar = None
    nama_file_asli = ""
    
    if sumber_file == "Unggah Mandiri":
        uploaded_file = st.file_uploader("Unggah berkas (.bmp, .jpg, .png)", type=['bmp', 'jpg', 'jpeg', 'png'])
        if uploaded_file is not None:
            file_gambar = Image.open(uploaded_file)
            nama_file_asli = uploaded_file.name
    else:
        folder_dataset = "dataset"
        if not os.path.exists(folder_dataset):
            os.makedirs(folder_dataset)
            
        daftar_file = [f for f in os.listdir(folder_dataset) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        
        if len(daftar_file) > 0:
            pilihan = st.selectbox("Pilih citra uji:", daftar_file)
            file_gambar = Image.open(os.path.join(folder_dataset, pilihan))
            nama_file_asli = pilihan
        else:
            st.warning("⚠️ Direktori 'dataset' kosong.")
            
    st.divider()
    
    algoritma_pilihan = st.multiselect(
        "Pilih Metode Evaluasi:", 
        ["DWT (Wavelet)", "DCT (Cosine)", "Chroma Subsampling"],
        default=["DWT (Wavelet)", "DCT (Cosine)", "Chroma Subsampling"]
    )
    
    tombol_proses = st.button("🚀 Eksekusi Komparasi", use_container_width=True, type="primary")
    
    if len(st.session_state.riwayat) > 0:
        if st.button("🗑️ Bersihkan Memori Sesi", use_container_width=True):
            st.session_state.riwayat = []
            st.session_state.counter = 0
            st.rerun()

# ==========================================
# PROSES EKSEKUSI & PENGUKURAN EMPIRIS
# ==========================================
if file_gambar is not None and tombol_proses:
    if len(algoritma_pilihan) == 0:
        st.error("Pilih minimal 1 metode transformasi.")
    else:
        st.session_state.counter += 1
        id_unik = st.session_state.counter
        input_path = f"temp_input_{id_unik}.bmp"
        
        # Simpan file statis
        file_gambar.convert('RGB').save(input_path, format="BMP")
        ukuran_asli = os.path.getsize(input_path)
        
        hasil_job = {
            "nama_file": nama_file_asli,
            "input_path": input_path,
            "ukuran_asli_kb": ukuran_asli / 1024,
            "hasil_kompresi": {}
        }
        
        progress_bar = st.progress(0)
        step = 100 / len(algoritma_pilihan)
        
        for i, algo in enumerate(algoritma_pilihan):
            output_path = f"temp_output_{id_unik}_{algo[:3]}.bmp"
            
            # PENGUKURAN WAKTU EKSEKUSI (Mulai)
            start_time = time.time()
            
            try:
                if algo == "DWT (Wavelet)":
                    metrik = kompresi_dwt(input_path, output_path)
                elif algo == "DCT (Cosine)":
                    metrik = kompresi_dct(input_path, output_path)
                elif algo == "Chroma Subsampling":
                    metrik = kompresi_chroma(input_path, output_path)
                
                # PENGUKURAN WAKTU EKSEKUSI (Selesai)
                end_time = time.time()
                waktu_eksekusi = end_time - start_time
                
                metrik["waktu_eksekusi_detik"] = waktu_eksekusi
                
                hasil_job["hasil_kompresi"][algo] = {
                    "path": output_path,
                    "metrik": metrik
                }
            except Exception as e:
                st.error(f"Kegagalan pada {algo}: {e}")
                
            progress_bar.progress(int((i + 1) * step))
            
        st.session_state.riwayat.insert(0, hasil_job)
        st.toast('Proses komparasi berhasil dieksekusi!', icon='✅')

# ==========================================
# TATA LETAK UI: TAB DINAMIS
# ==========================================
tab_visual, tab_grafik, tab_matriks = st.tabs([
    "🖼️ Visualisasi Output", 
    "📈 Analisis Grafik Data", 
    "🗂️ Matriks Komparasi"
])

# ==========================================
# TAB 1: VISUALISASI OUTPUT
# ==========================================
with tab_visual:
    if len(st.session_state.riwayat) == 0:
        st.info("Silakan inisiasi pengujian melalui panel konfigurasi.")
    else:
        for item in st.session_state.riwayat:
            with st.expander(f"Hasil Pengujian: {item['nama_file']} (Klik untuk melihat detail)", expanded=True):
                st.markdown(f"**Ukuran Baseline (.bmp):** `{item['ukuran_asli_kb']:.2f} KB`")
                
                jumlah_algoritma = len(item["hasil_kompresi"])
                kolom = st.columns(jumlah_algoritma + 1)
                
                with kolom[0]:
                    st.image(item['input_path'], caption="Citra Referensi (100%)")
                
                for i, (nama_algo, data) in enumerate(item["hasil_kompresi"].items()):
                    with kolom[i + 1]:
                        st.image(data['path'], caption=f"Hasil: {nama_algo}")
                        
                        # Menampilkan Metrik dengan styling warna dari Streamlit
                        st.metric(
                            label="Ukuran Data", 
                            value=f"{data['metrik']['ukuran_kompresi_kb']:.2f} KB", 
                            delta=f"-{data['metrik']['persentase_pengurangan']:.2f}%",
                            delta_color="inverse"
                        )
                        st.caption(f"⏱️ Waktu: {data['metrik']['waktu_eksekusi_detik']:.3f} dtk")

# ==========================================
# TAB 2: ANALISIS GRAFIK DATA (EMPIRIS)
# ==========================================
with tab_grafik:
    if len(st.session_state.riwayat) > 0:
        data_terbaru = st.session_state.riwayat[0]
        st.subheader(f"Performa Pengujian Terakhir: {data_terbaru['nama_file']}")
        
        # Ekstraksi Data untuk Grafik
        df_grafik = {
            "Algoritma": [],
            "Ukuran (KB)": [],
            "Waktu (Detik)": []
        }
        
        # Masukkan data Asli sebagai Baseline
        df_grafik["Algoritma"].append("Baseline (Asli)")
        df_grafik["Ukuran (KB)"].append(data_terbaru["ukuran_asli_kb"])
        df_grafik["Waktu (Detik)"].append(0.0) # Baseline tidak memiliki waktu eksekusi
        
        for algo, data in data_terbaru["hasil_kompresi"].items():
            df_grafik["Algoritma"].append(algo)
            df_grafik["Ukuran (KB)"].append(data["metrik"]["ukuran_kompresi_kb"])
            df_grafik["Waktu (Detik)"].append(data["metrik"]["waktu_eksekusi_detik"])
            
        df_visual = pd.DataFrame(df_grafik).set_index("Algoritma")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("**Perbandingan Ukuran Data (Lebih rendah lebih baik)**")
            st.bar_chart(df_visual[["Ukuran (KB)"]], color="#FF4B4B")
            
        with col_g2:
            st.markdown("**Performa Kecepatan Komputasi (Lebih rendah lebih baik)**")
            # Hilangkan baseline (Asli) dari grafik waktu karena bernilai 0
            df_waktu = df_visual.drop("Baseline (Asli)")
            st.bar_chart(df_waktu[["Waktu (Detik)"]], color="#0068C9")
    else:
        st.info("Grafik empiris akan muncul setelah eksekusi pengujian.")

# ==========================================
# TAB 3: MATRIKS KOMPARASI (TEORI + EMPIRIS)
# ==========================================
with tab_matriks:
    st.subheader("I. Matriks Komparasi Teoretis")
    st.write("Karakteristik fundamental dari masing-masing algoritma terhadap pemrosesan citra spasial dan frekuensi.")
    
    data_teori = {
        "Parameter Analisis": [
            "1. Cara Kerja Utama", 
            "2. Data yang Dibuang (Lossy)", 
            "3. Efek Samping pada Gambar", 
            "4. Beban Komputasi (Kecepatan)",
            "5. Contoh Implementasi Populer"
        ],
        "DWT (Wavelet)": [
            "Memisahkan gambar menjadi struktur utama dan detail gelombang (frekuensi).", 
            "Detail frekuensi tinggi (seperti tekstur mikro atau tepi tajam objek).", 
            "Gambar menjadi sedikit lebih halus atau agak kabur (Blur).", 
            "Menengah (Menganalisis gelombang pada seluruh kanvas gambar).",
            "Format kompresi canggih seperti JPEG 2000."
        ],
        "DCT (Cosine)": [
            "Membagi gambar menjadi kotak-kotak kecil (8x8 piksel) lalu menganalisis frekuensinya.", 
            "Detail berlebih di dalam setiap kotak 8x8 yang tidak terlalu disadari mata manusia.", 
            "Muncul kotak-kotak kecil mirip mosaik (Blocking Artifacts) jika kompresi terlalu tinggi.", 
            "Tinggi (Membutuhkan perhitungan matematis rumit berulang-ulang pada tiap kotak kecil).",
            "Format standar JPEG yang digunakan sehari-hari."
        ],
        "Chroma Subsampling": [
            "Memisahkan elemen cahaya (terang/gelap) dari elemen warna gambar.", 
            "Setengah dari informasi warna asli (namun informasi cahaya dipertahankan 100%).", 
            "Sangat jernih. Mata manusia lebih sensitif pada cahaya dibanding warna, sehingga efek kompresinya nyaris tidak terlihat.", 
            "Sangat Rendah / Paling Cepat (Hanya memotong dan melewati piksel warna secara langsung).",
            "Transmisi sinyal TV Digital, Video YouTube, dan format WebP."
        ]
    }
    df_teori = pd.DataFrame(data_teori).set_index("Parameter Analisis")
    st.table(df_teori)
    
    st.divider()
    
    st.subheader("II. Matriks Hasil Empiris (Real-Time)")
    st.write("Tabel di bawah ini dihasilkan secara dinamis berdasarkan kalkulasi pengujian citra yang terakhir kali dieksekusi.")
    
    if len(st.session_state.riwayat) > 0:
        data_terbaru = st.session_state.riwayat[0]
        
        data_empiris = {
            "Algoritma Evaluasi": [],
            "Ukuran Asli (KB)": [],
            "Ukuran Reduksi (KB)": [],
            "Persentase Efisiensi": [],
            "Waktu Komputasi (Detik)": []
        }
        
        for algo, data in data_terbaru["hasil_kompresi"].items():
            data_empiris["Algoritma Evaluasi"].append(algo)
            data_empiris["Ukuran Asli (KB)"].append(f"{data_terbaru['ukuran_asli_kb']:.2f}")
            data_empiris["Ukuran Reduksi (KB)"].append(f"{data['metrik']['ukuran_kompresi_kb']:.2f}")
            data_empiris["Persentase Efisiensi"].append(f"{data['metrik']['persentase_pengurangan']:.2f}%")
            data_empiris["Waktu Komputasi (Detik)"].append(f"{data['metrik']['waktu_eksekusi_detik']:.4f}")
            
        df_empiris = pd.DataFrame(data_empiris).set_index("Algoritma Evaluasi")
        st.dataframe(df_empiris, use_container_width=True)
    else:
        st.info("Data empiris kosong. Harap jalankan pengujian untuk menampilkan matriks komparasi numerik.")