import streamlit as st
from auth import create_user_table, register_user, login_user
from db import add_transaction, get_transactions, get_total_by_category, get_monthly_totals
import matplotlib.pyplot as plt
from pdfreports import send_email, generate_pdf_report

create_user_table()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

st.title("💰 Kişisel Finans Takip Uygulaması")

menu = st.sidebar.selectbox("Menü", [
    "🔐 Giriş Yap", 
    "📝 Kayıt Ol",
    "➕ Kayıt Ekle",
    "📋 Özet Görüntüle",
    "📊 Grafikler",
    "📤 Rapor Al ve Gönder",
    "🚪 Çıkış Yap"
])

#Giriş yapmamış kullanıcı
if not st.session_state.logged_in:

    if menu == "🔐 Giriş Yap":
        st.subheader("🔐 Giriş Yap")
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        if st.button("Giriş"):
            if login_user(username, password):
                st.success(f"Hoş geldin {username}!")
                st.session_state.logged_in = True
                st.session_state.username = username
            else:
                st.error("Hatalı kullanıcı adı veya şifre.")

    elif menu == "📝 Kayıt Ol":
        st.subheader("📝 Kayıt Ol")
        new_user = st.text_input("Yeni Kullanıcı Adı")
        new_password = st.text_input("Yeni Şifre", type="password")
        if st.button("Kayıt Ol"):
            if register_user(new_user, new_password):
                st.success("Kayıt başarılı! Giriş yapabilirsiniz.")
            else:
                st.warning("Bu kullanıcı adı zaten kayıtlı.")


#Giriş yapmış kullanıcı
else:
    st.success(f"Giriş yapıldı: {st.session_state.username}")

     #Kayıt ekleme bölümü
    if menu == "➕ Kayıt Ekle":
        st.header("➕ Yeni Gelir/Gider Ekle")

        islem_tipi = st.radio("İşlem Tipi", ["Gelir", "Gider"], horizontal=True)
        kategori = st.selectbox("Kategori", ["Maaş", "Market", "Fatura", "Kira", "Ulaşım", "Diğer"])
        tutar = st.number_input("Tutar (₺)", min_value= 0.0, format= "%.2f")
        aciklama = st.text_input("Açıklama (isteğe bağlı)")

        if st.button("Kaydet"):
            add_transaction(st.session_state.username, islem_tipi, kategori, tutar, aciklama)
            st.success("İşlem Kaydedildi.")

    #Harcamalar özeti görüntüleme bölümü
    elif menu == "📋 Özet Görüntüle":
        st.header("📋 Kayıtlarım")
        df = get_transactions(st.session_state.username)
        st.dataframe(df)

    #Grafikler bölümü
    elif menu == "📊 Grafikler":
        st.subheader("📊 Harcama Analizi")

        with st.expander("📌 Kategori Bazlı Gider Dağılımı"):
            cat_data = get_total_by_category(st.session_state.username)
            if not cat_data.empty:
                fig1, ax1 = plt.subplots()
                ax1.pie(cat_data, labels= cat_data.index, autopct= '%1.1f%%', startangle= 90)
                ax1.axis('equal')
                st.pyplot(fig1)
            else:
                st.info("Henüz gider verisi yok.")

        with st.expander("📅 Aylık Gelir-Gider Toplamları"):
            monthly_data = get_monthly_totals(st.session_state.username)
            if not monthly_data.empty:
                fig2, ax2 = plt.subplots()
                monthly_data.plot(kind= 'bar', ax = ax2)
                plt.xticks(rotation= 45)
                st.pyplot(fig2)
            else:
                st.info("Henüz veri yok.")
    
    #Rapor Al ve Gönder bölümü
    elif menu == "📤 Rapor Al ve Gönder":
        st.subheader("📤 Raporu PDF olarak e-posta ile gönder")
    
        df = get_transactions(st.session_state.username)
        if df.empty:
            st.warning("Hiç kaydınız yok, rapor oluşturulamaz.")
        else:
            kategoriler_toplam = get_total_by_category(st.session_state.username)
            aylik_toplam = get_monthly_totals(st.session_state.username)

            email = st.text_input("E-posta adresinizi giriniz:")
            if st.button("Raporu Gönder"):
                pdf_buffer = generate_pdf_report(st.session_state.username, df, kategoriler_toplam, aylik_toplam)
                try:
                    send_email(email, pdf_buffer, st.session_state.username)
                    st.success("Rapor başarıyla gönderildi!")
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")

    elif menu == "🚪 Çıkış Yap":
        st.subheader("😋 Görüşmek Üzere")
        if st.button("🚪 Çıkış Yap"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.success(f"Başarıyla çıkış yaptınız!")
