# sinema_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # --- 1. KULLANICI ARAYÜZLERİ (HTML SAYFALARI) ---
    path('', views.index_view, name='index'),                     # Ana sayfa: film listesi / yönlendirmeler
    path('login/', views.login_view, name='login'),               # Kullanıcı giriş ekranı (HTML formu)
    path('gise/', views.gise_view, name='gise'),                  # Gişe ekranı: film seçimi + koltuk seçimi
    path('sepet/', views.sepet_view, name='sepet'),               # Sepet görüntüleme ve ödeme sayfası
    path('satis_test/', views.bilet_satis_form_view, name='satis_test'),  # Test amaçlı bilet satış formu
    
    # --- 2. ÜYELİK VE OTURUM İŞLEMLERİ ---
    path('kayit-ol/', views.kayit_ol_view, name='kayit_ol'),      # Kullanıcı kayıt formundan gelen veriyi SQL'e kaydeder
    path('login-yap/', views.login_yap_view, name='login_yap'),   # Giriş işlemi: e-posta + şifre kontrolü
    
    # --- 3. ÖDEME ---
    path('odeme-yap/', views.odeme_yap_view, name='odeme_yap'),   # Kullanıcının sepetindeki ürünler için ödeme işlemi
    
    # --- 4. API ENDPOINT'LERİ ---
    path('api/', views.api_index_view, name='api_index'),  # API ana sayfası (dökümantasyon gibi)
    path('api/filmler/vizyon/', views.harici_film_listesi_api_view, name='api_harici_filmler'),  
    # Harici bir kaynaktan vizyondaki filmleri listeleyen endpoint
    
    # --- STORED PROCEDURE (SP) ÇAĞRILARI ---
    path('api/satis/', views.sp_bilet_satisi_api_view, name='api_sp_bilet_satis'),  # SP kullanarak bilet satışı
    path('api/seanslar/aktif/', views.sp_aktif_seanslari_getir_api_view, name='api_sp_aktif_seanslar'),  # Aktif seanslar
    path('api/hasilat/<int:film_id>/', views.sp_film_hasilatini_hesapla_api_view, name='api_sp_film_hasilat'),  
    # Bir filmin toplam hasılatını hesaplayan SP
    
    path('api/biletlerim/<int:kullanici_id>/', views.sp_kullanici_biletleri_api_view, name='api_sp_kullanici_biletleri'),  
    # Kullanıcının satın aldığı biletleri döner
    
    path('api/kapasite/<int:seans_id>/', views.sp_kapasite_kontrol_api_view, name='api_sp_kapasite_kontrol'),  
    # Bir seansın doluluk / kapasite bilgisini kontrol eden SP
    
    # --- VIEW (VW) KULLANIMLARI ---
    path('api/view/aktif/', views.vw_aktif_seanslar_api_view, name='api_vw_aktif_seanslar'),  
    # SQL View üzerinden aktif seansları getirir
    
    # --- FUNCTION (FN) KULLANIMLARI ---
    path('api/fn/vizyon/<int:film_id>/', views.fn_vizyon_suresi_api_view, name='api_fn_vizyon_suresi'),  
    # SQL Function: filmin vizyonda kalma süresini hesaplar
    
    path('api/fn/gelir/<int:senas_id>/', views.fn_potansiyel_gelir_api_view, name='api_fn_potansiyel_gelir'),  
    # SQL Function: bir seansın potansiyel gelirini hesaplar
    
    path('api/fn/tamad/<int:kullanici_id>/', views.fn_tam_adi_getir_api_view, name='api_fn_tam_adi'),  
    # SQL Function: kullanıcının tam adını döner
    
    # --- OTURUMU KAPATMA ---
    path('cikis-yap/', views.cikis_yap_view, name='cikis_yap'),   # Kullanıcının çıkış yapmasını sağlar
]
