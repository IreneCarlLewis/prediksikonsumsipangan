import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from utils import (NAMA_PANGAN, PERIODE, SATUAN, TARGET, baca_metrik_per_cluster, gaya_grafik,
                   nama_kelompok, penjelasan_kelompok_wilayah, tinggi_tabel)

with st.container(key="kepala_beranda"):
    st.title("Evaluasi Kinerja Model")
with st.container(border=True, key="kartu_tujuan"):
    st.markdown("Halaman ini menunjukkan **seberapa dekat hasil prediksi dengan data sebenarnya** "
                "sehingga pengguna dapat menilai seberapa jauh hasil prediksi dapat dipercaya.")
    st.caption("Nilai pada halaman ini diperoleh dengan menguji model pada kabupaten/kota yang tidak "
               "dipakai saat model belajar. Random Forest adalah model yang dipakai di aplikasi, "
               "sedangkan Regresi Linear Berganda adalah model sederhana sebagai pembanding.")

with st.container(border=True, key="kartu_evaluasi"):
    metrik = baca_metrik_per_cluster()

    # Pilih kelompok pangan dan kelompok wilayah
    kiri, kanan = st.columns(2) # membuat dropdown agar tampil sejajar
    klaster = kiri.selectbox("Kelompok Wilayah", sorted(metrik["cluster"].unique()),format_func=nama_kelompok)
    target = kanan.selectbox("Kelompok Pangan", TARGET, format_func=lambda t: NAMA_PANGAN[t])

    # saring tabel metrik agr menyisakan baris sesuai cluster terpilih
    bagian = metrik[metrik["cluster"] == klaster] 
    penjelasan_kelompok_wilayah()

    # Metrik untuk pangan terpilih 
    for kode_model, judul in [("RF", "Random Forest Regression"), ("RLB", "Regresi Linear Berganda")]:
        baris = bagian[(bagian["target"] == target) & (bagian["model"] == kode_model)].iloc[0]
        st.markdown(f"**{judul}**")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("RMSE", f"{baris['RMSE']:.3f}", border=True)
        k2.metric("MSE", f"{baris['MSE']:.3f}", border=True)
        k3.metric("MAE", f"{baris['MAE']:.3f}", border=True)
        k4.metric("R²", f"{baris['R2']:.2f}", border=True)

    rf = bagian[(bagian["target"] == target) & (bagian["model"] == "RF")].iloc[0]
    rlb = bagian[(bagian["target"] == target) & (bagian["model"] == "RLB")].iloc[0]
    pangan = NAMA_PANGAN[target]
    if rf["R2"] <= 0:
        kalimat = (f"Untuk kelompok pangan {pangan} di {nama_kelompok(klaster)}, nilai R² Random Forest "
                    f"tidak lebih dari 0, artinya model belum mampu memprediksi kelompok pangan ini "
                    f"dengan baik. Hasil prediksinya perlu dibaca dengan hati-hati.")
    else:
        kalimat = (f"Untuk kelompok pangan {pangan} di {nama_kelompok(klaster)}, Random Forest mampu "
                    f"menjelaskan sekitar {rf['R2'] * 100:.0f}% perbedaan konsumsi antarwilayah, dengan "
                    f"selisih prediksi rata-rata (MAE) sekitar {rf['MAE']:.3f} {SATUAN[target]} {PERIODE}. ")
        if rf["R2"] > rlb["R2"]:
                kalimat += f"Hasil ini lebih baik daripada Regresi Linear Berganda (R² {rlb['R2']:.2f})."
        else:
                kalimat += f"Hasil ini belum lebih baik daripada Regresi Linear Berganda (R² {rlb['R2']:.2f})."
        st.info(kalimat)

# Tabel 12 pangan: R² dan RMSE RF vs RLB 
with st.container(border=True, key="kartu_tabel"):
    lebar = bagian.pivot_table(index="target", columns="model", values=["R2", "RMSE"])
    lebar = lebar.reindex(TARGET)                                  # urutan pangan tetap
    tabel = {
        "Kelompok Pangan": [NAMA_PANGAN[t] for t in TARGET],
        "R² RF": lebar[("R2", "RF")].values,
        "R² RLB": lebar[("R2", "RLB")].values,
        "RMSE RF": lebar[("RMSE", "RF")].values,
        "RMSE RLB": lebar[("RMSE", "RLB")].values,
    }
    st.dataframe(tabel, hide_index=True, width="stretch", height=tinggi_tabel(len(TARGET)),
                 column_config={"R² RF": st.column_config.NumberColumn(format="%.2f"),"R² RLB": st.column_config.NumberColumn(format="%.2f"),"RMSE RF": st.column_config.NumberColumn(format="%.3f"),"RMSE RLB": st.column_config.NumberColumn(format="%.3f")})

# Grafik R² RF vs RLB 
with st.container(border=True, key="grafik"):
    posisi = np.arange(len(TARGET))                                # posisi baris 0..11
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.barh(posisi - 0.18, tabel["R² RF"], height=0.36, color="#3B4556", label="Random Forest")
    ax.barh(posisi + 0.18, tabel["R² RLB"], height=0.36, color="#BCC3CE", label="Regresi Linear Berganda")
    ax.set_yticks(posisi, tabel["Kelompok Pangan"])
    ax.invert_yaxis()                                              # pangan pertama di atas
    ax.axvline(0, color="#374151", linewidth=0.8)                  # garis nol
    ax.set_xlabel("R²")
    ax.set_title(f"R² Random Forest vs Regresi Linear Berganda — {nama_kelompok(klaster)}")
    ax.legend(loc="lower right", fontsize=7)
    gaya_grafik(ax)
    st.pyplot(fig)
    plt.close(fig)

# cara baca evaluasi kinerja model
with st.expander("Cara membaca:", expanded=True):
        st.markdown(
        "Grafik di atas membandingkan R² kedua model untuk 12 kelompok pangan. Batang yang lebih "
        "panjang berarti prediksi lebih baik.\n\n"
        "**RMSE** menunjukkan besar kesalahan prediksi rata-rata dalam satuan konsumsi. RMSE lebih "
        "sensitif terhadap kesalahan prediksi yang besar karena eror yang dikuadratkan. "
        "**Makin kecil nilainya, makin baik.**\n\n"
        "**MSE** adalah rata-rata kuadrat selisih antara prediksi dan nilai sebenarnya. Karena "
        "dikuadratkan, satuannya ikut menjadi kuadrat sehingga lebih mudah dibaca melalui RMSE "
        "(akar dari MSE). **Makin kecil nilainya, makin baik.**\n\n"
        "**MAE** adalah rata-rata selisih mutlak antara prediksi dan nilai sebenarnya, dalam satuan "
        "konsumsi. **Makin kecil nilainya, makin baik.**\n\n"
        "**R²** menunjukkan seberapa besar variasi konsumsi antarwilayah yang dapat dijelaskan "
        "model. Nilai 1 berarti prediksi sempurna, nilai 0 berarti model tidak lebih baik daripada "
        "selalu menebak nilai rata-rata, dan nilai negatif berarti model lebih buruk daripada "
        "menebak nilai rata-rata."
    )
