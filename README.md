# Studi Komparasi Algoritma Kompresi Citra Digital

Repositori ini memuat implementasi dan analisis komparasi tiga algoritma kompresi citra yang berbeda karakteristiknya, yaitu **K-Means Quantization**, **Singular Value Decomposition (SVD)**, dan **Run-Length Encoding (RLE)**.

Studi ini secara khusus menggunakan format berkas citra mentah (Bitmap/`.bmp`) untuk mengevaluasi efisiensi kompresi, pengurangan ruang penyimpanan, dan dampaknya terhadap kualitas visual citra. Pengujian dilakukan menggunakan bahasa pemrograman Python dengan antarmuka berbasis web interaktif.

## Deskripsi dan Logika Implementasi Algoritma

Pengujian kompresi pada format `.bmp` menghadirkan tantangan teknis tersendiri karena sifat formatnya yang selalu mengalokasikan memori statis (umumnya 24-bit per piksel untuk RGB). Oleh karena itu, implementasi algoritma dalam studi ini dirancang dengan pendekatan spesifik:

1. **K-Means Color Quantization (Kategori: Lossy)**
   - **Konsep:** Menggunakan pendekatan _machine learning_ untuk melakukan klasterisasi jutaan variasi warna menjadi beberapa warna dominan (contoh: 16 warna).
   - **Implementasi:** Setelah klasterisasi matriks warna, citra dikonversi ke dalam mode Palet 8-bit (`P` mode dengan `Image.ADAPTIVE`) untuk memastikan ruang penyimpanan yang digunakan berkurang secara signifikan di dalam wadah `.bmp`.

2. **Singular Value Decomposition / SVD (Kategori: Lossy)**
   - **Konsep:** Menggunakan aljabar linear untuk mendekomposisi matriks citra menjadi tiga komponen matriks ($U, \Sigma, V^T$) dan mengabaikan (_truncate_) komponen dengan variansi rendah.
   - **Implementasi:** Berfokus pada kompresi resolusi/spasial. Pengukuran kompresi dihitung berdasarkan **ukuran teoretis ruang penyimpanan elemen matriks float32**, bukan dari ukuran berkas `.bmp` hasil rekonstruksi, untuk menyimulasikan ukuran penyimpanan seandainya struktur SVD murni disimpan.

3. **Run-Length Encoding / RLE (Kategori: Lossless)**
   - **Konsep:** Menyederhanakan penyimpanan data dengan mencatat jumlah perulangan piksel berderet yang memiliki nilai warna sama persis.
   - **Implementasi:** Pengukuran kompresi dihitung menggunakan **simulasi blok 4-Byte teoretis** (1 byte untuk jumlah deret, 3 byte untuk nilai RGB). Studi ini menunjukkan bahwa RLE berpotensi mengalami ekspansi data (_negative compression_) apabila diterapkan pada citra dengan variansi piksel tinggi atau yang memiliki _anti-aliasing_.

## Struktur Direktori

Arsitektur sistem dibangun secara modular dengan memisahkan logika komputasi dari logika antarmuka pengguna.

```text
studi-komparasi-kompresi/
│
├── algoritma/                 # Modul pemrosesan logika kompresi
│   ├── __init__.py
│   ├── rle_compress.py        # Logika iterasi deret warna RLE
│   ├── kmeans_compress.py     # Logika klasterisasi warna K-Means
│   └── svd_compress.py        # Logika dekomposisi matriks SVD
│
├── dataset/                   # Folder penempatan sampel citra .bmp
├── app.py                     # Antarmuka web pengujian
├── requirements.txt           # Daftar pustaka yang dibutuhkan
└── README.md                  # Dokumentasi proyek
```

## Persyaratan Sistem dan Instalasi

Sistem ini membutuhkan instalasi pustaka standar pemrosesan data dan antarmuka web.

### Dependensi Utama (berdasarkan `requirements.txt`)

- **streamlit** - Untuk pembangunan antarmuka web.
- **numpy** - Untuk komputasi matriks dan SVD.
- **scikit-learn** - Untuk model klasterisasi K-Means.
- **Pillow** - Untuk pembacaan dan penulisan berkas citra digital.

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
