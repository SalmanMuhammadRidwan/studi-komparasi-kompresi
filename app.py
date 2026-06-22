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
if 'riwayat_batch' not in st.session_state:
    st.session_state.riwayat_batch = []
if 'counter' not in st.session_state:
    st.session_state.counter = 0

# ==========================================
# HEADER & DESKRIPSI
# ==========================================
st.title("📊 Platform Evaluasi Kompresi Citra Digital")
st.markdown("""
Sistem komparasi multi-citra untuk mengevaluasi efisiensi reduksi data, performa waktu, dan hasil visual dari metode **DWT**, **DCT**, dan **Chroma Subsampling**.
""")

# ==========================================
# BAGIAN SIDEBAR (KONTROL PARAMETER)
# ==========================================
with st.sidebar:
    st.header("⚙️ Parameter Pengujian")
    
    sumber_file = st.radio("Sumber Citra Uji:", ["Unggah Mandiri", "Pilih dari Dataset"])
    daftar_file_proses = []
    
    if sumber_file == "Unggah Mandiri":
        uploaded_files = st.file_uploader("Unggah maksimal 10 berkas", type=['bmp', 'jpg', 'jpeg', 'png'], accept_multiple_files=True)
        if uploaded_files:
            if len(uploaded_files) > 10:
                st.warning("⚠️ Batas maksimal 10 berkas. Hanya 10 berkas pertama yang diproses.")
                uploaded_files = uploaded_files[:10]
            for uf in uploaded_files:
                daftar_file_proses.append({"nama": uf.name, "objek": Image.open(uf)})
                
    else:
        folder_dataset = "dataset"
        if not os.path.exists(folder_dataset):
            os.makedirs(folder_dataset)
        daftar_dataset = [f for f in os.listdir(folder_dataset) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        
        if len(daftar_dataset) > 0:
            pilihan_dataset = st.multiselect("Pilih maksimal 10 citra uji:", daftar_dataset)
            if pilihan_dataset:
                if len(pilihan_dataset) > 10:
                    st.warning("⚠️ Batas maksimal 10 berkas. Hanya 10 berkas pertama yang diproses.")
                    pilihan_dataset = pilihan_dataset[:10]
                for pd_file in pilihan_dataset:
                    daftar_file_proses.append({"nama": pd_file, "objek": Image.open(os.path.join(folder_dataset, pd_file))})
        else:
            st.warning("⚠️ Direktori 'dataset' kosong.")
            
    st.divider()
    
    algoritma_pilihan = st.multiselect(
        "Pilih Metode Evaluasi:", 
        ["DWT (Wavelet)", "DCT (Cosine)", "Chroma Subsampling"],
        default=["DWT (Wavelet)", "DCT (Cosine)", "Chroma Subsampling"]
    )
    
    tombol_proses = st.button("🚀 Eksekusi Batch Komparasi", width="stretch", type="primary")

# ==========================================
# PROSES EKSEKUSI BATCH MULTI-CITRA
# ==========================================
if tombol_proses:
    if len(daftar_file_proses) == 0:
        st.error("Pilih minimal 1 citra untuk diproses.")
    elif len(algoritma_pilihan) == 0:
        st.error("Pilih minimal 1 metode transformasi.")
    else:
        st.session_state.counter += 1
        batch_id = st.session_state.counter
        
        batch_result = {
            "batch_id": batch_id,
            "waktu_eksekusi": time.strftime("%Y-%m-%d %H:%M:%S"),
            "data_citra": []
        }
        
        total_proses = len(daftar_file_proses) * len(algoritma_pilihan)
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        step_current = 0
        
        for citra in daftar_file_proses:
            # 1. Pisahkan nama file dari ekstensinya (misal: "1.bmp" menjadi "1")
            nama_tanpa_ekstensi = os.path.splitext(citra['nama'])[0]
            
            # 2. Gunakan nama_tanpa_ekstensi pada string path
            input_path = f"temp_input_b{batch_id}_{nama_tanpa_ekstensi}.bmp"
            
            img_baseline = citra['objek'].convert('RGB')
            img_baseline.thumbnail((800, 800)) 
            img_baseline.save(input_path, format="BMP")
            
            ukuran_asli = os.path.getsize(input_path)
            
            hasil_per_citra = {
                "nama_file": citra['nama'],
                "input_path": input_path,
                "ukuran_asli_kb": ukuran_asli / 1024,
                "kompresi": {}
            }
            
            for algo in algoritma_pilihan:
                status_text.text(f"Memproses {citra['nama']} dengan {algo}...")
                output_path = f"temp_output_b{batch_id}_{algo[:3]}_{nama_tanpa_ekstensi}.bmp"
                start_time = time.time()
                
                try:
                    if algo == "DWT (Wavelet)":
                        metrik = kompresi_dwt(input_path, output_path)
                    elif algo == "DCT (Cosine)":
                        metrik = kompresi_dct(input_path, output_path)
                    elif algo == "Chroma Subsampling":
                        metrik = kompresi_chroma(input_path, output_path)
                        
                    metrik["waktu_eksekusi_detik"] = time.time() - start_time
                    hasil_per_citra["kompresi"][algo] = {"path": output_path, "metrik": metrik}
                except Exception as e:
                    st.error(f"Kegagalan pada {algo} ({citra['nama']}): {e}")
                
                step_current += 1
                progress_bar.progress(step_current / total_proses)
                
            batch_result["data_citra"].append(hasil_per_citra)
            
        status_text.empty()
        st.session_state.riwayat_batch.insert(0, batch_result)
        st.toast(f'Batch #{batch_id} selesai dieksekusi!', icon='✅')

    if len(st.session_state.riwayat_batch) > 0:
        st.sidebar.divider()
    
        if st.sidebar.button("🗑️ Hapus Riwayat & File Lokal", type="primary"):
            file_sampah = [f for f in os.listdir('.') if f.startswith('temp_input_') or f.startswith('temp_output_')]
        
            for f in file_sampah:
                try:
                    if os.path.exists(f):
                        os.remove(f)
                except Exception as e:
                    pass 
        
            st.session_state.riwayat_batch = []
            st.session_state.counter = 0
            st.rerun()

# ==========================================
# TATA LETAK UI: TAB DINAMIS
# ==========================================
tab_visual, tab_grafik, tab_matriks = st.tabs([
    "🖼️ Visualisasi Komparasi Citra", 
    "📈 Analisis Grafik Antar-Citra", 
    "🗂️ Matriks & Data Agregat"
])

# ==========================================
# TAB 1: VISUALISASI KOMPARASI CITRA
# ==========================================
with tab_visual:
    if len(st.session_state.riwayat_batch) == 0:
        st.info("Silakan unggah citra dan jalankan pengujian melalui panel di sebelah kiri.")
    else:
        batch_terbaru = st.session_state.riwayat_batch[0]
        st.success(f"Menampilkan visualisasi dari Eksekusi Batch #{batch_terbaru['batch_id']} ({len(batch_terbaru['data_citra'])} Citra)")
        
        for item in batch_terbaru['data_citra']:
            with st.expander(f"📄 Citra: {item['nama_file']} | Baseline: {item['ukuran_asli_kb']:.2f} KB", expanded=False):
                jumlah_algoritma = len(item["kompresi"])
                kolom = st.columns(jumlah_algoritma + 1)
                
                with kolom[0]:
                    st.image(item['input_path'], caption="Citra Referensi (100%)")
                
                for i, (nama_algo, data) in enumerate(item["kompresi"].items()):
                    with kolom[i + 1]:
                        st.image(data['path'], caption=f"Hasil: {nama_algo}")
                        st.metric(
                            label=f"Reduksi {nama_algo[:3]}", 
                            value=f"{data['metrik']['ukuran_kompresi_kb']:.2f} KB", 
                            delta=f"-{data['metrik']['persentase_pengurangan']:.2f}%",
                            delta_color="inverse"
                        )

# ==========================================
# TAB 2: ANALISIS GRAFIK DATA ANTAR-CITRA
# ==========================================
with tab_grafik:
    if len(st.session_state.riwayat_batch) > 0:
        batch_terbaru = st.session_state.riwayat_batch[0]
        st.header("Analisis Performa Berdasarkan Karakteristik Citra")
        st.write("Grafik di bawah ini membandingkan bagaimana algoritma merespons berbagai citra yang berbeda secara bersamaan.")
        
        data_efisiensi = {"Nama File": []}
        data_waktu = {"Nama File": []}
        
        algoritma_terdeteksi = list(batch_terbaru['data_citra'][0]['kompresi'].keys())
        for algo in algoritma_terdeteksi:
            data_efisiensi[algo] = []
            data_waktu[algo] = []
            
        for citra in batch_terbaru['data_citra']:
            data_efisiensi["Nama File"].append(citra['nama_file'])
            data_waktu["Nama File"].append(citra['nama_file'])
            
            for algo in algoritma_terdeteksi:
                if algo in citra["kompresi"]:
                    data_efisiensi[algo].append(citra["kompresi"][algo]["metrik"]["persentase_pengurangan"])
                    data_waktu[algo].append(citra["kompresi"][algo]["metrik"]["waktu_eksekusi_detik"])
                else:
                    data_efisiensi[algo].append(0)
                    data_waktu[algo].append(0)

        df_efisiensi = pd.DataFrame(data_efisiensi).set_index("Nama File")
        df_waktu = pd.DataFrame(data_waktu).set_index("Nama File")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.subheader("1. Efisiensi Reduksi Ruang (%)")
            st.write("Semakin tinggi grafik, semakin banyak memori yang dihemat.")
            st.bar_chart(df_efisiensi)
            
        with col_g2:
            st.subheader("2. Waktu Komputasi (Detik)")
            st.write("Semakin rendah grafik, semakin cepat algoritma bekerja.")
            st.bar_chart(df_waktu)
    else:
        st.info("Visualisasi antar-citra akan muncul setelah eksekusi batch selesai.")

# ==========================================
# TAB 3: MATRIKS KOMPARASI & DATA AGREGAT
# ==========================================
with tab_matriks:
    st.subheader("I. Matriks Komparasi Teoretis")
    
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
            "Format kompresi resolusi tinggi seperti JPEG 2000."
        ],
        "DCT (Cosine)": [
            "Membagi gambar menjadi kotak-kotak kecil (8x8) lalu menganalisis frekuensinya.", 
            "Detail berlebih di dalam setiap kotak 8x8 yang kurang disadari mata manusia.", 
            "Muncul kotak-kotak kecil mirip mosaik (Blocking Artifacts) di kompresi ekstrem.", 
            "Tinggi (Membutuhkan perhitungan matematis berulang pada setiap blok matriks).",
            "Format gambar standar industri harian (JPEG/JPG)."
        ],
        "Chroma Subsampling": [
            "Memisahkan elemen cahaya (terang/gelap) dari elemen warna citra digital.", 
            "50% dari informasi warna asli (informasi intensitas cahaya utuh 100%).", 
            "Sangat jernih. Mata manusia lemah terhadap detail warna, degradasi tidak kasat mata.", 
            "Sangat Cepat (Hanya melompati piksel matriks secara linear).",
            "Sistem transmisi TV Digital, Video Streaming (MPEG), dan WebP."
        ]
    }
    df_teori = pd.DataFrame(data_teori).set_index("Parameter Analisis")
    st.table(df_teori)
    
    st.divider()
    
    if len(st.session_state.riwayat_batch) > 0:
        batch_terbaru = st.session_state.riwayat_batch[0]
        st.subheader(f"II. Matriks Hasil Empiris: Batch #{batch_terbaru['batch_id']}")
        st.write("Tabel di bawah ini merupakan rincian data mentah dari seluruh citra yang diuji pada sesi eksekusi terakhir.")
        
        data_tabel_master = []
        for citra in batch_terbaru['data_citra']:
            for algo, data in citra["kompresi"].items():
                data_tabel_master.append({
                    "Nama File Citra": citra['nama_file'],
                    "Algoritma": algo,
                    "Ukuran Asli (KB)": round(citra['ukuran_asli_kb'], 2),
                    "Ukuran Reduksi (KB)": round(data['metrik']['ukuran_kompresi_kb'], 2),
                    "Persentase Hemat (%)": round(data['metrik']['persentase_pengurangan'], 2),
                    "Waktu (Detik)": round(data['metrik']['waktu_eksekusi_detik'], 4)
                })
                
        df_master = pd.DataFrame(data_tabel_master)
        st.dataframe(df_master, width="stretch")
    else:
        st.info("Data empiris kosong. Harap jalankan pengujian untuk menampilkan matriks rekapitulasi data.")