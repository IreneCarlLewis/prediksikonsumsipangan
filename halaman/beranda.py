import streamlit as st
from utils import FAKTOR, INFO_FAKTOR, NAMA_PANGAN, SATUAN, TARGET, baca_data_panel


# ---------- Kepala halaman: judul + tujuan aplikasi ----------
with st.container(key="kepala_beranda"):
    st.title("Prediksi Konsumsi Pangan Wilayah")
    st.markdown("Aplikasi ini bertujuan memberikan gambaran prediksi rata-rata konsumsi per kapita 12 "
                "kelompok pangan di suatu wilayah berdasarkan kondisi sosial ekonominya, serta "
                "menjelaskan faktor yang berkaitan dengan hasil prediksi tersebut.")
    if st.button("Mulai Simulasi", icon=":material/arrow_forward:", key="mulai_atas"):
        st.switch_page("halaman/simulasi.py")

# ---------- Cara kerja aplikasi ----------
with st.container(key="kartu_proses"):
    st.subheader("Bagaimana aplikasi menghasilkan prediksi?")
    langkah = [
        (":material/edit_note:", "Data masukan", "Empat faktor sosial ekonomi",
         "Pengguna mengisi kepadatan penduduk, IPM, persentase penduduk miskin, dan tingkat "
         "pengangguran terbuka di halaman Simulasi Prediksi."),
        (":material/hub:", "Tentukan kelompok wilayah", "Pengelompokan K-Means",
         "Nilai yang diisi dibandingkan dengan tiga kelompok wilayah hasil pengelompokan 514 "
         "kabupaten/kota yang mirip kondisinya, lalu dipilih kelompok yang paling mirip."),
        (":material/forest:", "Hitung perkiraan konsumsi", "Model Random Forest",
         "Setiap kelompok wilayah memiliki 12 model, satu untuk setiap kelompok pangan, yang "
         "belajar dari data anggota kelompoknya tahun 2022–2025. Model kelompok yang terpilih "
         "menghitung perkiraan konsumsi 12 kelompok pangan."),
        (":material/insights:", "Jelaskan hasilnya", "Interpretasi SHAP",
         "Kontribusi setiap faktor terhadap hasil prediksi dihitung, sehingga terlihat faktor yang "
         "menaikkan dan menurunkan perkiraan. Hasilnya ditampilkan di halaman Interpretasi Lokal."),
    ]
    for i, (ikon, judul, sub, isi) in enumerate(langkah):
        with st.expander(f"**{judul}**  \n{sub}", icon=ikon, key=f"proses_{i}"):
            st.markdown(isi)
    st.caption("Keandalan setiap model diuji dengan menebak konsumsi kabupaten/kota yang tidak dipakai "
               "saat model belajar. Hasilnya dapat dilihat di halaman Evaluasi Kinerja Model.")

# ---------- Contoh skenario ----------
with st.container(border=True, key="kartu_contoh"):
    st.subheader(":material/lightbulb: Contoh penggunaan")
    st.markdown("Pemerintah suatu kabupaten berencana menurunkan persentase penduduk miskin dari 12% "
            "menjadi 10%. Perencana di Dinas Ketahanan Pangan ingin mengetahui, apakah konsumsi "
            "telur, ikan, dan pangan lainnya diperkirakan ikut naik atau turun.")
    kiri, tengah, kanan = st.columns(3)
    with kiri.container(border=True, height="stretch", key="langkah_1"):
        st.markdown("**1. Isi kondisi wilayah**")
        st.markdown("Isi kepadatan penduduk, IPM, kemiskinan (12%), dan pengangguran wilayah, atau "
                "gunakan nilai contoh yang tersedia, lalu tekan Prediksi.")
    with tengah.container(border=True, height="stretch", key="langkah_2"):
        st.markdown("**2. Ubah sesuai rencana**")
        st.markdown("Ganti nilai kemiskinan menjadi 10%, lalu tekan Prediksi lagi dan bandingkan "
                "hasilnya dengan prediksi sebelumnya.")
    with kanan.container(border=True, height="stretch", key="langkah_3"):
        st.markdown("**3. Pahami hasilnya**")
        st.markdown("Lihat perkiraan konsumsi 12 kelompok pangan, keandalan modelnya, dan faktor yang "
                "berkaitan dengan hasil di halaman Interpretasi Lokal.")

    if st.button("Mulai Simulasi", type="primary", icon=":material/arrow_forward:"):
        st.switch_page("halaman/simulasi.py")

# ---------- Penjelasan empat faktor ----------
with st.container(key="kartu_faktor"):
    st.subheader("Mengenal empat faktor sosial ekonomi")
    st.markdown("Keempat faktor berikut adalah data yang diisi pada halaman Simulasi Prediksi. "
                "Klik setiap faktor untuk melihat penjelasannya.")

    data = baca_data_panel()
    ikon_faktor = {"Nilai_kp": ":material/groups:", "Nilai_ipm": ":material/school:",
                   "P0": ":material/payments:", "Nilai_tpt": ":material/work:"}
    satuan_faktor = {"Nilai_kp": "Satuan: jiwa/km²", "Nilai_ipm": "Satuan: indeks 0–100",
                     "P0": "Satuan: persen (%)", "Nilai_tpt": "Satuan: persen (%)"}
    for i, f in enumerate(FAKTOR):
        info = INFO_FAKTOR[f]
        with st.expander(f"**{info['judul']}**  \n{satuan_faktor[f]}", icon=ikon_faktor[f],
                         key=f"proses_faktor_{i}"):
            st.markdown(f"{info['apa']}\n\n"
                        f"**Cara menghitung:** {info['hitung']}\n\n"
                        f"**Rentang nilai:** {info['rentang']}\n\n"
                        f":material/arrow_downward: **Makin kecil:** {info['kecil']}\n\n"
                        f":material/arrow_upward: **Makin besar:** {info['besar']}")
            st.caption(f"Pada data penelitian: {data[f].min():g} sampai {data[f].max():g}.")

# ---------- Hasil yang diperoleh ----------
with st.container(border=True, key="kartu_hasil"):
    st.subheader(":material/restaurant: Hasil yang diperoleh")
    st.markdown("Aplikasi menghasilkan perkiraan **rata-rata konsumsi** "
                "untuk 12 kelompok pangan berikut.")
    daftar = [f"{NAMA_PANGAN[t]} ({SATUAN[t]})" for t in TARGET]
    k1, k2, k3 = st.columns(3)
    k1.markdown("\n".join(f"- {d}" for d in daftar[0:4]))
    k2.markdown("\n".join(f"- {d}" for d in daftar[4:8]))
    k3.markdown("\n".join(f"- {d}" for d in daftar[8:12]))

# ---------- Isi halaman lain ----------
with st.container(border=True, key="kartu_halaman"):
    st.subheader(":material/map: Halaman pada aplikasi")
    st.markdown(
        "- **Simulasi Prediksi**: menghitung perkiraan konsumsi 12 kelompok pangan untuk kondisi "
        "wilayah yang diisi.\n"
        "- **Interpretasi Lokal**: menjelaskan faktor yang paling menaikkan atau menurunkan hasil "
        "prediksi.\n"
        "- **Evaluasi Kinerja Model**: menunjukkan seberapa akurat perkiraan untuk setiap kelompok "
        "pangan.\n"
        "- **Interpretasi Global**: menunjukkan faktor yang paling berpengaruh terhadap konsumsi "
        "setiap kelompok pangan.")

with st.container(border=True, key="kartu_keterangan"):
    st.markdown("Hasil aplikasi merupakan perkiraan berdasarkan pola data tahun 2022–2025, bukan data "
            "resmi BPS dan bukan ramalan tahun mendatang. Hasil juga menunjukkan keterkaitan, "
            "bukan hubungan sebab-akibat.")