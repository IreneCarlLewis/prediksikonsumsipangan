import streamlit as st

st.set_page_config(page_title="Prediksi Konsumsi Pangan", layout="wide")

beranda = st.Page("halaman/beranda.py", title="Beranda", icon=":material/home:", default=True)
simulasi = st.Page("halaman/simulasi.py", title="Simulasi Prediksi", icon=":material/tune:")
lokal = st.Page("halaman/interpretasi_lokal.py", title="Interpretasi Lokal",
                icon=":material/search_insights:")
evaluasi = st.Page("halaman/evaluasi.py", title="Evaluasi Kinerja Model",
                   icon=":material/fact_check:")
global_ = st.Page("halaman/interpretasi_global.py", title="Interpretasi Global",
                  icon=":material/bar_chart:")
semua_halaman = [beranda, simulasi, lokal, evaluasi, global_]

halaman_aktif = st.navigation(semua_halaman, position="hidden")

# ---------- Sidebar: identitas aplikasi, menu, dan info data ----------
with st.sidebar:
    st.markdown("# :material/eco: Prediksi Konsumsi Pangan")
    st.divider()
    for halaman in semua_halaman:
        if halaman.title == halaman_aktif.title:
            with st.container(key="menu_aktif"):
                st.page_link(halaman)
        else:
            st.page_link(halaman)
    st.divider()
    # with st.container(border=True, key="sidebar_info"):
    #     st.markdown("**:material/database: Sumber data**")
    #     st.caption("BPS, 514 kabupaten/kota, tahun 2022–2025")

st.html("""
<style>
/* ===== 1. Animasi muncul saat pindah halaman ===== */
@keyframes muncul { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
[data-testid="stMain"] [data-testid="stElementContainer"] { animation: muncul 0.4s ease-out; }

/* ===== 2. Jarak atas halaman ===== */
[data-testid="stMainBlockContainer"] { padding-top: 4.5rem; }

/* ===== 3. Form, kotak lipat, dan kartu ===== */
[data-testid="stForm"], [data-testid="stExpander"] details, [class*="st-key-kartu"] {
    background-color: #FCF9F3;
    box-shadow: 0 1px 3px rgba(46, 35, 24, 0.08);
}
[class*="st-key-kartu"] {
    border: 1px solid #E6D6BC;
    border-top: 4px solid #C19966;
    box-shadow: 0 4px 14px rgba(46, 35, 24, 0.10);
    padding: 1.2rem 1.4rem;
    border-radius: 1.3rem;
    overflow: hidden;
}

/* ===== 4. Kartu kecil (langkah contoh penggunaan) ===== */
[class*="st-key-langkah"] {
    background-color: #F3E6D0;
    border: 1px solid #E0BD8A;
    border-left: 5px solid #C19966;
    border-radius: 0.9rem;
    padding: 1rem 1.1rem;
}

/* ===== 5. Sidebar: kartu sumber data dan menu yang sedang dibuka ===== */
[class*="st-key-sidebar_info"] { background-color: #FBF6EC; }
[class*="st-key-menu_aktif"] [data-testid="stPageLink-NavLink"] { background-color: #C19966; }
[class*="st-key-menu_aktif"] [data-testid="stPageLink-NavLink"] * { color: #FFFFFF !important; font-weight: 600; }

/* ===== 6. Kepala halaman (kotak cokelat muda bergradasi) ===== */
[class*="st-key-kepala"] {
    background: linear-gradient(135deg, #C19966 0%, #E0BD8A 100%);
    border-radius: 0.9rem;
    padding: 1.6rem 2rem;
    box-shadow: 0 6px 18px rgba(193, 153, 102, 0.30);
}
[class*="st-key-kepala"] * { color: #2E2318 !important; }

/* ===== 7. Tombol di kepala halaman ===== */
[class*="st-key-kepala"] [data-testid="stBaseButton-secondary"] {
    background-color: #FFFFFF;
    border: none;
}
[class*="st-key-kepala"] [data-testid="stBaseButton-secondary"] * {
    color: #77542E !important;
    font-weight: 600;
}
[class*="st-key-kepala"] [data-testid="stBaseButton-secondary"]:hover {
    background-color: #F7EEDF;
}

/* ===== 8. Daftar proses dan daftar faktor (expander) di Beranda ===== */
[class*="st-key-proses"] details { background-color: #FFFFFF; box-shadow: none; border: none; }
[class*="st-key-proses"] summary { padding: 0.6rem 0.3rem; }
[class*="st-key-proses"] summary > span { display: flex; align-items: center; gap: 1rem; width: 100%; }

/* Kotak ikon di kiri */
[class*="st-key-proses"] summary > span > span:first-child {
    width: 52px; height: 52px; border-radius: 0.9rem; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
}
[class*="st-key-proses_0"] summary > span > span:first-child { background-color: #F6E3C8; }
[class*="st-key-proses_1"] summary > span > span:first-child { background-color: #FBE4D8; }
[class*="st-key-proses_2"] summary > span > span:first-child { background-color: #EDE3CF; }
[class*="st-key-proses_3"] summary > span > span:first-child { background-color: #F8EBD3; }
[class*="st-key-proses_faktor_0"] summary > span > span:first-child { background-color: #F6E3C8; }
[class*="st-key-proses_faktor_1"] summary > span > span:first-child { background-color: #FBE4D8; }
[class*="st-key-proses_faktor_2"] summary > span > span:first-child { background-color: #EDE3CF; }
[class*="st-key-proses_faktor_3"] summary > span > span:first-child { background-color: #F8EBD3; }

/* Ikon kiri tidak berubah saat kursor diarahkan */
[class*="st-key-proses"] summary > span > span:first-child > span { display: none; }
[class*="st-key-proses"] summary > span > span:first-child::before {
    font-family: "Material Symbols Rounded"; font-size: 26px; color: #77542E;
}
[class*="st-key-proses_0"] summary > span > span:first-child::before { content: "edit_note"; }
[class*="st-key-proses_1"] summary > span > span:first-child::before { content: "hub"; }
[class*="st-key-proses_2"] summary > span > span:first-child::before { content: "forest"; }
[class*="st-key-proses_3"] summary > span > span:first-child::before { content: "insights"; }
[class*="st-key-proses_faktor_0"] summary > span > span:first-child::before { content: "groups"; }
[class*="st-key-proses_faktor_1"] summary > span > span:first-child::before { content: "school"; }
[class*="st-key-proses_faktor_2"] summary > span > span:first-child::before { content: "payments"; }
[class*="st-key-proses_faktor_3"] summary > span > span:first-child::before { content: "work"; }

/* Panah di kanan */
[class*="st-key-proses"] summary > span::after {
    content: "expand_more";
    font-family: "Material Symbols Rounded";
    font-size: 22px; margin-left: auto;
    background-color: #F5EEE2; border-radius: 0.6rem; padding: 0.25rem;
    transition: transform 0.2s;
}
[class*="st-key-proses"] details[open] summary > span::after { transform: rotate(180deg); }

/* Judul dan keterangan kecil */
[class*="st-key-proses"] summary p { margin: 0; line-height: 1.5; color: #8C7B68; font-size: 0.92rem; }
[class*="st-key-proses"] summary strong { color: #2E2318; font-size: 1.08rem; }
[class*="st-key-proses"] [data-testid="stExpanderDetails"] { padding-left: 4.6rem; }
</style>
""")

halaman_aktif.run()