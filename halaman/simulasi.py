from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from utils import (FAKTOR, INFO_FAKTOR, KETERANGAN_KELOMPOK, NAMA_FITUR, NAMA_FITUR_AWAM,
                   PERIODE, TAHUN_ACUAN, baca_data_panel, baca_metrik_per_cluster, gaya_grafik,
                   keterangan_nilai, nama_kelompok, penjelasan_kelompok_wilayah,
                   prediksi_12_pangan, teks_rentang, tentukan_cluster, tinggi_tabel)

with st.container(key="kepala_beranda"):
    st.title("Simulasi Prediksi")
with st.container(border=True, key="kartu_simulasi"):
    st.markdown("Isi kondisi sosial ekonomi sebuah wilayah, lalu tekan **Prediksi** untuk melihat "
                "perkiraan konsumsi 12 kelompok pangan. Untuk menguji skenario lain, ubah nilainya lalu "
                "tekan **Prediksi** lagi. Penjelasan setiap faktor tersedia di halaman Beranda.")

data = baca_data_panel()
data_2025 = data[data["Tahun"] == TAHUN_ACUAN]

# Nilai contoh: nilai tengah (median) tahun 2025, bukan data wilayah tertentu
contoh = {"Nilai tengah seluruh kabupaten/kota": data_2025[FAKTOR].median()}
for k in [0, 1, 2]:
    bagian = data_2025[data_2025["cluster"] == k]
    contoh[f"Wilayah khas {nama_kelompok(k)}"] = bagian[FAKTOR].median()
contoh["Kosongkan (isi sendiri)"] = pd.Series(0.0, index=FAKTOR)   # semua isian 0

with st.container(border=True, key="kartu_input"):
    # Fungsi tombol Reset: hapus isian form dan hasil prediksi
    def reset_form():
        for kunci in list(st.session_state.keys()):
            if kunci.startswith(("kp_", "ipm_", "p0_", "tpt_")):
                del st.session_state[kunci]
        for kunci in ["input", "klaster", "baris_fitur", "prediksi"]:
            st.session_state.pop(kunci, None)
        st.session_state["pilihan_contoh"] = "Kosongkan (isi sendiri)"


    pilihan = st.selectbox("Gunakan nilai contoh", list(contoh.keys()), key="pilihan_contoh",
                        help="Nilai contoh adalah nilai tengah data tahun 2025, bukan data "
                                "kabupaten/kota tertentu. Setelah dipilih, setiap nilai tetap dapat "
                                "diubah sesuai kondisi wilayah yang ingin disimulasikan.")
    nilai_contoh = contoh[pilihan].round(2)

# ---------- Form input ----------
with st.form("form_input", border=True):
    st.caption("Gunakan **titik (.)** sebagai pemisah desimal, contoh: 8.74 (bukan 8,74).")
    kiri, kanan = st.columns(2)
    kp = kiri.number_input(NAMA_FITUR_AWAM["Nilai_kp"],
                           value=float(nilai_contoh["Nilai_kp"]), format="%.2f",
                           help=INFO_FAKTOR["Nilai_kp"]["apa"], key=f"kp_{pilihan}")
    kiri.caption(f"Rentang data: {teks_rentang('Nilai_kp')}")
    ipm = kanan.number_input(NAMA_FITUR_AWAM["Nilai_ipm"],
                             value=float(nilai_contoh["Nilai_ipm"]), format="%.2f",
                             help=INFO_FAKTOR["Nilai_ipm"]["apa"], key=f"ipm_{pilihan}")
    kanan.caption(f"Rentang data: {teks_rentang('Nilai_ipm')}")
    p0 = kiri.number_input(NAMA_FITUR_AWAM["P0"],
                           value=float(nilai_contoh["P0"]), format="%.2f",
                           help=INFO_FAKTOR["P0"]["apa"], key=f"p0_{pilihan}")
    kiri.caption(f"Rentang data: {teks_rentang('P0')}")
    tpt = kanan.number_input(NAMA_FITUR_AWAM["Nilai_tpt"],
                             value=float(nilai_contoh["Nilai_tpt"]), format="%.2f",
                             help=INFO_FAKTOR["Nilai_tpt"]["apa"], key=f"tpt_{pilihan}")
    kanan.caption(f"Rentang data: {teks_rentang('Nilai_tpt')}")
    st.selectbox("Tahun acuan", [TAHUN_ACUAN], disabled=True,
                 help="Tahun dikunci pada 2025 (tahun data terbaru), sehingga hasil menggambarkan "
                      "kondisi tahun 2025.")
    st.caption("Keempat faktor saling berkaitan, misalnya wilayah dengan kemiskinan rendah umumnya "
               "memiliki IPM yang lebih tinggi. Isi kombinasi nilai yang wajar agar hasil prediksi "
               "lebih dapat dipercaya.")
    with st.container(horizontal=True):
        ditekan = st.form_submit_button("Prediksi", type="primary", icon=":material/calculate:")
        st.form_submit_button("Reset", icon=":material/restart_alt:", on_click=reset_form)

# ---------- Proses saat tombol ditekan ----------
if ditekan:
    # Cek isian dulu sebelum diprediksi
    kesalahan = []
    if kp <= 0 or kp > 100000:
        kesalahan.append("Kepadatan penduduk harus lebih dari 0 dan paling besar 100.000 jiwa/km².")
    if ipm <= 0 or ipm > 100:
        kesalahan.append("IPM harus lebih dari 0 dan paling besar 100.")
    if p0 < 0 or p0 > 100:
        kesalahan.append("Persentase penduduk miskin harus antara 0 dan 100%.")
    if tpt < 0 or tpt > 100:
        kesalahan.append("Tingkat pengangguran harus antara 0 dan 100%.")

    if kesalahan:
        # Tampilkan pesan error dan hapus hasil lama supaya tidak membingungkan
        st.error("**Input belum valid, prediksi tidak dijalankan.**\n\n"
                 + "\n".join(f"- {k}" for k in kesalahan), icon=":material/error:")
        for kunci in ["input", "klaster", "baris_fitur", "prediksi"]:
            st.session_state.pop(kunci, None)
    else:
        try:
            nilai = {"Nilai_kp": round(kp, 2), "Nilai_ipm": round(ipm, 2),
                     "P0": round(p0, 2), "Nilai_tpt": round(tpt, 2)}
            klaster = tentukan_cluster(nilai)
            baris_fitur = pd.DataFrame([{**nilai, "Tahun": TAHUN_ACUAN}])
            # Disimpan di session_state supaya bisa dipakai halaman Interpretasi Lokal
            st.session_state["input"] = nilai
            st.session_state["klaster"] = klaster
            st.session_state["baris_fitur"] = baris_fitur
            st.session_state["prediksi"] = prediksi_12_pangan(klaster, baris_fitur)
        except Exception:
            # Kalau ada kesalahan tak terduga, tampilkan pesan yang mudah dipahami
            st.error("Terjadi kesalahan saat menghitung prediksi. Periksa kembali isian Anda, "
                     "lalu coba tekan Prediksi lagi.", icon=":material/error:")
            for kunci in ["input", "klaster", "baris_fitur", "prediksi"]:
                st.session_state.pop(kunci, None)

# ---------- Tampilkan hasil (selama sudah pernah diprediksi) ----------
if "prediksi" in st.session_state:
    nilai = st.session_state["input"]
    klaster = st.session_state["klaster"]
    prediksi = st.session_state["prediksi"]

    with st.container(border=True, key="kartu_hasil"):
        st.subheader("Hasil prediksi")

        # Peringatan kalau ada nilai di luar rentang data penelitian
        di_luar = [NAMA_FITUR[f] for f in FAKTOR if not data[f].min() <= nilai[f] <= data[f].max()]
        if di_luar:
            st.warning("Nilai berikut berada di luar rentang data penelitian, sehingga hasil "
                       "prediksi kurang dapat dipercaya: " + ", ".join(di_luar))

        # Kondisi yang diisi beserta artinya
        with st.container(border=True):
            st.markdown("**Kondisi yang diisi**")
            kolom = st.columns(4)
            for i, f in enumerate(["Nilai_kp", "Nilai_ipm", "P0", "Nilai_tpt"]):
                satuan = "%" if f in ("P0", "Nilai_tpt") else ""
                kolom[i].metric(NAMA_FITUR[f], f"{nilai[f]:g}{satuan}", border=True)
                kolom[i].caption(keterangan_nilai(f, nilai[f]))
            st.markdown(f"Termasuk **{nama_kelompok(klaster)}**: {KETERANGAN_KELOMPOK[klaster]}")
        penjelasan_kelompok_wilayah()

        # Tabel prediksi + R² model
        padi = prediksi[prediksi["target"] == "Total_Padi"].iloc[0]
        st.markdown(f"Angka pada tabel adalah perkiraan rata-rata konsumsi **{PERIODE}** di wilayah "
                    f"dengan kondisi seperti yang diisi. Contoh: Padi-padian "
                    f"{padi['Prediksi Konsumsi']:.2f} {padi['Satuan']} berarti setiap orang diperkirakan "
                    f"mengonsumsi sekitar {padi['Prediksi Konsumsi']:.2f} {padi['Satuan']} "
                    f"padi-padian dalam seminggu.")
        cair = prediksi[prediksi["target"] == "Total_Bumbucair"].iloc[0]
        st.markdown(f"Bumbu-bumbuan cair memakai satuan 100 ml (contoh: {cair['Prediksi Konsumsi']:.3f} "
                           f"× 100 ml = sekitar {cair['Prediksi Konsumsi'] * 100:.0f} ml).")
        metrik = baca_metrik_per_cluster()
        r2_rf = metrik[(metrik["cluster"] == klaster) & (metrik["model"] == "RF")]
        r2_rf = r2_rf.set_index("target")["R2"]
        tabel = prediksi.copy()
        tabel = prediksi.copy()
        tabel = tabel.drop(columns="target")
        st.dataframe(tabel, hide_index=True, width="stretch", height=tinggi_tabel(len(tabel)),
                     column_config={"Prediksi Konsumsi": st.column_config.NumberColumn(format="%.3f")})
        st.caption("Ketepatan prediksi berbeda-beda untuk setiap kelompok pangan. Hasil pengujian "
                   "model dapat dilihat di halaman Evaluasi Kinerja Model.")

        # Grafik hanya untuk pangan bersatuan Kg, supaya panjang batang bisa dibandingkan
        kg = prediksi[prediksi["Satuan"] == "Kg"].sort_values("Prediksi Konsumsi")
        fig, ax = plt.subplots(figsize=(6.5, 2.8))
        ax.barh(kg["Kelompok Pangan"], kg["Prediksi Konsumsi"], color="#5E9C76", height=0.6)
        ax.set_title("Prediksi konsumsi, kelompok pangan bersatuan kilogram")
        ax.set_xlabel("Prediksi konsumsi (Kg)")
        gaya_grafik(ax)
        st.pyplot(fig, width=700)
        plt.close(fig)
        st.caption("Grafik hanya memuat kelompok pangan bersatuan kilogram agar dapat dibandingkan. "
                   "Kelompok pangan lain (telur, minyak, kelapa, bumbu-bumbuan) ditampilkan pada tabel.")

        
        st.caption("Hasil merupakan perkiraan model berdasarkan pola data tahun 2022–2025, bukan data "
                   "resmi BPS, dan tidak dimaksudkan untuk meramal tahun-tahun mendatang.")


        st.markdown("Ingin tahu **mengapa** hasil prediksinya seperti ini? Halaman Interpretasi Lokal "
                    "menunjukkan faktor yang paling menaikkan atau menurunkan prediksi.")
        if st.button("Lihat Interpretasi", type="primary", icon=":material/arrow_forward:"):
            st.switch_page("halaman/interpretasi_lokal.py")