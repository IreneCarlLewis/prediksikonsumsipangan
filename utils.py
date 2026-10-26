from pathlib import Path
import joblib
import matplotlib.pyplot as plt
import pandas as pd
import shap
import streamlit as st

# Alamat folder
FOLDER_APP = Path(__file__).parent          # folder app_web/
FOLDER_MODEL = FOLDER_APP / "model"         # scaler, K-Means, 36 RF
FOLDER_HASIL = FOLDER_APP / "hasil"         # tabel hasil penelitian
FOLDER_MODEL_UTAMA = FOLDER_APP.parent / "hasil_model_utama"   # PEMODELAN/hasil_model_utama

# Fitur dan target (HARUS sama dengan saat pelatihan) ----------
FAKTOR = ["Nilai_kp", "Nilai_ipm", "P0", "Nilai_tpt"]   # 4 faktor sosial ekonomi
FITUR = FAKTOR + ["Tahun"]                               # 5 fitur RF, urutan tidak boleh berubah
TAHUN_ACUAN = 2025                                       # tahun yang dipakai di halaman Simulasi

# Urutan kelompok pangan untuk tabel dan grafik
TARGET = ["Total_Padi", "Total_Umbi", "Total_Ikan", "Total_Daging", "Total_Telur",
          "Total_Sayur", "Total_Kacang", "Total_Buah", "Total_Minyak", "Total_Kelapa",
          "Total_Bumbucair", "Total_Bumbupadat"]

# ---------- 3. Nama tampilan (silakan sesuaikan teksnya di sini saja) ----------
NAMA_PANGAN = {"Total_Padi": "Padi-padian", "Total_Umbi": "Umbi-umbian", "Total_Ikan": "Ikan",
               "Total_Daging": "Daging", "Total_Telur": "Telur", "Total_Sayur": "Sayur-sayuran",
               "Total_Kacang": "Kacang-kacangan", "Total_Buah": "Buah-buahan",
               "Total_Minyak": "Minyak", "Total_Kelapa": "Kelapa",
               "Total_Bumbucair": "Bumbu-bumbuan cair", "Total_Bumbupadat": "Bumbu-bumbuan padat"}

SATUAN = {"Total_Padi": "Kg", "Total_Umbi": "Kg", "Total_Ikan": "Kg", "Total_Daging": "Kg",
          "Total_Telur": "Butir", "Total_Sayur": "Kg", "Total_Kacang": "Kg", "Total_Buah": "Kg",
          "Total_Minyak": "Liter", "Total_Kelapa": "Butir", "Total_Bumbucair": "× 100 ml",
          "Total_Bumbupadat": "Gram"}

NAMA_FITUR = {"Nilai_kp": "Kepadatan penduduk", "Nilai_ipm": "IPM", "P0": "P0",
              "Nilai_tpt": "TPT", "Tahun": "Tahun"}
NAMA_FITUR_LENGKAP = {**NAMA_FITUR, "Tahun": "Tahun (variabel kontrol)"}

NAMA_FITUR_AWAM = {"Nilai_kp": "Kepadatan penduduk (jiwa/km²)",
                   "Nilai_tpt": "Tingkat Pengangguran Terbuka / TPT (%)",
                   "Nilai_ipm": "Indeks Pembangunan Manusia / IPM",
                   "P0": "Persentase penduduk miskin / P0 (%)"}

# Urutan dan warna faktor di grafik Interpretasi Global
URUTAN_FAKTOR = ["Nilai_ipm", "P0", "Nilai_kp", "Nilai_tpt", "Tahun"]
WARNA_FAKTOR = {"Nilai_ipm": "#2E7BD6", "P0": "#E8683A", "Nilai_kp": "#1EAD7E",
                "Nilai_tpt": "#EBA40C", "Tahun": "#A3A3A3"}

# Nomor cluster di model (0, 1, 2) -> nama yang ditampilkan
SINGKATAN_CLUSTER = {0: "Kepadatan Rendah", 1: "Padat Penduduk", 2: "Kepadatan Sangat Rendah"}

def nama_kelompok(klaster):
    return f"Kelompok Wilayah {klaster + 1} ({SINGKATAN_CLUSTER[klaster]})"

# ---------- Teks penjelasan untuk pengguna awam ----------
PERIODE = "per orang per minggu"

KETERANGAN_KELOMPOK = {
    0: "Wilayah berkepadatan rendah dengan kesejahteraan menengah. Kelompok terbesar, sebagian "
       "besar kabupaten (contoh: Banyuwangi, Sumedang, Soppeng).",
    1: "Wilayah padat dengan kesejahteraan tinggi. Umumnya kota dan kabupaten di sekitar kota "
       "besar (contoh: Kota Semarang, Kota Bekasi, Sidoarjo).",
    2: "Wilayah berkepadatan sangat rendah dengan kesejahteraan rendah. Persentase penduduk "
       "miskin tinggi dan IPM rendah, sebagian besar di Papua, NTT, dan Maluku "
       "(contoh: Asmat, Sumba Barat, Kepulauan Aru).",
}


INFO_FAKTOR = {
    "Nilai_kp": {
        "judul": "Kepadatan Penduduk",
        "apa": "Banyaknya penduduk yang tinggal di setiap 1 km² wilayah.",
        "hitung": "Jumlah penduduk dibagi luas wilayah (km²).",
        "rentang": "Mulai dari 0 jiwa/km², tidak ada batas atas.",
        "kecil": "Wilayah lengang, umumnya perdesaan atau pedalaman.",
        "besar": "Wilayah padat, umumnya perkotaan.",
    },
    "Nilai_ipm": {
        "judul": "Indeks Pembangunan Manusia (IPM)",
        "apa": "Angka ringkasan kualitas hidup penduduk suatu wilayah didasarkan pada tiga dimensi dasar.",
        "hitung": "Gabungan tiga hal: kesehatan (umur harapan hidup), pendidikan (lama sekolah), "
                  "dan standar hidup (pengeluaran per orang). Ketiganya dirata-rata menjadi "
                  "satu angka.",
        "rentang": "0 sampai 100. Kategori BPS: di bawah 60 rendah, 60–70 sedang, 70–80 tinggi, "
                   "80 ke atas sangat tinggi.",
        "kecil": "Kesehatan, pendidikan, dan daya beli penduduk masih rendah.",
        "besar": "Kesehatan, pendidikan, dan daya beli penduduk makin baik.",
    },
    "P0": {
        "judul": "Persentase Penduduk Miskin (P0)",
        "apa": "Ketidakmampuan ekonomi seseorang untuk memenuhi kebutuhan dasar pangan maupun nonpangan.",
        "hitung": "Jumlah penduduk yang pengeluarannya per bulan berada di bawah garis kemiskinan, "
                  "dibagi jumlah seluruh penduduk, dikali 100%. Garis kemiskinan adalah batas "
                  "pengeluaran minimum untuk makanan dan kebutuhan pokok lainnya.",
        "rentang": "0% sampai 100%.",
        "kecil": "Makin sedikit penduduk miskin.",
        "besar": "Makin banyak penduduk miskin.",
    },
    "Nilai_tpt": {
        "judul": "Tingkat Pengangguran Terbuka (TPT)",
        "apa": "Bagian angkatan kerja yang belum mendapat pekerjaan.",
        "hitung": "Jumlah pengangguran dibagi jumlah angkatan kerja (penduduk usia 15 tahun ke "
                  "atas yang bekerja atau sedang mencari kerja), dikali 100%.",
        "rentang": "0% sampai 100%.",
        "kecil": "Hampir semua angkatan kerja sudah bekerja.",
        "besar": "Makin banyak pengangguran. Di perkotaan TPT sering lebih tinggi karena banyak "
                 "pencari kerja, jadi TPT tinggi tidak selalu berarti wilayah miskin.",
    },
}


def keterangan_nilai(fitur, nilai):
    if fitur == "Nilai_ipm":
        if nilai < 60:
            return "kategori rendah"
        elif nilai < 70:
            return "kategori sedang"
        elif nilai < 80:
            return "kategori tinggi"
        return "kategori sangat tinggi"
    data = baca_data_panel()
    tengah = data[data["Tahun"] == TAHUN_ACUAN][fitur].median()
    if abs(nilai - tengah) <= 0.01:
        return f"sama dengan nilai tengah nasional ({tengah:.2f})"
    if nilai > tengah:
        return f"di atas nilai tengah nasional ({tengah:.2f})"
    return f"di bawah nilai tengah nasional ({tengah:.2f})"


# ---------- 4. Format angka gaya Indonesia (koma desimal) untuk kalimat ----------
def angka_id(nilai, desimal=3, tanda=False):
    teks = f"{nilai:+.{desimal}f}" if tanda else f"{nilai:.{desimal}f}"
    return teks.replace("-", "−").replace(".", ",")      # 0.041 -> 0,041 ; -0.014 -> −0,014


NAMA_FAKTOR_AWAM = {"Nilai_kp": "kepadatan penduduk",
                    "Nilai_ipm": "IPM (kualitas hidup penduduk)",
                    "P0": "persentase penduduk miskin",
                    "Nilai_tpt": "tingkat pengangguran",
                    "Tahun": "perbedaan tahun"}


def gabung(daftar):
    """['a', 'b', 'c'] -> 'a, b dan c' supaya kalimat terdengar wajar."""
    if len(daftar) == 1:
        return daftar[0]
    return ", ".join(daftar[:-1]) + " dan " + daftar[-1]


def angka_singkat(nilai):
    """Angka kecil ditulis 3 desimal, angka besar 2 desimal, dengan koma desimal."""
    return angka_id(nilai, 3 if abs(nilai) < 1 else 2)


def takaran(nilai, target):
    """Angka + satuan yang enak dibaca, misalnya '1,82 kg' atau '17,1 ml'."""
    if target == "Total_Bumbucair":                     # satuan asli 100 ml -> diubah ke ml
        return f"{angka_id(nilai * 100, 1)} ml"
    return f"{angka_singkat(nilai)} {SATUAN[target].lower()}"


# ---------- 5. Membaca tabel dan model (disimpan di cache) ----------
# @st.cache_data      : untuk tabel. Dibaca sekali, lalu dipakai ulang.
# @st.cache_resource  : untuk model. Dibuka sekali, dipakai semua halaman.

@st.cache_data
def baca_data_panel():
    data = pd.read_excel(FOLDER_HASIL / "data_panel_cluster.xlsx")
    return data.drop(columns=["Unnamed: 0"], errors="ignore")

@st.cache_data
def baca_metrik_per_cluster():
    return pd.read_excel(FOLDER_HASIL / "metrik_per_cluster.xlsx")

@st.cache_data
def baca_shap_global():
    return pd.read_excel(FOLDER_HASIL / "hasil_shap.xlsx", sheet_name="shap_global")

@st.cache_resource
def muat_clustering():
    scaler = joblib.load(FOLDER_MODEL_UTAMA / "kmeans" / "scaler_clustering.joblib")
    kmeans = joblib.load(FOLDER_MODEL_UTAMA / "kmeans" / "model_clustering.joblib")
    return scaler, kmeans

@st.cache_resource
def muat_rf(klaster, target):
    return joblib.load(FOLDER_MODEL_UTAMA / "randomforest" / f"rf_cluster{klaster}_{target}.joblib")



# ---------- 6. Fungsi inti ----------

def tentukan_cluster(nilai_faktor):
    scaler, kmeans = muat_clustering() # panggil fungsi scaler dan clustering
    kolom = list(scaler.feature_names_in_) # mengambil urutan kolom di scaler              
    baris = pd.DataFrame([nilai_faktor])[kolom] # susun ulang urutan kolom
    z = pd.DataFrame(scaler.transform(baris), columns=kolom) # standardisasi input user
    return int(kmeans.predict(z)[0]) # hitung k means

def prediksi_12_pangan(klaster, baris_fitur):
    hasil = [] # menyimpah hasil prediksi setiap pangan
    for target in TARGET: # untuk setiap kelompok pangan
        rf = muat_rf(klaster, target) # panggil model prediksi yang cocok
        # catat hasil untuk ditampilkan dalam bentuk tabel di aplikasi
        hasil.append({"target": target,
                      "Kelompok Pangan": NAMA_PANGAN[target], # ambil nama pangan
                      "Prediksi Konsumsi": rf.predict(baris_fitur[FITUR])[0], # prediksi
                      "Satuan": SATUAN[target]}) # ambil satuan
    return pd.DataFrame(hasil) # ubah jadi tabel dan kembalikan ke simulasi.py

def hitung_shap(klaster, target, baris_fitur):
    rf = muat_rf(klaster, target) # panggil model prediksi yang cocok
    # panggil explainer untuk setiap prediktor
    hasil = shap.TreeExplainer(rf)(baris_fitur[FITUR])[0]  
    return hasil

def teks_rentang(fitur):
    data = baca_data_panel()
    return f"{data[fitur].min():g}–{data[fitur].max():g}"

def tabel_kelompok():
    data = baca_data_panel()
    terbaru = data[data["Tahun"] == TAHUN_ACUAN]
    baris = []
    for k in [0, 1, 2]:
        bagian = terbaru[terbaru["cluster"] == k]
        baris.append({"Kelompok": nama_kelompok(k),
                      "Gambaran": KETERANGAN_KELOMPOK[k],
                      "Jumlah kab/kota": data[data["cluster"] == k]["Kabupaten/Kota"].nunique(),
                      "Kepadatan": bagian["Nilai_kp"].median(),
                      "TPT (%)": bagian["Nilai_tpt"].median(),
                      "IPM": bagian["Nilai_ipm"].median(),
                      "P0 (%)": bagian["P0"].median()})
    return pd.DataFrame(baris)


def penjelasan_kelompok_wilayah():
    with st.expander("Apa itu Kelompok Wilayah?"):
        st.markdown("Ke-514 kabupaten/kota dikelompokkan menjadi tiga kelompok wilayah berdasarkan "
                    "kemiripan keempat faktor sosial ekonominya (metode K-Means). Setiap kelompok "
                    "memiliki model prediksi sendiri, karena pola konsumsi di wilayah perkotaan "
                    "berbeda dengan wilayah perdesaan atau wilayah tertinggal. Angka pada tabel "
                    "adalah nilai tengah (median) tahun 2025.")
        st.dataframe(tabel_kelompok(), hide_index=True, width="stretch",
                     column_config={"Kepadatan": st.column_config.NumberColumn(format="%.0f"),
                                    "TPT (%)": st.column_config.NumberColumn(format="%.2f"),
                                    "IPM": st.column_config.NumberColumn(format="%.2f"),
                                    "P0 (%)": st.column_config.NumberColumn(format="%.2f")})

def tinggi_tabel(jumlah_baris):
    """Tinggi tabel (piksel) supaya semua baris terlihat tanpa scroll: ±35 piksel per baris."""
    return (jumlah_baris + 1) * 35 + 3


# ---------- 7. Gaya grafik bersama ----------
def gaya_grafik(ax):
    """Bingkai tipis di keempat sisi dan garis bantu tipis, seperti desain."""
    for sisi in ax.spines.values():
        sisi.set_linewidth(0.8)
    ax.grid(axis="x", color="#E5E7EB", linewidth=0.8)
    ax.set_axisbelow(True)                                    # garis bantu di belakang batang
    ax.tick_params(labelsize=8)

plt.rcParams.update({"font.size": 8, "axes.titlesize": 9})
