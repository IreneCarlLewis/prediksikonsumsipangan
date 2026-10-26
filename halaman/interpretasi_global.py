import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from utils import (NAMA_FAKTOR_AWAM, NAMA_FITUR, NAMA_FITUR_LENGKAP, NAMA_PANGAN, TARGET,
                   URUTAN_FAKTOR, WARNA_FAKTOR, angka_id, baca_shap_global, gabung, gaya_grafik,
                   nama_kelompok, penjelasan_kelompok_wilayah)
with st.container(key="kepala_beranda"):
    st.title("Interpretasi Global")
with st.container(border=True, key="kartu_global"):
    st.markdown("Halaman ini menjawab pertanyaan **faktor apa yang paling berpengaruh terhadap "
                "konsumsi suatu kelompok pangan?** Berbeda dengan Interpretasi Lokal yang menjelaskan "
                "satu hasil prediksi, halaman ini merangkum pengaruh setiap faktor untuk seluruh "
                "kabupaten/kota dalam satu kelompok wilayah.")

shap_global = baca_shap_global()

# Pilihan 
with st.container(border=True, key="kartu_grafikglobal"):
    kiri, kanan = st.columns(2)
    klaster = kiri.selectbox("Kelompok Wilayah", sorted(shap_global["cluster"].unique()), format_func=nama_kelompok)
    target = kanan.selectbox("Kelompok Pangan", TARGET, format_func=lambda t: NAMA_PANGAN[t])
    bagian = shap_global[shap_global["cluster"] == klaster]
    penjelasan_kelompok_wilayah()

    # Legenda warna faktor (kotak kecil berwarna + nama) 
    legenda = "&nbsp;&nbsp;&nbsp;".join(
        f"<span style='display:inline-block;width:14px;height:9px;background:{WARNA_FAKTOR[f]};"
        f"margin-right:5px'></span>{NAMA_FITUR_LENGKAP[f]}" for f in URUTAN_FAKTOR)
    st.markdown(f"<div style='text-align:center;font-size:12px'>{legenda}</div>", unsafe_allow_html=True)

    # Grafik 1: peringkat rata-rata |SHAP| untuk pangan terpilih
    pangan = NAMA_PANGAN[target]
    satu = bagian[bagian["target"] == target].sort_values("nilai_rata2_shap") # terkecil di bawah
    st.subheader(f"Peringkat kontribusi faktor – {pangan}")

    fig, ax = plt.subplots(figsize=(6.5, 2.6))
    batang = ax.barh([NAMA_FITUR_LENGKAP[f] for f in satu["fitur"]], satu["nilai_rata2_shap"], color=[WARNA_FAKTOR[f] for f in satu["fitur"]], height=0.6)
    ax.bar_label(batang, labels=[f"{v:.4f}" for v in satu["nilai_rata2_shap"]], padding=3, fontsize=7)
    ax.set_xlim(0, satu["nilai_rata2_shap"].max() * 1.3) # ruang untuk label angka
    ax.set_xlabel("Rata-rata |nilai SHAP|")
    gaya_grafik(ax)
    st.pyplot(fig)
    plt.close(fig)

    # Kalimat otomatis (bahasa awam, Tahun tidak ikut diperingkat)
    urut = satu[satu["fitur"] != "Tahun"].sort_values("nilai_rata2_shap", ascending=False)
    pertama, kedua, terakhir = urut.iloc[0], urut.iloc[1], urut.iloc[-1]
    tahun = satu[satu["fitur"] == "Tahun"].iloc[0]
    nama_pangan = pangan.lower()
    kalimat = (f"Di {nama_kelompok(klaster)}, faktor yang **paling berpengaruh** terhadap konsumsi "
               f"{nama_pangan} adalah **{NAMA_FAKTOR_AWAM[pertama['fitur']]}**, disusul "
               f"{NAMA_FAKTOR_AWAM[kedua['fitur']]}.")
    rasio = pertama["nilai_rata2_shap"] / kedua["nilai_rata2_shap"]
    if rasio >= 1.5:
        kalimat += (f"Pengaruhnya sekitar {angka_id(rasio, 1)} kali lebih besar daripada "
                    f"{NAMA_FAKTOR_AWAM[kedua['fitur']]}. ")
    kalimat += f"Faktor yang pengaruhnya paling kecil adalah {NAMA_FAKTOR_AWAM[terakhir['fitur']]}."
    if tahun["nilai_rata2_shap"] >= kedua["nilai_rata2_shap"]:
        kalimat += (f" Selain itu, perbedaan tahun (2022–2025) juga cukup berpengaruh, yang berarti "
                    f"konsumsi {nama_pangan} ikut berubah dari tahun ke tahun.")
    st.markdown(kalimat)
    st.caption("Panjang batang menunjukkan rata-rata besar pengaruh faktor (rata-rata nilai SHAP "
            "mutlak) dalam satuan kelompok pangan tersebut. Makin panjang, makin besar pengaruhnya. "
            "Grafik ini menunjukkan besar pengaruh, bukan arahnya (menaikkan atau menurunkan). Arah "
            "pengaruh untuk satu wilayah dapat dilihat di halaman Interpretasi Lokal.")

# Grafik 2: persentase kontribusi 12 pangan (batang bertumpuk 100%)
with st.container(border=True, key="kartu_tujuan"):
    st.subheader(f"Persentase kontribusi faktor pada 12 kelompok pangan – {nama_kelompok(klaster)}")
    persen = bagian.pivot_table(index="target", columns="fitur", values="shap_persen")
    persen = persen.reindex(TARGET)[URUTAN_FAKTOR] # urutan baris & kolom tetap

    posisi = np.arange(len(TARGET))
    fig, ax = plt.subplots(figsize=(6.5, 4.6))
    kiri_batang = np.zeros(len(TARGET)) # titik awal tiap segmen
    for f in URUTAN_FAKTOR:
        nilai = persen[f].values
        batang = ax.barh(posisi, nilai, left=kiri_batang, color=WARNA_FAKTOR[f], height=0.75)
        # Tulis persen di dalam segmen kalau cukup lebar (>= 8%)
        label = [f"{v:.0f}%" if v >= 8 else "" for v in nilai]
        ax.bar_label(batang, labels=label, label_type="center", fontsize=6.5,
                    color="white" if f == "Nilai_ipm" else "#1F2937")
        kiri_batang += nilai

    baris_pilih = TARGET.index(target) # sorot pangan yang dipilih
    ax.barh(baris_pilih, 100, height=0.75, fill=False, edgecolor="black", linewidth=1.2)
    ax.set_yticks(posisi, [NAMA_PANGAN[t] for t in TARGET])
    ax.get_yticklabels()[baris_pilih].set_fontweight("bold")
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Persentase kontribusi (%)")
    gaya_grafik(ax)
    ax.grid(False)
    st.pyplot(fig)
    plt.close(fig)

    # Narasi persentase kontribusi (bahasa awam)
    pilih = persen.loc[target].sort_values(ascending=False)    # 5 faktor pangan terpilih, besar ke kecil
    utama = pilih.index[0]   
    
    st.caption("Persentase dipakai agar jenis pangan dengan satuan berbeda (kg, butir, liter, gram) "
               "dapat dibandingkan. Perbedaan tahun bukan faktor sosial ekonomi, melainkan perubahan "
               "konsumsi dari tahun ke tahun yang tidak tercakup oleh keempat faktor.")

    st.caption("Setiap baris adalah satu kelompok pangan dengan total 100%. Warna menunjukkan faktor dengan makna "
               "makin lebar bagian suatu warna, makin besar pengaruh faktor tersebut pada kelompok "
               "pangan itu. Baris yang diberi bingkai hitam adalah kelompok pangan yang sedang dipilih.")                                  # faktor terbesar untuk pangan terpilih

    teks = ("**Cara membaca grafik:** setiap batang mewakili satu jenis pangan. Satu batang penuh "
            "bernilai 100%, lalu dibagi menurut besar kontribusi (sumbangan) setiap faktor terhadap "
            "perkiraan konsumsi. Makin lebar suatu warna, makin besar kontribusi faktor itu.\n\n")

    teks += f"Untuk **{nama_pangan}** (batang berbingkai hitam), pembagiannya:\n"
    for f, nilai in pilih.items():
        teks += f"- {NAMA_FAKTOR_AWAM[f]}: {nilai:.0f}%\n"
    if utama == "Tahun":
        teks += (f"\nArtinya, kontribusi terbesar berasal dari perbedaan tahun, yaitu perubahan "
                 f"konsumsi {nama_pangan} dari tahun ke tahun, bukan dari kondisi sosial ekonomi "
                 f"wilayah.\n\n")
    else:
        teks += (f"\nArtinya, {NAMA_FAKTOR_AWAM[utama]} memberi kontribusi terbesar pada perkiraan "
                 f"konsumsi {nama_pangan}.\n\n")

    juara = persen.idxmax(axis=1)                              # faktor terbesar di setiap pangan
    sering = juara.value_counts().index[0]                     # faktor yang paling sering terbesar
    jumlah = juara.value_counts().iloc[0]
    contoh = [NAMA_PANGAN[t].lower() for t in juara[juara == sering].index][:3]   # maks. 3 contoh
    if sering == "Tahun":
        teks += (f"Jika dilihat dari ke-12 jenis pangan, perbedaan tahun memberi kontribusi terbesar "
                 f"pada **{jumlah} dari 12 jenis pangan** (misalnya {gabung(contoh)}). Artinya, di "
                 f"{nama_kelompok(klaster)} konsumsi banyak jenis pangan lebih banyak berubah dari "
                 f"tahun ke tahun.")
    else:
        kata_juga = " juga" if sering == utama else ""
        teks += (f"Jika dilihat dari ke-12 jenis pangan, **{NAMA_FAKTOR_AWAM[sering]}**{kata_juga} "
                 f"memberi kontribusi terbesar pada **{jumlah} dari 12 jenis pangan** (misalnya "
                 f"{gabung(contoh)}). Jadi, di {nama_kelompok(klaster)}, {NAMA_FAKTOR_AWAM[sering]} "
                 f"adalah faktor yang paling sering memberi kontribusi terbesar terhadap perkiraan "
                 f"konsumsi pangan.")
    st.markdown(teks)
    # st.caption("Persentase digunakan agar kelompok pangan dengan satuan berbeda dapat dibandingkan.")
    # st.caption("Kontribusi Tahun menggambarkan perbedaan antartahun, bukan faktor sosial ekonomi.")