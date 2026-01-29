# sinema_app/serializers.py

from rest_framework import serializers
from .models import Film, Seans, Kullanici, Koltuk 

# 1. Ana Model Serializer'lar (sadece veri listelemek için)
class FilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = '__all__' 

class KullaniciSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kullanici
        fields = '__all__'

# 2. Saklı Yordam ve View Çıktıları için Özel Serializerlar
# Bu T-SQL'den dönen kolon isimleriyle eşleşmelidir

# SP2: sp_AktifSeanslarGetir ve VIEW: vw_AktifSeansDetaylari için ortak
class SeansDetaySerializer(serializers.Serializer):
    SeansID = serializers.IntegerField()
    FilmAdi = serializers.CharField(max_length=255)
    SalonAdi = serializers.CharField(max_length=255)
    Tarih = serializers.DateField()
    Saat = serializers.TimeField()
    Fiyat = serializers.DecimalField(max_digits=5, decimal_places=2)
    # View'de KalanKoltukSayisi alanı da var
    KalanKoltukSayisi = serializers.IntegerField(required=False) 


# SP4: sp_KullaniciBiletleriniListele için
class KullaniciBiletSerializer(serializers.Serializer):
    BiletID = serializers.IntegerField()
    FilmAdi = serializers.CharField(max_length=255)
    SalonAdi = serializers.CharField(max_length=255)
    SeansTarihi = serializers.DateField()
    SeansSaati = serializers.TimeField()
    Koltuk = serializers.CharField(max_length=10)
    Fiyat = serializers.DecimalField(max_digits=5, decimal_places=2)
    SatisZamani = serializers.DateTimeField()