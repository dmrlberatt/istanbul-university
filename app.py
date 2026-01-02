import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# SAYFA AYARLARI & TASARIM (MOBİL ODAKLI)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ÜniAsistan",
    page_icon="🎓",
    layout="centered",  # Mobilde daha derli toplu görünmesi için
    initial_sidebar_state="collapsed"
)

# Özel CSS: Mobilde butonları büyütmek ve boşlukları ayarlamak için
st.markdown("""
<style>
    /* Tab başlıklarını büyüt */
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 2px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b;
        color: white;
    }
    /* Kart görünümü için stil */
    div.stContainer {
        border: 1px solid #e6e6e6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. VERİ İŞLEME VE YÜKLEME
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        # Excel dosyasını oku. Header 3. satırda (index 2).
        # Tüm verileri string (metin) olarak okuyoruz ki tarih formatı bozulmasın.
        df = pd.read_excel(
            "2025-2026-guz-final-sinav-programi.xlsx", 
            header=2, 
            dtype=str
        )
        
        # Sütun isimlerindeki boşlukları temizleyelim (garanti olsun)
        df.columns = df.columns.str.strip()
        
        # ÖNEMLİ: Merged Cells (Birleştirilmiş Hücreler) Çözümü
        # 'Bölüm' sütunundaki boş (NaN) değerleri bir üst satırdan dolduruyoruz.
        df['Bölüm'] = df['Bölüm'].ffill()
        
        # Gereksiz boş satırları temizle (Ders Kodu olmayan satırlar gibi)
        df = df.dropna(subset=['Dersin Kodu'])
        
        return df
    except FileNotFoundError:
        st.error("Veri dosyası (Excel) bulunamadı. Lütfen dosya ismini kontrol et.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
        return pd.DataFrame()

# Veriyi yükle
df = load_data()

# -----------------------------------------------------------------------------
# OTURUM YÖNETİMİ (SESSION STATE)
# -----------------------------------------------------------------------------
# Kullanıcının eklediği sınavları hafızada tutmak için
if 'my_exams' not in st.session_state:
    st.session_state.my_exams = []

def add_exam(exam_row):
    # Çift eklemeyi engellemek için kontrol
    exam_code = exam_row['Dersin Kodu']
    if not any(d['Dersin Kodu'] == exam_code for d in st.session_state.my_exams):
        st.session_state.my_exams.append(exam_row)
        st.toast(f"{exam_row['Dersin Adı']} listene eklendi!", icon="✅")
    else:
        st.toast("Bu ders zaten listende var.", icon="ℹ️")

def remove_exam(exam_code):
    st.session_state.my_exams = [d for d in st.session_state.my_exams if d['Dersin Kodu'] != exam_code]
    st.rerun() # Listeyi anında güncellemek için sayfayı yenile

# -----------------------------------------------------------------------------
# DUMMY VERİ FONKSİYONLARI
# -----------------------------------------------------------------------------
def get_yemek_listesi():
    return [
        {"gun": "Pazartesi", "ana": "Mercimek Çorbası", "ara": "Tavuk Sote", "tatli": "Sütlaç", "cal": "850 kcal"},
        {"gun": "Salı", "ana": "Ezogelin", "ara": "Karnıyarık", "tatli": "Meyve", "cal": "920 kcal"},
        {"gun": "Çarşamba", "ana": "Domates Çorbası", "ara": "Izgara Köfte", "tatli": "Baklava", "cal": "1050 kcal"},
    ]

def get_duyurular():
    return [
        {"baslik": "Final Sınavları Hakkında", "tarih": "02.01.2026", "metin": "Sınav giriş yerleri OBS üzerinden ilan edilmiştir."},
        {"baslik": "Kütüphane Çalışma Saatleri", "tarih": "01.01.2026", "metin": "Final haftası boyunca kütüphanemiz 7/24 açıktır."},
        {"baslik": "Bahar Yarıyılı Kayıtları", "tarih": "28.12.2025", "metin": "Kayıt yenileme işlemleri Şubat ayında başlayacaktır."},
    ]

def get_etkinlikler():
    return [
        {"kulup": "Yazılım Kulübü", "etkinlik": "Python Workshop", "yer": "Mühendislik B Blok", "zaman": "10 Ocak, 14:00"},
        {"kulup": "Tiyatro Topluluğu", "etkinlik": "Yıl Sonu Gösterisi", "yer": "Kültür Merkezi", "zaman": "15 Ocak, 19:00"},
    ]

# -----------------------------------------------------------------------------
# ANA ARAYÜZ (TABS)
# -----------------------------------------------------------------------------
st.title("📱 Kampüs Asistanı")

# Sekmelerin oluşturulması
tab1, tab2, tab3, tab4 = st.tabs(["📝 Sınavlar", "🍽️ Yemek", "📢 Duyuru", "🎉 Etkinlik"])

# --- TAB 1: SINAVLAR & LİSTEM ---
with tab1:
    st.subheader("Sınav Programı")
    
    if not df.empty:
        # Bölüm Seçimi
        bolumler = df['Bölüm'].unique()
        secilen_bolum = st.selectbox("Bölümünü Seç:", bolumler)
        
        # Seçilen bölüme göre filtrele
        filtered_df = df[df['Bölüm'] == secilen_bolum]
        
        # Ders Arama
        arama_metni = st.text_input("Ders Ara (Ad veya Kod):", "")
        if arama_metni:
            filtered_df = filtered_df[
                filtered_df['Dersin Adı'].str.contains(arama_metni, case=False, na=False) |
                filtered_df['Dersin Kodu'].str.contains(arama_metni, case=False, na=False)
            ]
        
        st.markdown("---")
        
        # Liste Görünümü (Mobil Uyumlu Kartlar)
        st.caption(f"{len(filtered_df)} ders bulundu.")
        
        for index, row in filtered_df.iterrows():
            with st.container():
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{row['Dersin Adı']}**")
                    st.caption(f"📅 {row['Gün']} | ⏰ {row['Saat']}")
                    st.caption(f"📍 {row['Ders Yeri']}")
                with c2:
                    # Buton için benzersiz key kullanımı şarttır
                    if st.button("➕", key=f"add_{index}", help="Listeme Ekle"):
                        add_exam(row)

    st.markdown("---")
    st.subheader("📌 Sınavlarım")
    
    if len(st.session_state.my_exams) > 0:
        for item in st.session_state.my_exams:
             with st.container():
                st.info(f"**{item['Dersin Adı']}**\n\n📅 {item['Gün']} - ⏰ {item['Saat']} - 📍 {item['Ders Yeri']}")
                if st.button("Kaldır", key=f"del_{item['Dersin Kodu']}"):
                    remove_exam(item['Dersin Kodu'])
    else:
        st.write("Henüz bir sınav eklemedin.")

# --- TAB 2: YEMEKHANE ---
with tab2:
    st.header("Yemek Listesi")
    yemekler = get_yemek_listesi()
    
    for yemek in yemekler:
        with st.container():
            st.markdown(f"### {yemek['gun']}")
            st.write(f"🍲 **Ana Yemek:** {yemek['ana']}")
            st.write(f"🥗 **Yan:** {yemek['ara']}")
            st.write(f"🍰 **Tatlı:** {yemek['tatli']}")
            st.caption(f"🔥 {yemek['cal']}")
            st.divider()

# --- TAB 3: DUYURULAR ---
with tab3:
    st.header("Güncel Duyurular")
    duyurular = get_duyurular()
    
    for duyuru in duyurular:
        with st.expander(f"📢 {duyuru['baslik']} ({duyuru['tarih']})", expanded=True):
            st.write(duyuru['metin'])

# --- TAB 4: ETKİNLİKLER ---
with tab4:
    st.header("Kulüp Etkinlikleri")
    etkinlikler = get_etkinlikler()
    
    for etk in etkinlikler:
        st.success(f"**{etk['kulup']}** sunar:")
        st.write(f"🎭 {etk['etkinlik']}")
        st.write(f"📍 {etk['yer']} | ⏰ {etk['zaman']}")
        st.divider()
