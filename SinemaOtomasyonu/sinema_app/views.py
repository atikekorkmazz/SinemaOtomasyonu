from django.shortcuts import redirect,render
from django.db import connection
from django.http import HttpResponse,JsonResponse
from .models import Film,Seans #gerekli modelleri import ettik
import datetime
import time
import requests #harici api için gerekli
#api için gerekli importlar
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import SeansDetaySerializer, KullaniciBiletSerializer
import json
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta

TMDB_API_KEY='928efd2b59dabaad02422db88a55f9a7'

#RAPORLAMA VE SAKLI YORDAM SONUCLARINI GORMEK ICIN FONKSIYON
def raporlama_view(query,params=None):
    #sql sorgusunu calistirir ve sonucu kolon isimleriyle birlikte sozluk listesi olarak dondurur
    with connection.cursor() as cursor:
        cursor.execute(query,params if params else [])
        #kolon isimlerini aliyoruz (salonAdi, FilmAdi vs)
        columns =[col[0] for col in cursor.description]
        #sonuclari listeye donusturur
        results=[dict(zip(columns,row))for row in cursor.fetchall()]
        return results
    

@api_view(['GET'])
def harici_film_listesi_api_view(request):
    #kullandigimiz apideki vizyondaki filmleri çeker
    url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=tr-TR&page=1"

    try:
        response = requests.get(url)
        response.raise_for_status() 
        data = response.json()
        
        #gerekli alanları alıyoruz
        filmler = [
            {
                'tmdb_id': film['id'],
                'ad': film['title'],
                'vizyon_tarihi': film['release_date'],
                'oy_ortalamasi': film['vote_average'],
                'poster_path': f"https://image.tmdb.org/t/p/w500{film['poster_path']}"
            }
            for film in data.get('results', [])
        ]
        
        return Response(filmler)
        
    except requests.RequestException as e:
        return Response({'hata': f"Harici API'ye erişilemiyor: {e}"}, status=503)

# sp - execute komutları

#sp1: sp_biletSatisi(input: SenasID,KoltukID,KullaniciID - output:sonuc)
@api_view(['POST'])
def sp_bilet_satisi_api_view(request):
    try:
        seans_id=request.data.get('seans_id')
        koltuk_id=request.data.get('koltuk_id')
        kullanici_id=request.data.get('kullanici_id')

        with connection.cursor() as cursor:
            cursor.execute(
                "EXEC sp_BiletSatisi @SeansID=%s, @KoltukID=%s, @KullaniciID=%s, @Sonuc=NULL OUTPUT",
                [seans_id,koltuk_id,kullanici_id if kullanici_id else None]
            )
        return Response ({"mesaj":"BAŞARILI: Bilet satışı tamamlandı. (TRG1 tetiklendi)",
                          "seans_id":seans_id, "koltuk_id":koltuk_id, "kullanici_id":kullanici_id},status=200)
    except Exception as e:
        return Response({"hata": f"Satış başarısız. Detay: {e}"},status=400)


#sp2: sp_AktifSeanslariGetir(inpur:Tarih) select yaptigi için listeleme viewi
@api_view(['GET'])
def sp_aktif_seanslari_getir_api_view(request):
    tarih_str=request.GET.get('tarih')
    if not tarih_str:
        tarih_str=datetime.date.today().strftime('%Y-%m-%d')

    try:
        query="EXEC sp_AktifSeanslariGetir @Tarih=%s"
        seanslar_veri=raporlama_view(query,[tarih_str])
        serializer=SeansDetaySerializer(seanslar_veri,many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'hata': f"Aktif seanslar alınamadı. Detay: {e}"},status=500)


#sp3: sp_FilmHasilatiniHesapla
@api_view(['GET'])
def sp_film_hasilatini_hesapla_api_view(request,film_id):
    try:
        with connection.cursor() as cursor:
            #output cekme yontemi
            cursor.execute(
                "DECLARE @H DECIMAL(10,2); EXEC sp_FilmHasilatiniHesapla @FilmID=%s, @ToplamHasılat=@H OUTPUT; SELECT @H AS ToplamHasılat;",
                [film_id]
            )
            hasilat=cursor.fetchone()[0]
        return Response({'film_id': film_id,'hasilat': hasilat,'birim': 'TL'},status=200)
    except Exception as e:
        return Response({'hata': f'Hata oluştu: {e}'},status=500)
    

#sp4: sp_KullaniciBiletleriniListele
@api_view(['GET'])
def sp_kullanici_biletleri_api_view(request,kullanici_id):
    try:
        query="EXEC sp_KullaniciBiletleriniListele @KullaniciID=%s"
        biletler_veri=raporlama_view(query, [kullanici_id])
        serializer=KullaniciBiletSerializer(biletler_veri,many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'hata': f"Biletler listelenemedi. Detay: {e}"},status=500)
    

#sp5: sp_SeansKapasiteKontrolu
@api_view(['GET'])
def sp_kapasite_kontrol_api_view(request,seans_id):
    try:
        with connection.cursor() as cursor:
            #output cekme yontemi
            cursor.execute(
                "DECLARE @Bos INT; EXEC sp_SeansKapasiteKontrolu @SenasID=%s, @BosKoltukSayisi=@Bos OUTPUT; SELECT @Bos AS BosKoltuk;",
                [seans_id]
            )
            bos_koltuk=cursor.fetchone()[0]
        return Response({'seans_id': seans_id, 'bos_koltuk_sayisi': bos_koltuk},status=200)
    except Exception as e:
        return Response({'hata': f'Hata oluştu: {e}'},status=500)


#fonksiyonlar ve view - api endpointleri

#view1: vw_AktifSeansDetaylari (get islemi)
@api_view(['GET'])
def vw_aktif_seanslar_api_view(request):
    try:
        query = "SELECT * FROM vw_AktifSeansDetaylari ORDER BY Tarih, Saat"
        seanslar_veri=raporlama_view(query)

        #wiew de kalanKoltukSayisi oldugu icin serializer da tanımlanmalıdır(serializer.py da tanımlamıştı)
        serializer=SeansDetaySerializer(seanslar_veri,many=True)

        return Response(serializer.data)
    except Exception as e:
        return Response({'hata': f"Aktif seans detayları alınamadı. Detay: {e}"},status=500)
    

#fn1: fn_VizyonSuresiHesapla (get islemi)
@api_view(['GET'])
def fn_vizyon_suresi_api_view(request,film_id):
    try: 
        #django orm ile filmi cekip vizyon tarihine ulasiyoruz
        film=Film.objects.get(pk=film_id)

        query="SELECT dbo.fn_ViztonSuresiHesapla(%s) AS GunFarki"
        with connection.cursor() as cursor:
            cursor.execute(query,[film.VizyonTarihi])
            gun_farki=cursor.fetchone()[0]
        return Response({
            'film_id': film_id,
            'film_adi': film.Ad,
            'gun_farki': gun_farki
        },status=200)
    
    except Film.DoesNotExist:
        return Response({'hata': 'Film MSSQL veritabanında bulunamadı.'},status=404)
    except Exception as e:
        return Response({'hata': f'Hata oluştu: {e}'},status=500)


#fn2: fn_TamAdiGetir (get islemi)
@api_view(['GET'])
def fn_tam_adi_getir_api_view(request,kullanici_id):
    try:
        query="SELECT dbo.fn_TamAdiGetir(%s) AS TamAd"

        with connection.cursor() as cursor:
            cursor.execute(query, [kullanici_id])
            tam_ad=cursor.fetchone()[0]
        return Response({'kullanici_id':kullanici_id, 'tam_ad': tam_ad},status=200)
        
    except Exception as e:
        return Response({'hata': f'Hata oluştu: {e}'},status=500)
    


#fn3: fn_PotansiyelGelirHesapla (get islemi)
@api_view(['GET'])
def fn_potansiyel_gelir_api_view(request,senas_id):
    try:
        query="SELECT dbo.fn_PotansiyelGelirHesapla(%s) AS Gelir"

        with connection.cursor() as cursor: 
            cursor.execute(query, [senas_id])
            gelir=cursor.fetchone()[0]

        return Response({'seans_id': senas_id, 'potansiyel_gelir': gelir, 'birim': 'TL'},status=200)
    
    except Exception as e:
        return Response({'hata': f'Hata oluştu: {e}'},status=500)
    



# ana giris noktasi
@api_view(['GET'])
def api_index_view(request):
    #tüm api endpoinlerine baglanti veren giris sayfasi(json)
    endpoints={
        'Ana Sayfa': '/api/',
        'Vizyondaki Filmler (TMDB)': '/api/filmler/vizyon/',
        'SP_AktifSeanslar (MSSQL)': '/api/seanslar/aktif/?tarih=YYYY-MM-DD',
        'SP_BiletSatışı (MSSQL)': '/api/satis/ (POST: seans_id, koltuk_id, kullanici_id)',
        'VW_AktifSeansDetayları (MSSQL)': '/api/view/aktif/',
        'FN_PotansiyelGelir (MSSQL)': '/api/fn/gelir/{seans_id}/',
        'SP_KullaniciBiletleri (MSSQL)': '/api/biletlerim/{kullanici_id}/',
    }
    return Response(endpoints)


def login_view(request):
    return render(request,'sinema_app/login.html')


# --- ARAYÜZ (HTML) VIEW FONKSİYONLARI ---

def index_view(request):
    # --- 1. OTOMATİK TARİH HESAPLAMA ---
    bugun = datetime.now()
    secilen_tarih_str = request.GET.get('tarih', bugun.strftime('%Y-%m-%d'))
    
    tarih_listesi = []
    gunler_tr = {'Monday':'Pazartesi','Tuesday':'Salı','Wednesday':'Çarşamba','Thursday':'Perşembe','Friday':'Cuma','Saturday':'Cumartesi','Sunday':'Pazar'}
    aylar_tr = {1:'Oca', 2:'Şub', 3:'Mar', 4:'Nis', 5:'May', 6:'Haz', 7:'Tem', 8:'Ağu', 9:'Eyl', 10:'Eki', 11:'Kas', 12:'Ara'}

    for i in range(4):
        yeni_tarih = bugun + timedelta(days=i)
        yeni_tarih_formatli = yeni_tarih.strftime('%Y-%m-%d')
        gun_adi_ing = yeni_tarih.strftime('%A')
        tarih_listesi.append({
            'gun_ay': f"{yeni_tarih.day} {aylar_tr[yeni_tarih.month]}",
            'gun_adi': gunler_tr[gun_adi_ing],
            'full_date': yeni_tarih_formatli,
            'is_active': yeni_tarih_formatli == secilen_tarih_str,
            'is_today': i == 0 
        })

    # --- 2. VERİTABANINDAN FİLTRELİ SEANSLARI ÇEKME ---
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.SeansID, f.Ad, f.Tur, f.Aciklama, s.Saat, s.Tarih, s.Fiyat, s.Dil, f.PosterPath 
            FROM Seans s 
            JOIN Film f ON s.FilmID = f.FilmID
            WHERE s.Tarih = %s
            ORDER BY f.Ad, s.Saat
        """, [secilen_tarih_str])
        seanslar = cursor.fetchall()
    
    base_url = "https://image.tmdb.org/t/p/w500"
    film_sozlugu = {}

    for s in seanslar:
        f_ad = s[1]
        if f_ad not in film_sozlugu:
            p_path = s[8] if s[8] else ""
            afis_url = p_path if p_path.startswith('http') else (base_url + p_path if p_path else "")
            film_sozlugu[f_ad] = {
                'ad': f_ad, 'tur': s[2], 'meta': f"{s[5]} | {s[6]} TL",
                'afis': afis_url, 'dublaj': [], 'altyazi': []
            }
        
        # Saat formatı HH:MM
        saat_str = s[4].strftime('%H:%M') if hasattr(s[4], 'strftime') else str(s[4])[:5]
        seans_verisi = {'id': s[0], 'saat': saat_str}
        
        # --- KRİTİK NOKTA: Dil Verisini Temizleme ---
        db_dil = str(s[7]).strip().upper() if s[7] else "DUBLAJLI"
        
        # Altyazılı mı Dublajlı mı? (İçinde 'ALT' geçiyorsa altyazı)
        if "ALT" in db_dil:
            hedef_liste = film_sozlugu[f_ad]['altyazi']
        else:
            hedef_liste = film_sozlugu[f_ad]['dublaj']
        
        # --- TEKİLLEŞTİRME ---
        if not any(item['saat'] == seans_verisi['saat'] for item in hedef_liste):
            hedef_liste.append(seans_verisi)

    return render(request, 'sinema_app/index.html', {
        'filmler': film_sozlugu.values(),
        'tarihler': tarih_listesi
    })

def gise_view(request):
    seans_id = request.GET.get('seans_id')
    
    if not seans_id:
        return redirect('/') # ID yoksa ana sayfaya at

    with connection.cursor() as cursor:
        # 1. Film, Tür ve Saat Bilgilerini Çek (Sepet için)
        cursor.execute("""
            SELECT f.Ad, f.Tur, s.Saat 
            FROM Seans s 
            JOIN Film f ON s.FilmID = f.FilmID 
            WHERE s.SeansID = %s
        """, [seans_id])
        bilgi = cursor.fetchone()
        
        # 2. Salondaki Tüm Koltukları Çek
        cursor.execute("""
            SELECT k.KoltukID, k.Sira, k.Numara 
            FROM Koltuk k 
            JOIN Seans s ON k.SalonID = s.SalonID 
            WHERE s.SeansID = %s
            ORDER BY k.Sira, k.Numara
        """, [seans_id])
        tum_koltuklar = cursor.fetchall()

        # 3. Satılmış (Dolu) Koltukları Çek
        # Not: Bilet tablonun adını ve SeansID sütununu kontrol et
        cursor.execute("""
            SELECT KoltukID FROM Bilet WHERE SeansID = %s
        """, [seans_id])
        dolu_koltuklar = [row[0] for row in cursor.fetchall()]

    # Verileri HTML'in anlayacağı JSON formatına çeviriyoruz
    context = {
        'seans_id': seans_id,
        'seans_bilgisi': {
            'FilmAd': bilgi[0] if bilgi else "Film Bulunamadı",
            'Tur': bilgi[1] if bilgi else "Tür Yok",
            'Saat': bilgi[2] if bilgi else "00:00"
        },
        'tum_koltuklar_json': json.dumps(tum_koltuklar),
        'dolu_koltuklar_json': json.dumps(dolu_koltuklar),
    }
    
    return render(request, 'sinema_app/gise.html', context)

def sepet_view(request):
    # Kullanıcı giriş yapmış mı kontrol et
    giris_yapti_mi = 'kullanici_id' in request.session
    return render(request, 'sinema_app/sepet.html', {'giris_yapti_mi': giris_yapti_mi})

def bilet_satis_form_view(request):
    """Bilet satış testi için kullanılan form sayfasını döndürür."""
    return render(request, 'sinema_app/api_test_form.html')


def api_filmleri_veritabanina_kaydet(request):
    TMDB_API_KEY = '928efd2b59dabaad02422db88a55f9a7'
    url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=tr-TR&page=1"
    
    try:
        response = requests.get(url)
        data = response.json()
        yeni_film_sayisi = 0

        for item in data.get('results', []):
            # Eğer film veritabanında zaten varsa tekrar ekleme (Ad kontrolü)
            if not Film.objects.filter(Ad=item['title']).exists():
                Film.objects.create(
                    Ad=item['title'],
                    Tur="Aksiyon/Macera", # TMDB tür id'lerini de çözebilirsin ama şimdilik sabit
                    Sure=120, # TMDB detay API'sinden çekilebilir, şimdilik 120
                    Aciklama=item['overview'][:500], # Açıklama çok uzunsa kes
                    VizyonTarihi=item['release_date']
                )
                yeni_film_sayisi += 1
        
        return HttpResponse(f"İşlem Başarılı! {yeni_film_sayisi} adet yeni film SSMS'e eklendi.")
    except Exception as e:
        return HttpResponse(f"Hata oluştu: {e}")
    

# 2. ÖDEME İŞLEMİ (Sepetteki biletleri SQL'e kaydeder)
@csrf_exempt
def odeme_yap_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sepet = data.get('sepet', [])
            
            if not sepet:
                return JsonResponse({'status': 'error', 'message': 'Sepet boş!'})

            with connection.cursor() as cursor:
                for bilet in sepet:
                    # SQL Bilet tablosuna kayıt atıyoruz
                    cursor.execute("""
                        INSERT INTO Bilet (SeansID, KoltukID, Fiyat, BiletTipi,KullaniciID,SatisZamani)
                        VALUES (%s, %s, %s, %s,%s, GETDATE())
                    """, [
                        bilet.get('seans_id'), 
                        bilet.get('id'),     # KoltukID
                        bilet.get('fiyat'), 
                        bilet.get('tip'),      # Tam/Öğrenci
                        bilet.get('kullanici_id')
                    ])
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error'}, status=400)


def kayit_ol_view(request):
    if request.method == "POST":
        ad = request.POST.get('first_name')
        soyad = request.POST.get('last_name')
        eposta = request.POST.get('email')
        sifre = request.POST.get('password')
        
        print(f"KAYIT DENEMESİ: {ad} {soyad} - {eposta} - Şifre: {sifre}") # Terminale yazar

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO dbo.Kullanici (Ad, Soyad, Eposta, Sifre, Rol)
                VALUES (%s, %s, %s, %s, 'Musteri')
            """, [ad, soyad, eposta, sifre])
        return redirect('login')
    return redirect('login')

def login_yap_view(request):
    print("--- Giriş Fonksiyonu Tetiklendi ---")
    if request.method == "POST":
        eposta = request.POST.get('email')
        sifre = request.POST.get('password')
        
        print(f"Gelen Bilgiler -> Email: {eposta}, Sifre: {sifre}")

        with connection.cursor() as cursor:
            # Sifre sütununun SQL'deki ismi tam olarak 'Sifre' mi kontrol et!
            cursor.execute("""
                SELECT KullaniciID, Ad FROM dbo.Kullanici 
                WHERE Eposta = %s AND Sifre = %s
            """, [eposta, sifre])
            user = cursor.fetchone()
            
            if user:
                print(f"BAŞARILI: {user[1]} giriş yaptı!")
                request.session['kullanici_id'] = user[0]
                request.session['kullanici_ad'] = user[1]
                return redirect('index') # 'index' isminin urls.py'da path('', views.index_view, name='index') olduğundan emin ol
            else:
                print("HATA: E-posta veya şifre veritabanıyla eşleşmedi!")
                return render(request, 'sinema_app/login.html', {'hata': 'E-posta veya şifre hatalı!'})
    
    print("HATA: İstek POST değil, GET olarak geldi!")
    return redirect('login')


def cikis_yap_view(request):
    # Session (oturum) bilgilerini tamamen temizler
    request.session.flush() 
    # Çıkış yapınca kullanıcıyı login'e gönderiyoruz, 
    # oraya "sepeti_sil" diye bir işaret (parametre) yollayalım.
    return redirect('/login/?action=clear_cart')
    return redirect('login')