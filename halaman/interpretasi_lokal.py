import matplotlib.pyplot as plt
import pandas as pd
import shap
import streamlit as st
from utils import (FITUR, NAMA_FAKTOR_AWAM, NAMA_FITUR, NAMA_FITUR_LENGKAP, NAMA_PANGAN, PERIODE,
                   SATUAN, TARGET, angka_id, gabung, hitung_shap, nama_kelompok, takaran)

with st.container(key="kepala_beranda"):
    st.title("Interpretasi Lokal")
with st.container(border=True, key="kartu_lokal"):
    st.markdown("Halaman ini menjawab pertanyaan: **mengapa hasil prediksi bernilai sekian?** "
            "Penjelasan dimulai dari rata-rata prediksi di kelompok wilayah, lalu setiap faktor "
            "menambah atau mengurangi nilai tersebut hingga mencapai hasil prediksi untuk data "
            "yang Anda isi di halaman Simulasi Prediksi.")

# Halaman ini butuh hasil dari halaman Simulasi
if "prediksi" not in st.session_state:
    st.info("Belum ada hasil prediksi. Silakan isi kondisi wilayah dan tekan **Prediksi** di "
            "halaman Simulasi Prediksi terlebih dahulu.")
    
    if st.button("Buka Simulasi Prediksi", type="primary", icon=":material/arrow_forward:"):
        st.switch_page("halaman/simulasi.py")
    st.stop()

nilai = st.session_state["input"]
klaster = st.session_state["klaster"]
baris_fitur = st.session_state["baris_fitur"]

# ---------- Ringkasan input ----------
with st.container(border=True, key="kartu_nilai"):
    st.markdown("Nilai faktor yang diisi di halaman Simulasi Prediksi:")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Kepadatan penduduk", f"{nilai['Nilai_kp']:g}", border=True)        # :g = tanpa nol berlebih
    k2.metric("TPT", f"{nilai['Nilai_tpt']:.2f}%", border=True)
    k3.metric("IPM", f"{nilai['Nilai_ipm']:.2f}", border=True)
    k4.metric("P0", f"{nilai['P0']:.2f}%", border=True)
    st.markdown(f"Kelompok wilayah: **{nama_kelompok(klaster)}**")

# Pilih kelompok pangan
with st.container(border=True, key="kartu_grafikshap"):
    target = st.selectbox("Kelompok pangan", TARGET, index=TARGET.index("Total_Ikan"),
                          format_func=lambda t: NAMA_PANGAN[t])
    st.caption(f"Satuan prediksi dan kontribusi: {SATUAN[target]} {PERIODE}.")
    penjelasan = hitung_shap(klaster, target, baris_fitur)
    nilai_shap = penjelasan.values  # 5 angka kontribusi tiap fitur
    nilai_dasar = float(penjelasan.base_values) # rata-rata prediksi di kelompok wilayah
    prediksi = nilai_dasar + nilai_shap.sum() # hasil prediksi model (aditivitas)

# Grafik waterfall
    grafik = shap.Explanation(values=nilai_shap, base_values=nilai_dasar, 
                              data=penjelasan.data, feature_names=[NAMA_FITUR[f] for f in FITUR])
    shap.plots.waterfall(grafik, show=False)
    fig = plt.gcf()
    fig.set_size_inches(7, 3.4)
    st.pyplot(fig)
    plt.close(fig)

    with st.expander("Cara membaca grafik", expanded=True):
        st.markdown(
            "- **E[f(X)]** (paling bawah) adalah rata-rata prediksi seluruh kabupaten/kota di kelompok "
            "wilayah ini, sebagai titik awal.\n"
            "- **f(x)** (paling atas) adalah hasil prediksi untuk nilai yang Anda isi.\n"
            "- Batang **merah (+)** menaikkan prediksi, batang **biru (−)** menurunkan prediksi. "
            "Makin panjang batangnya, makin besar pengaruh faktor tersebut.\n"
            "- Angka abu-abu di sebelah kiri nama faktor adalah nilai yang Anda isi.\n"
            "- **Tahun** dikunci pada 2025. Kontribusinya menunjukkan perbedaan tahun 2025 dibanding "
            "rata-rata tahun 2022–2025, bukan pengaruh faktor sosial ekonomi.\n"
            "- Kontribusi menunjukkan cara model memakai setiap faktor, bukan bukti sebab-akibat.")

    # Tabel kontribusi (urut dari pengaruh terbesar)
    tabel = pd.DataFrame({
        "fitur": FITUR,
        "Faktor": [NAMA_FITUR_LENGKAP[f] for f in FITUR],
        "Nilai Input": [f"{penjelasan.data[i]:g}" if f in ("Nilai_kp", "Tahun") else f"{penjelasan.data[i]:.2f}" for i, f in enumerate(FITUR)],
        "kontribusi": nilai_shap,
    })
    tabel["Kontribusi"] = tabel["kontribusi"].map(lambda v: f"{v:+.3f}".replace("-", "−"))
    tabel["Arah"] = tabel["kontribusi"].map(lambda v: "menaikkan" if v > 0 else "menurunkan")
    tabel = tabel.reindex(tabel["kontribusi"].abs().sort_values(ascending=False).index)
    st.dataframe(tabel[["Faktor", "Nilai Input", "Kontribusi", "Arah"]], hide_index=True,
                 width="stretch",
                 column_config={"Nilai Input": st.column_config.TextColumn(),
                                "Kontribusi": st.column_config.TextColumn()})

# Kalimat penjelasan otomatis (hanya 4 faktor sosial ekonomi, tanpa Tahun)
    sosek = tabel[tabel["fitur"] != "Tahun"]
    naik = sosek[sosek["kontribusi"] > 0].sort_values("kontribusi", ascending=False)
    turun = sosek[sosek["kontribusi"] < 0].sort_values("kontribusi")
    pangan = NAMA_PANGAN[target].lower()

        # Kalimat 1: hasil prediksi dibandingkan rata-rata wilayah yang serupa
    selisih = prediksi - nilai_dasar
    if abs(selisih) < 0.05 * abs(nilai_dasar):
        banding = "hampir sama dengan"
    elif selisih > 0:
        banding = "lebih tinggi daripada"
    else:
        banding = "lebih rendah daripada"
    kalimat = (f"Untuk kondisi yang Anda isi, setiap orang diperkirakan mengonsumsi sekitar "
               f"**{takaran(prediksi, target)} {pangan} per minggu**. Angka ini {banding} "
               f"rata-rata wilayah di {nama_kelompok(klaster)}, yaitu sekitar "
               f"{takaran(nilai_dasar, target)} dimana kelompok ini memiliki kemiripan dengan kondisi wilayah yang diinputkan "
               f"pada sistem.\n\n")

    # Kalimat 2: faktor yang paling menaikkan dan paling menurunkan perkiraan
    if len(naik):
        f = naik.iloc[0]
        kalimat += (f"Faktor yang paling **mendorong konsumsi naik** adalah "
                    f"{NAMA_FAKTOR_AWAM[f['fitur']]}, yang membuat perkiraan naik sekitar "
                    f"{takaran(f['kontribusi'], target)}. ")
    if len(turun):
        f = turun.iloc[0]
        awal = "Sebaliknya, faktor" if len(naik) else "Faktor"
        kalimat += (f"{awal} yang paling **menurunkan konsumsi** adalah "
                    f"{NAMA_FAKTOR_AWAM[f['fitur']]}, yang membuat nilai prediksi turun sekitar "
                    f"{takaran(abs(f['kontribusi']), target)}. ")

    # Kalimat 3: faktor yang pengaruhnya kecil
    terbesar = sosek["kontribusi"].abs().max()
    kecil = [NAMA_FAKTOR_AWAM[f] for f, v in zip(sosek["fitur"], sosek["kontribusi"])
             if abs(v) < 0.1 * terbesar]
    if kecil:
        kalimat += f"Pengaruh {gabung(kecil)} relatif kecil. "

    # Kalimat 4: penjelasan Tahun (paragraf baru)
    kontribusi_tahun = tabel.loc[tabel["fitur"] == "Tahun", "kontribusi"].iloc[0]
    arah_tahun = "menaikkan" if kontribusi_tahun > 0 else "menurunkan"
    kalimat += (f"\n\nSelain empat faktor tersebut, ada **Tahun** yang "
                f"{arah_tahun} perkiraan sekitar {takaran(abs(kontribusi_tahun), target)}. Tahun "
                f"bukan faktor sosial ekonomi. Tahun menangkap perubahan konsumsi dari tahun ke tahun "
                f"yang tidak tercakup oleh keempat faktor, misalnya karena perubahan harga pangan "
                f"atau kebijakan yang berlaku secara nasional.")

    # Tampilkan semua kalimat sekaligus (cukup SATU kali)
    st.markdown(kalimat)
