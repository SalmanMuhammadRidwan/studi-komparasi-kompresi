# Studi Komparasi Algoritma Kompresi Citra Digital

Repositori ini memuat implementasi dan analisis komparasi tiga algoritma kompresi citra yang berbasis transformasi matematis dan persepsi visual, yaitu **Discrete Wavelet Transform (DWT)**, **Discrete Cosine Transform (DCT)**, dan **Chroma Subsampling**.

Studi ini secara khusus menggunakan format berkas citra mentah (Bitmap/`.bmp`) untuk mengevaluasi efisiensi reduksi data, kecepatan komputasi, dan dampaknya terhadap kualitas visual citra. Pengujian dilakukan menggunakan bahasa pemrograman Python dengan antarmuka berbasis web interaktif.

## Deskripsi dan Logika Implementasi Algoritma

Pengujian kompresi pada format `.bmp` menghadirkan tantangan teknis karena sifat formatnya yang selalu mengalokasikan memori statis secara penuh. Oleh karena itu, komparasi pada sistem ini berfokus pada evaluasi efisiensi teoretis dari manipulasi matriks tiap algoritma:

1. **Discrete Wavelet Transform / DWT (Kategori: Lossy)**
   - **Konsep:** Memisahkan citra menjadi komponen frekuensi tinggi (detail dan tepi) dan frekuensi rendah (struktur dasar citra) menggunakan dekomposisi gelombang (_wavelet_).
   - **Implementasi:** Menggunakan metode transformasi Haar. Proses kompresi dilakukan dengan mengeliminasi (mengubah menjadi nol) matriks kuadran frekuensi tinggi, dan hanya merekonstruksi citra dari matriks frekuensi rendah (LL). Pengukuran ukuran penyimpanan disimulasikan pada rasio data 25% dari ukuran asli.

2. **Discrete Cosine Transform / DCT (Kategori: Lossy)**
   - **Konsep:** Membagi matriks citra menjadi blok-blok berukuran 8x8 piksel dan mentransformasikannya dari domain spasial ke domain frekuensi. Algoritma ini merupakan pondasi utama dari format JPEG standar.
   - **Implementasi:** Melakukan pemotongan nilai matriks pada setiap blok dengan hanya mempertahankan koefisien frekuensi rendah di sudut kiri atas matriks. Pengukuran ukuran data dihitung berdasarkan persentase matriks blok yang dipertahankan.

3. **Chroma Subsampling (Kategori: Lossy Perseptual)**
   - **Konsep:** Memanfaatkan keterbatasan persepsi visual mata manusia yang lebih peka terhadap intensitas cahaya dibandingkan dengan detail warna.
   - **Implementasi:** Mengonversi citra dari ruang warna RGB ke YCbCr. Resolusi pada saluran terang/gelap (Luma/Y) dipertahankan utuh 100%, sementara resolusi pada kedua saluran warna (Chroma/Cb & Cr) dipotong hingga 50%. Kalkulasi ukuran menunjukkan efisiensi reduksi ruang penyimpanan yang tetap stabil pada angka 50% dengan degradasi visual yang nyaris tidak kasat mata.

## Struktur Direktori

Arsitektur sistem dibangun secara modular dengan memisahkan logika komputasi matriks dari logika antarmuka pengguna dasbor analitik.

```text
studi-komparasi-kompresi/
│
├── algoritma/                 # Modul pemrosesan logika kompresi
│   ├── __init__.py
│   ├── dwt_compress.py        # Logika dekomposisi gelombang wavelet (DWT)
│   ├── dct_compress.py        # Logika transformasi frekuensi blok (DCT)
│   └── chroma_compress.py     # Logika subsampling ruang warna YCbCr
│
├── dataset/                   # Folder penempatan sampel citra .bmp
├── app.py                     # Antarmuka web pengujian dan matriks empiris
├── requirements.txt           # Daftar pustaka yang dibutuhkan
└── README.md                  # Dokumentasi proyek
```

## Persyaratan Sistem dan Instalasi

Sistem ini membutuhkan instalasi pustaka standar komputasi saintifik dan antarmuka web.

### Dependensi Utama (berdasarkan `requirements.txt`)

- **streamlit** - Untuk pembangunan antarmuka web dan visualisasi data.
- **numpy** - Untuk komputasi manipulasi array dan matriks.
- **scipy** - Untuk pemrosesan algoritma Discrete Cosine Transform (DCT).
- **PyWavelets** - Untuk pemrosesan algoritma Discrete Wavelet Transform (DWT).
- **Pillow** - Untuk pembacaan, konversi ruang warna, dan penulisan berkas citra digital.

### Langkah Instalasi

1. Lakukan kloning pada repositori ini.
2. (Opsional) Buat dan aktifkan virtual environment.
3. Pasang seluruh dependensi dengan mengeksekusi perintah:

```bash
pip install -r requirements.txt
```

### Eksekusi Aplikasi

Aplikasi evaluasi kompresi dapat dijalankan di server lokal dengan mengeksekusi perintah berikut pada terminal:

```bash
streamlit run app.py
```

**Catatan**: Apabila perintah tidak dikenali oleh sistem, gunakan perintah alternatif:

```bash
python -m streamlit run app.py
```

Setelah dieksekusi, sistem secara otomatis akan membuka antarmuka pengujian pada peramban web standar di alamat http://localhost:8501. Pengguna dapat mengunggah sampel citra berformat .bmp dan meninjau visualisasi serta metrik kalkulasi ukurannya secara real-time.
