import re
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
contoh["Kosongkan (isi sendiri)"] = pd.Series(None, index=FAKTOR, dtype="float")   # semua isian kosong

with st.container(border=True, key="kartu_input"):
    # Fungsi tombol Reset: hapus isian form dan hasil prediksi
    def reset_form():
        for kunci in list(st.session_state.keys()):
            if kunci.startswith(("kp_", "ipm_", "p0_", "tpt_")):
                del st.session_state[kunci]
        for kunci in ["input", "klaster", "baris_fitur", "prediksi"]:
            st.session_state.pop(kunci, None)
        st.session_state["pilihan_contoh"] = "Kosongkan (isi sendiri)"
        # Nomor ini naik setiap tombol ditekan, supaya kotak isian selalu dibuat ulang dalam keadaan kosong
        st.session_state["nomor_kosongkan"] = st.session_state.get("nomor_kosongkan", 0) + 1


    pilihan = st.selectbox("Gunakan nilai contoh", list(contoh.keys()), key="pilihan_contoh",
                        help="Nilai contoh adalah nilai tengah data tahun 2025, bukan data "
                                "kabupaten/kota tertentu. Setelah dipilih, setiap nilai tetap dapat "
                                "diubah sesuai kondisi wilayah yang ingin disimulasikan.")
    nilai_contoh = contoh[pilihan].round(2)
    nomor = st.session_state.get("nomor_kosongkan", 0)

    
    def nilai_awal(fitur):
        # Isi awal kotak dalam bentuk teks. Kosong ("") untuk pilihan "Kosongkan (isi sendiri)"
        return "" if pd.isna(nilai_contoh[fitur]) else f"{nilai_contoh[fitur]:.2f}"


def baca_angka(teks, batas_atas):
    # Mengubah isian teks menjadi angka. Hasil: (angka, pesan salah)
    # Titik dan koma sama-sama boleh. Pengguna hanya ditanya jika tulisannya bermakna ganda.
    teks = teks.strip().replace(" ", "")                  # buang semua spasi
    if teks == "":
        return None, None                                 # kosong, nanti dianggap "belum diisi"

    if re.fullmatch(r"\d+", teks):                        # 1622
        return float(teks), None
    if re.fullmatch(r"\d+[.,](\d{1,2}|\d{4,})", teks):    # 1622.33 / 1622,33 / 8,7 (bukan 3 angka)
        return float(teks.replace(",", ".")), None
    if re.fullmatch(r"\d{1,3}(\.\d{3})+,\d+", teks):      # 1.622,33 (gaya Indonesia)
        return float(teks.replace(".", "").replace(",", ".")), None
    if re.fullmatch(r"\d{1,3}(,\d{3})+\.\d+", teks):      # 1,622.33 (gaya Inggris)
        return float(teks.replace(",", "")), None
    if re.fullmatch(r"\d{1,3}([.,]\d{3}){2,}", teks) and len(set(re.sub(r"\d", "", teks))) == 1:
        return float(re.sub(r"[.,]", "", teks)), None     # 1.234.567 (ribuan, tanpa desimal)

    if re.fullmatch(r"\d+[.,]\d{3}", teks):               # 1.622 / 1,622: desimal atau ribuan?
        desimal = float(teks.replace(",", "."))
        ribuan = float(teks.replace(".", "").replace(",", ""))
        if ribuan > batas_atas:                           # ribuan tidak mungkin, jadi pasti desimal
            return desimal, None
        bulat = teks.replace(",", "").replace(".", "")
        return None, (f"ditulis {teks}. Apakah maksudnya {desimal:.2f} atau {bulat}? "
                      f"Tulis {desimal:.2f} untuk desimal, atau {bulat} untuk ribuan")

    return None, "harus berisi angka, contoh: 1622.33 atau 1622,33"

# Form input
with st.form("form_input", border=True):
    st.caption("Desimal boleh memakai titik atau koma, contoh: 1622.33 atau 1622,33.")
    kiri, kanan = st.columns(2)
    kp = kiri.text_input(NAMA_FITUR_AWAM["Nilai_kp"],
                           value=nilai_awal("Nilai_kp"), placeholder="Isi sendiri",
                           help=INFO_FAKTOR["Nilai_kp"]["apa"], key=f"kp_{pilihan}_{nomor}")
    kiri.caption(f"Rentang data: {teks_rentang('Nilai_kp')}")
    ipm = kanan.text_input(NAMA_FITUR_AWAM["Nilai_ipm"],
                             value=nilai_awal("Nilai_ipm"), placeholder="Isi sendiri",
                             help=INFO_FAKTOR["Nilai_ipm"]["apa"], key=f"ipm_{pilihan}_{nomor}")
    kanan.caption(f"Rentang data: {teks_rentang('Nilai_ipm')}")
    p0 = kiri.text_input(NAMA_FITUR_AWAM["P0"],
                           value=nilai_awal("P0"), placeholder="Isi sendiri",
                           help=INFO_FAKTOR["P0"]["apa"], key=f"p0_{pilihan}_{nomor}")
    kiri.caption(f"Rentang data: {teks_rentang('P0')}")
    tpt = kanan.text_input(NAMA_FITUR_AWAM["Nilai_tpt"],
                             value=nilai_awal("Nilai_tpt"), placeholder="Isi sendiri",
                             help=INFO_FAKTOR["Nilai_tpt"]["apa"], key=f"tpt_{pilihan}_{nomor}")
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

# Proses saat tombol ditekan 
if ditekan:
    # Cek isian dulu sebelum diprediksi
    kesalahan = []
    # Nama kotak, aturan nilai, dan cara mengecek aturannya
    aturan = {
        "Nilai_kp": ("Kepadatan penduduk", "harus lebih dari 0 dan paling besar 100.000 jiwa/km²",
                     lambda v: 0 < v <= 100000),
        "Nilai_ipm": ("IPM", "harus lebih dari 0 dan paling besar 100", lambda v: 0 < v <= 100),
        "P0": ("Persentase penduduk miskin", "harus antara 0 dan 100%", lambda v: 0 <= v <= 100),
        "Nilai_tpt": ("Tingkat pengangguran", "harus antara 0 dan 100%", lambda v: 0 <= v <= 100),
    }
    isian = {"Nilai_kp": kp, "Nilai_ipm": ipm, "P0": p0, "Nilai_tpt": tpt}   # masih berupa teks
    angka = {}                                                               # hasil ubahan ke angka
    batas_atas = {"Nilai_kp": 100000, "Nilai_ipm": 100, "P0": 100, "Nilai_tpt": 100}  # sama dengan aturan
    for fitur, teks_isian in isian.items():
        nama, syarat, sesuai = aturan[fitur]
        nilai_isian, pesan = baca_angka(teks_isian, batas_atas[fitur])   # ubah teks menjadi angka
        if pesan is not None:
            kesalahan.append(f"{nama} {pesan}.")
        elif nilai_isian is None:
            kesalahan.append(f"{nama} belum diisi. Nilainya {syarat}.")
        elif not sesuai(nilai_isian):
            kesalahan.append(f"{nama} {syarat}.")
        else:
            angka[fitur] = nilai_isian                     # simpan angka yang sudah benar

    if kesalahan:
        # Tampilkan pesan error dan hapus hasil lama supaya tidak membingungkan
        st.error("**Input belum valid, prediksi tidak dijalankan.**\n\n"
                 + "\n".join(f"- {k}" for k in kesalahan), icon=":material/error:")
        for kunci in ["input", "klaster", "baris_fitur", "prediksi"]:
            st.session_state.pop(kunci, None)
    else:
        try:
            nilai = {f: round(angka[f], 2) for f in ["Nilai_kp", "Nilai_ipm", "P0", "Nilai_tpt"]}
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

# Tampilkan hasil (selama sudah pernah diprediksi) 
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
                kolom[i].metric(NAMA_FITUR[f], f"{nilai[f]:.2f}{satuan}", border=True)
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

        # Grafik per satuan. Gram diubah ke Kg dan 100 ml diubah ke Liter,
        # supaya satuan yang sejenis (berat dengan berat, volume dengan volume) ada di satu grafik
        grafik = prediksi.copy()                                   # salinan, tabel di atas tidak berubah
        gram = grafik["Satuan"] == "Gram"
        grafik.loc[gram, "Prediksi Konsumsi"] = grafik.loc[gram, "Prediksi Konsumsi"] / 1000   # 1 kg = 1.000 gram
        grafik.loc[gram, "Satuan"] = "Kg"
        ml = grafik["Satuan"] == "× 100 ml"
        grafik.loc[ml, "Prediksi Konsumsi"] = grafik.loc[ml, "Prediksi Konsumsi"] / 10         # 100 ml = 0,1 liter
        grafik.loc[ml, "Satuan"] = "Liter"
        grafik.loc[gram | ml, "Kelompok Pangan"] = grafik.loc[gram | ml, "Kelompok Pangan"] + "*"  # tanda hasil ubahan

        judul = {"Kg": "Kilogram", "Butir": "Butir", "Liter": "Liter"}
        for satuan in ["Kg", "Butir", "Liter"]:                    # satu grafik untuk setiap satuan
            bagian = grafik[grafik["Satuan"] == satuan].sort_values("Prediksi Konsumsi")
            tinggi = 0.35 * len(bagian) + 0.9                          # tinggi mengikuti jumlah batang
            fig, ax = plt.subplots(figsize=(6.5, tinggi))
            fig.subplots_adjust(left=0.24, right=0.97, bottom=0.5 / tinggi, top=1 - 0.3 / tinggi)  # tepi sama untuk semua grafik
            batang = ax.barh(bagian["Kelompok Pangan"], bagian["Prediksi Konsumsi"], color="#5E9C76", height=0.6)
            ax.bar_label(batang, fmt="%.3f", padding=3, fontsize=8)   # angka di ujung batang
            ax.set_xlim(0, bagian["Prediksi Konsumsi"].max() * 1.15)  # ruang untuk angka
            ax.set_title(f"Prediksi Konsumsi Kelompok Pangan Bersatuan {judul[satuan]}")
            ax.set_xlabel(f"Prediksi Konsumsi ({satuan})")
            gaya_grafik(ax)
            st.pyplot(fig, width=700, bbox_inches=None)               # tanpa dipotong, supaya ukuran huruf sama
            plt.close(fig)
        st.caption("Setiap grafik hanya memuat kelompok pangan dengan satuan yang sama agar dapat "
                   "dibandingkan. Tanda * berarti satuannya diubah untuk grafik: bumbu-bumbuan padat "
                   "dari gram ke kg (dibagi 1.000) dan bumbu-bumbuan cair dari 100 ml ke liter "
                   "(dibagi 10). Tabel di atas tetap memakai satuan asli.")

        
        st.caption("Hasil merupakan perkiraan model berdasarkan pola data tahun 2022–2025, bukan data "
                   "resmi BPS, dan tidak dimaksudkan untuk meramal tahun-tahun mendatang.")


        st.markdown("Ingin tahu **mengapa** hasil prediksinya seperti ini? Halaman Interpretasi Lokal "
                    "menunjukkan faktor yang paling menaikkan atau menurunkan prediksi.")
        if st.button("Lihat Interpretasi", type="primary", icon=":material/arrow_forward:"):
            st.switch_page("halaman/interpretasi_lokal.py")