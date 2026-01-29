from django.contrib import admin, messages
from .models import Film, Salon, Seans, Koltuk, Kullanici, Bilet
from django.urls import path
from django.shortcuts import redirect
from .views import api_filmleri_veritabanina_kaydet
from django.db import connection
from datetime import timedelta
from django import forms
from django.template.response import TemplateResponse

# Basit modelleri admin paneline ekliyorum.
# Bu modeller üzerinde özel bir işlem yapmadığım için direkt register ettim.
admin.site.register(Koltuk)
admin.site.register(Kullanici)
admin.site.register(Bilet)

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    change_list_template = "admin/film_change_list.html"
    # Film listesinde görünmesini istediğim sütunlar
    list_display = ('Ad', 'Tur', 'VizyonTarihi', 'VizyonBitisTarihi')

    def get_urls(self):
        # Admin'in kendi URL'lerini alıyorum
        urls = super().get_urls()
        # API'den film çekmek için özel bir URL ekliyorum
        custom_urls = [
            path('api-aktar/', self.admin_site.admin_view(self.api_aktar_view), name='api-aktar'),
        ]
        return custom_urls + urls

    def api_aktar_view(self, request):
        # Film bilgilerini API'den alıp veritabanına kaydeden fonksiyon
        api_filmleri_veritabanina_kaydet(request)
        self.message_user(request, "API'den filmler başarıyla SSMS'e çekildi!")
        return redirect("..")

    # Film kaydedildiği anda otomatik seans üretmek için save_model metodunu override ediyorum
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Filmin vizyon başlangıç ve bitiş tarihleri girildiyse otomatik seans oluşturma başlıyor
        if obj.VizyonTarihi and obj.VizyonBitisTarihi:
            current_date = obj.VizyonTarihi  # Seans üretmeye vizyonun başladığı tarihten başlıyorum

            # Her gün için otomatik oluşturmak istediğim standart seans planı
            # Burada saatleri ve filmin dil seçeneğini manuel olarak belirledim.
            seans_planı = [
                {'saat': '10:00', 'dil': 'DUBLAJLI'},
                {'saat': '14:00', 'dil': 'DUBLAJLI'},
                {'saat': '18:00', 'dil': 'DUBLAJLI'},
                {'saat': '13:00', 'dil': 'ALTYAZILI'},
                {'saat': '17:00', 'dil': 'ALTYAZILI'},
                {'saat': '21:00', 'dil': 'ALTYAZILI'},
            ]

            eklenen = 0  # Kaç seans eklendiğini takip ediyorum

            # Vizyon bitiş tarihine kadar her gün için seans oluşturuyorum
            while current_date <= obj.VizyonBitisTarihi:
                for plan in seans_planı:
                    # Aynı salon, tarih ve saatte seans var mı diye kontrol ediyorum
                    # Burada şimdilik SalonID=1 varsayılan olarak kullanılıyor
                    exists = Seans.objects.filter(
                        SalonID_id=1, 
                        Tarih=current_date, 
                        Saat=plan['saat']
                    ).exists()

                    # Eğer aynı olan seans yoksa yeni seans oluşturuyorum
                    if not exists:
                        Seans.objects.create(
                            FilmID=obj,
                            SalonID_id=1,  # Geliştirilebilir: Dinamik salon seçimi yapılabilir
                            Tarih=current_date,
                            Saat=plan['saat'],
                            Fiyat=150.00,   # Varsayılan fiyat belirledim
                            Dil=plan['dil']
                        )
                        eklenen += 1

                # Bir sonraki güne geçiyorum
                current_date += timedelta(days=1)
            
            # Eğer seans eklendiyse kullanıcıya bilgilendirme mesajı gösteriyorum
            if eklenen > 0:
                self.message_user(request, f"{obj.Ad} için {eklenen} adet seans otomatik oluşturuldu.")

# Tarih aralığını seçmek için kullandığım özel form
class TarihAraligiForm(forms.Form):
    baslangic_tarihi = forms.DateField(label="Başlangıç Tarihi", widget=forms.SelectDateWidget)
    bitis_tarihi = forms.DateField(label="Bitiş Tarihi", widget=forms.SelectDateWidget)

@admin.register(Seans)
class SeansAdmin(admin.ModelAdmin):
    # Admin seans listesinde görmek istediğim sütunlar
    list_display = ('SeansID', 'FilmID', 'SalonID', 'Tarih', 'Saat', 'Dil', 'Fiyat')
    # Hızlı filtreleme alanları
    list_filter = ('Tarih', 'FilmID', 'SalonID')
    # Toplu işlem olarak seans kopyalama ekledim
    actions = ['toplu_seans_kopyala']

    def toplu_seans_kopyala(self, request, queryset):
        # Kullanıcı tarih seçip Apply'a bastıysa burası çalışıyor
        if 'apply' in request.POST:
            form = TarihAraligiForm(request.POST)
            if form.is_valid():
                baslangic = form.cleaned_data['baslangic_tarihi']  # Kopyalamanın başlayacağı tarih
                bitis = form.cleaned_data['bitis_tarihi']          # Biteceği tarih
                eklenen_sayisi = 0

                # Kullanıcının seçtiği örnek seansların her birini
                # belirtilen tarih aralığına çoğaltıyorum
                for seans in queryset:
                    current_date = baslangic
                    while current_date <= bitis:
                        # Aynı gün, saat ve salonda seans varsa tekrarlamamak için kontrol ediyorum
                        exists = Seans.objects.filter(
                            SalonID=seans.SalonID,
                            Tarih=current_date,
                            Saat=seans.Saat
                        ).exists()

                        if not exists:
                            # Eğer saat boşsa yeni seansı oluşturuyorum
                            Seans.objects.create(
                                FilmID=seans.FilmID,
                                SalonID=seans.SalonID,
                                Tarih=current_date,
                                Saat=seans.Saat,
                                Fiyat=seans.Fiyat,
                                Dil=seans.Dil
                            )
                            eklenen_sayisi += 1

                        # Bir sonraki güne geçiyorum
                        current_date += timedelta(days=1)
                
                self.message_user(request, f"İşlem Başarılı! Toplam {eklenen_sayisi} yeni seans oluşturuldu.")
                return None

        # İlk açılışta tarih seçim formunu gösteriyorum
        form = TarihAraligiForm()
        return TemplateResponse(request, "admin/tarih_secim_formu.html", {
            'items': queryset,
            'form': form,
            'action': 'toplu_seans_kopyala'
        })

    toplu_seans_kopyala.short_description = "Seçili Seansları Belirli Tarih Aralığına Kopyala"

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('Ad', 'Kapasite')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Eğer yeni salon oluşturuluyorsa otomatik olarak koltuk üretimi yapıyorum
        if not change:
            with connection.cursor() as cursor:
                # Salon içinde oluşturmak istediğim sıra harfleri
                siralar = ['A', 'B', 'C', 'D', 'E']
                
                # Her sıra için 1–10 arası koltuk ekliyorum
                for sira_harfi in siralar:
                    for no in range(1, 11):
                        cursor.execute("""
                            INSERT INTO Koltuk (SalonID, Sira, Numara) 
                            VALUES (%s, %s, %s)
                        """, [obj.SalonID, sira_harfi, no])
