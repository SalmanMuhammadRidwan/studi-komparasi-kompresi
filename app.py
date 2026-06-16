import streamlit as st
import os
from algoritma.kmeans_compress import kompresi_kmeans
from algoritma.svd_compress import kompresi_svd
from algoritma.rle_compress import kompresi_rle

st.set_page_config(page_title="Uji Kompresi Gambar", layout="wide")

st.title("Studi Komparasi Algoritma Kompresi Gambar")
st.write("Aplikasi pengujian kompresi menggunakan K-Means, SVD, dan RLE pada format .bmp")

# Bagian Input UI
uploaded_file = st.file_uploader("Pilih gambar format .bmp", type=['bmp'])
algoritma = st.selectbox("Pilih Metode Kompresi:", ["K-Means Quantization", "Singular Value Decomposition (SVD)", "Run-Length Encoding (RLE)"])

if uploaded_file is not None:
    # Simpan file yang diunggah ke penyimpanan sementara
    input_path = "temp_input.bmp"
    output_path = "temp_output.bmp"
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    if st.button("Mulai Kompresi"):
        with st.spinner('Memproses kompresi...'):
            try:
                # Panggil fungsi berdasarkan pilihan algoritma
                if algoritma == "K-Means Quantization":
                    hasil = kompresi_kmeans(input_path, output_path, n_colors=16)
                elif algoritma == "Singular Value Decomposition (SVD)":
                    hasil = kompresi_svd(input_path, output_path, k=50)
                elif algoritma == "Run-Length Encoding (RLE)":
                    hasil = kompresi_rle(input_path, output_path)
                
                # Tampilkan Hasil Visual side-by-side
                st.subheader("Hasil Kompresi")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.image(input_path, caption="Gambar Asli")
                    st.info(f"Ukuran: {hasil['ukuran_asli_kb']:.2f} KB")
                    
                with col2:
                    st.image(output_path, caption=f"Hasil: {algoritma}")
                    st.success(f"Ukuran: {hasil['ukuran_kompresi_kb']:.2f} KB")
                
                # Tampilkan Metrik Persentase
                st.metric(label="Pengurangan Ukuran File", value=f"{hasil['persentase_pengurangan']:.2f}%")
                
            except Exception as e:
                st.error(f"Terjadi kesalahan saat pemrosesan: {e}")