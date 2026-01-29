from django.db import models

# Film tablosunu temsil eden model sınıfı
class Film(models.Model):
    FilmID = models.AutoField(primary_key=True, db_column='FilmID')  # Her film için benzersiz ID
    Ad = models.CharField(max_length=100, db_column='Ad')  # Filmin adı
    Tur = models.CharField(max_length=50, db_column='Tur')  # Filmin türü (Aksiyon, Komedi vb.)
    Sure = models.IntegerField(db_column='Sure')  # Filmin süresi (dakika cinsinden)
    Aciklama = models.TextField(db_column='Aciklama', null=True)  # Filmin açıklaması (opsiyonel)
    VizyonTarihi = models.DateField(db_column='VizyonTarihi')  # Filmin vizyona giriş tarihi
    posterpath = models.TextField(db_column='PosterPath', blank=True, null=True)  # Film poster yolu (SQL'deki adla aynı)
    VizyonBitisTarihi = models.DateField(db_column='VizyonBitisTarihi', null=True, blank=True)  # Vizyon bitiş tarihi

    class Meta:
        managed = False
        db_table = 'Film'  # Film tablosu

    def __str__(self):
        return self.Ad  # Admin panelde film adının görünmesi için
        

# Sinema salonu modelimiz
class Salon(models.Model):
    SalonID = models.AutoField(primary_key=True, db_column='SalonID')  # Salon ID'si
    Ad = models.CharField(max_length=50, db_column='Ad')  # Salonun adı
    Kapasite = models.IntegerField(db_column='Kapasite')  # Salonun toplam koltuk kapasitesi

    class Meta:
        managed = False
        db_table = 'Salon'

    def __str__(self):
        return self.Ad  # Admin panelde salon adı görünsün


# Her bir koltuğu temsil eden model
class Koltuk(models.Model):
    KoltukID = models.AutoField(primary_key=True, db_column='KoltukID')  # Benzersiz koltuk ID
    SalonID = models.ForeignKey(Salon, on_delete=models.DO_NOTHING, db_column='SalonID')  # Koltuğun bağlı olduğu salon
    Sira = models.CharField(max_length=2, db_column='Sira')  # Koltuğun sıra harfi (A, B, C...)
    Numara = models.IntegerField(db_column='Numara')  # Koltuğun numarası

    class Meta:
        managed = False
        db_table = 'Koltuk'


# Sisteme kayıtlı kullanıcı tablosu
class Kullanici(models.Model):
    KullaniciID = models.AutoField(primary_key=True, db_column='KullaniciID')  # Kullanıcı ID
    Ad = models.CharField(max_length=50, db_column='Ad')  # Ad
    Soyad = models.CharField(max_length=50, db_column='Soyad')  # Soyad
    Eposta = models.CharField(max_length=100, db_column='Eposta')  # E-posta adresi
    Rol = models.CharField(max_length=10, db_column='Rol')  # Kullanıcı rolü (admin / normal)
    Sifre = models.CharField(max_length=100, db_column='Sifre')  # Şifre (hash'li saklanır genelde)

    class Meta:
        managed = False
        db_table = 'Kullanici'


# Her bir film gösteriminin seans bilgileri
class Seans(models.Model):
    SeansID = models.AutoField(primary_key=True, db_column='SeansID')  # Seans ID
    FilmID = models.ForeignKey(Film, on_delete=models.DO_NOTHING, db_column='FilmID')  # Seansın ait olduğu film
    SalonID = models.ForeignKey(Salon, on_delete=models.DO_NOTHING, db_column='SalonID')  # Seansın oynatıldığı salon
    Tarih = models.DateField(db_column='Tarih')  # Seans tarihi
    Saat = models.TimeField(db_column='Saat')  # Seans saati
    Fiyat = models.DecimalField(max_digits=5, decimal_places=2, db_column='Fiyat')  # Bilet fiyatı
    Dil = models.CharField(db_column='Dil', max_length=20, default='Dublaj')  # Dublaj / Altyazı bilgisi

    class Meta:
        managed = False
        db_table = 'Seans'

    def __str__(self):
        return f"{self.FilmID.Ad} - {self.Tarih} {self.Saat}"  # Admin görünümü için


# Satılan biletleri temsil eden model
class Bilet(models.Model):
    BiletID = models.AutoField(primary_key=True, db_column='BiletID')  # Bilet ID
    SeansID = models.ForeignKey(Seans, on_delete=models.DO_NOTHING, db_column='SeansID')  # Hangi seansa ait olduğu
    KoltukID = models.ForeignKey(Koltuk, on_delete=models.DO_NOTHING, db_column='KoltukID')  # Hangi koltuk alındı
    KullaniciID = models.ForeignKey(Kullanici, on_delete=models.DO_NOTHING, db_column='KullaniciID')  # Bileti alan kullanıcı
    SatisZaani = models.DateTimeField(db_column='SatisZamani', auto_now_add=True)  # Satışın yapıldığı tarih-saat

    class Meta:
        managed = False
        db_table = 'Bilet'
